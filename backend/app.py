from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil

from redis_queue import ocr_queue, redis_conn
from rq.job import Job

# Import the actual function from worker module
from worker import process_document

# ====================================================
# CREATE APP
# ====================================================
app = FastAPI(title="OCR Queue API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================
# STATIC FILES
# ====================================================
# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

if os.path.exists("static/index.html"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    def home():
        return FileResponse("static/index.html")
else:
    @app.get("/", response_class=HTMLResponse)
    def home():
        return """
        <h3>OCR Queue API is running</h3>
        <p>Visit /docs for API documentation</p>
        <p>⚠️ No static/index.html found. Create it to see the UI.</p>
        """

# ====================================================
# UPLOAD ENDPOINT
# ====================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document and queue it for OCR processing
    """
    job_id = str(uuid.uuid4())

    # Save file
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"[API] File saved: {file_path}")
    print(f"[API] Queueing job {job_id}...")

    # Enqueue job - pass the function directly, not as string
    job = ocr_queue.enqueue(
        process_document,  # Function object, not string!
        job_id=job_id,
        file_path=file_path,
        job_timeout='10m'  # 10 minute timeout
    )

    print(f"[API] Job queued with ID: {job.id}")

    return {
        "job_id": job.id,  # RQ job ID
        "custom_job_id": job_id,  # Your custom ID
        "status": "QUEUED",
        "filename": file.filename
    }


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the status of a job
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        response = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
        
        # If finished, include result
        if job.is_finished:
            response["result"] = job.result
        
        # If failed, include error
        if job.is_failed:
            response["error"] = str(job.exc_info)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@app.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """
    Get the result of a completed job
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if not job.is_finished:
            raise HTTPException(status_code=400, detail=f"Job not finished. Status: {job.get_status()}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "result": job.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found or failed: {str(e)}")


@app.get("/queue/stats")
async def get_queue_stats():
    """
    Get queue statistics
    """
    return {
        "queue_name": ocr_queue.name,
        "queued_jobs": len(ocr_queue),
        "started_jobs": ocr_queue.started_job_registry.count,
        "finished_jobs": ocr_queue.finished_job_registry.count,
        "failed_jobs": ocr_queue.failed_job_registry.count,
    }


@app.delete("/cleanup")
async def cleanup_old_jobs():
    """
    Clean up old completed jobs (optional maintenance endpoint)
    """
    from rq.registry import FinishedJobRegistry, FailedJobRegistry
    
    finished_registry = FinishedJobRegistry(queue=ocr_queue)
    failed_registry = FailedJobRegistry(queue=ocr_queue)
    
    # Clean up jobs older than 1 hour
    finished_count = finished_registry.count
    failed_count = failed_registry.count
    
    for job_id in finished_registry.get_job_ids():
        job = Job.fetch(job_id, connection=redis_conn)
        job.delete()
    
    for job_id in failed_registry.get_job_ids():
        job = Job.fetch(job_id, connection=redis_conn)
        job.delete()
    
    return {
        "cleaned_finished": finished_count,
        "cleaned_failed": failed_count
    }


# ====================================================
# NEW ENDPOINT: SYNCHRONOUS OCR PROCESSING
# ====================================================
@app.post("/api/extract-with-template")
async def extract_with_template(file: UploadFile = File(...)):
    """
    Synchronous OCR processing endpoint (processes immediately, no queue)
    This is what the UI expects!
    """
    import uuid
    from PIL import Image
    from pdf2image import convert_from_path
    from ai.ai_engine import ocr_page_improved
    
    # Generate unique ID
    job_id = str(uuid.uuid4())
    
    # Save file temporarily
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"[API] Processing file: {file_path}")
        
        # Read file
        if file_path.lower().endswith(".pdf"):
            print("[API] Converting PDF to image...")
            pages = convert_from_path(file_path)
            image = pages[0]  # first page only
        else:
            print("[API] Loading image...")
            image = Image.open(file_path).convert("RGB")
        
        # Run OCR
        print("[API] Running OCR...")
        result = ocr_page_improved(image)
        
        # Extract data
        lines = result['lines']
        full_text = result['full_text']
        metadata = result['metadata']
        
        print(f"[API] OCR complete - {len(lines)} lines extracted")
        
        # Determine document type (basic classification)
        doc_type = "UNKNOWN"
        text_lower = full_text.lower()
        if "prescription" in text_lower or "rx" in text_lower:
            doc_type = "PRESCRIPTION"
        elif "lab" in text_lower or "test" in text_lower or "result" in text_lower:
            doc_type = "LAB_REPORT"
        elif "discharge" in text_lower or "admission" in text_lower:
            doc_type = "DISCHARGE_SUMMARY"
        
        # Create structured data (basic extraction)
        structured_data = {
            "patient_name": "N/A",
            "date": "N/A",
            "doctor_name": "N/A",
            "extracted_text": full_text[:500] + "..." if len(full_text) > 500 else full_text
        }
        
        # Determine status based on confidence
        avg_confidence = metadata['avg_confidence']
        if avg_confidence > 0.8:
            status = "AUTO_APPROVED"
        elif avg_confidence > 0.5:
            status = "PENDING_REVIEW"
        else:
            status = "LOW_CONFIDENCE"
        
        return {
            "job_id": job_id,
            "raw_ocr": full_text,
            "structured_data": structured_data,
            "document_type": doc_type,
            "confidence_score": avg_confidence,
            "status": status,
            "metadata": metadata
        }
        
    except Exception as e:
        print(f"[API] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    finally:
        # Optional: Clean up the uploaded file after processing
        # os.remove(file_path)
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)