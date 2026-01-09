"""
MedScan AI Backend - LLM-Based Extraction Pipeline
Main FastAPI application for processing medical documents.

Workflow: DOCUMENT → OCR → LLM → DATABASE → FETCH
"""
import uvicorn
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes
import os
import shutil

# Redis Queue imports for async processing
try:
    from redis_queue_module.redis_queue import ocr_queue, redis_conn
    from rq.job import Job
    from rq.registry import FinishedJobRegistry, FailedJobRegistry
    QUEUE_AVAILABLE = True
    print("✅ Redis queue available for async processing")
except ImportError as e:
    QUEUE_AVAILABLE = False
    print(f"⚠️  Redis queue not available: {e}")
    print("   Async processing endpoints will not be available")

# Import OCR function (lazy loading to avoid TrOCR memory issues)
OCR_AVAILABLE = False
ocr_page = None

def _ensure_ocr_loaded():
    """Lazy load OCR engine only when needed."""
    global OCR_AVAILABLE, ocr_page
    if not OCR_AVAILABLE:
        try:
            from ai.ai_engine import ocr_page as _ocr_page
            ocr_page = _ocr_page
            OCR_AVAILABLE = True
            print("✅ OCR engine loaded successfully!")
        except ImportError as e:
            print(f"⚠️  OCR engine not available: {e}")

# Import LLM extractor
from ai.llm_extractor import LLMExtractor

# Import models and database
from models.models import MedicalRecord
from database.database import (
    add_record,
    get_record_by_id,
    get_all_records,
    get_patient_by_uhid,
    records_db
)

# ================================================================
# UPLOAD DIRECTORY SETUP
# ================================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ================================================================
# FASTAPI APPLICATION
# ================================================================

app = FastAPI(
    title="MedScan AI - LLM Extraction Pipeline",
    version="2.0.0",
    description="Zero-Downtime Hospital Digitization with LLM-powered extraction"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# STATIC FILES  
# ================================================================

# Mount static directory for the web interface
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def perform_ocr(file_content: bytes, filename: str) -> str:
    """
    Perform OCR on uploaded file using teammate's TrOCR implementation.
    """
    _ensure_ocr_loaded()  # Lazy load OCR engine
    
    if OCR_AVAILABLE:
        # Use actual OCR from ai_worker.ocr_page()
        try:
            if filename.lower().endswith(".pdf"):
                pages = convert_from_bytes(file_content)
                lines = ocr_page(pages[0])  # First page only for demo
            else:
                img = Image.open(BytesIO(file_content)).convert("RGB")
                lines = ocr_page(img)
            
            return "\n".join(lines)
        except Exception as e:
            print(f"OCR error: {e}")
            # Fallback to sample OCR if actual OCR fails
            return load_sample_ocr(filename)
    else:
        # Fallback: Load sample OCR text for demo
        return load_sample_ocr(filename)

def load_sample_ocr(filename: str) -> str:
    """Load sample OCR text as fallback."""
    try:
        if "opd" in filename.lower():
            with open("ai/sample_opd_ocr.txt", "r") as f:
                return f.read()
        elif "lab" in filename.lower():
            with open("ai/sample_lab_ocr.txt", "r") as f:
                return f.read()
        else:
            return "Sample OCR text for demo purposes."
    except:
        return "Fallback OCR text - no sample file found."

# ================================================================
# API ENDPOINTS
# ================================================================

@app.get("/")
def root():
    """API root endpoint - serves the web interface."""
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    # Check Groq availability
    from ai.llm_extractor import GROQ_AVAILABLE, USE_GROQ
    
    return {
        "status": "healthy",
        "service": "MedScan AI LLM Pipeline",
        "ocr_available": OCR_AVAILABLE,
        "groq_available": GROQ_AVAILABLE,
        "groq_enabled": USE_GROQ,
        "extraction_method": "groq" if USE_GROQ else "regex",
        "total_records": len(records_db)
    }

@app.post("/api/process-document", response_model=Dict[str, Any])
async def process_document(file: UploadFile = File(...)):
    """
    Main processing endpoint: Upload → OCR → LLM → Database
    
    Workflow:
    1. Receive PDF/image upload
    2. Extract text using OCR
    3. Pass OCR text to LLM for structured extraction
    4. Calculate confidence score
    5. Determine auto-approval status
    6. Save to database
    7. Return structured JSON
    """
    try:
        # Step 1: Read file
        file_content = await file.read()
        
        # Step 2: Perform OCR
        ocr_text = perform_ocr(file_content, file.filename)
        
        # Step 3: LLM extraction
        document_type = "AUTO"  # Auto-detect document type
        extracted_data = LLMExtractor.extract_structured_data(ocr_text, document_type)
        
        # Auto-detect document type
        detected_type = LLMExtractor._detect_document_type(ocr_text)
        
        # Step 4: Calculate confidence
        confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
        
        # Step 5: Determine status
        status_value = LLMExtractor.determine_status(confidence_score)
        
        # Step 6: Generate record ID
        record_id = f"rec_{uuid.uuid4().hex[:8]}"
        
        # Step 7: Get patient_id from extracted data (UHID)
        patient_id = extracted_data.get("patient_id", "UNKNOWN")
        
        # Step 8: Create medical record
        record = MedicalRecord(
            record_id=record_id,
            patient_id=patient_id,
            document_type=detected_type,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            status=status_value,
            processed_at=datetime.now().isoformat() + "Z",
            file_url=f"/uploads/{file.filename}"
        )
        
        # Step 9: Save to database
        add_record(record)
        
        # Step 10: Return response matching target schema
        return {
            "record_id": record.record_id,
            "patient_id": record.patient_id,
            "document_type": record.document_type,
            "extracted_data": record.extracted_data,
            "confidence_score": record.confidence_score,
            "status": record.status,
            "processed_at": record.processed_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )

@app.post("/api/extract-with-template")
async def extract_with_template(file: UploadFile = File(...)):
    """
    Extract key-value pairs from medical documents using OCR + LLM.
    
    This endpoint:
    1. Performs OCR on uploaded document
    2. Uses Groq Qwen LLM to extract key-value pairs (or fallback to regex)
    3. Returns both raw OCR text and extracted key-value pairs
    
    Returns:
        - raw_ocr: Plain text from OCR
        - extracted_data: Key-value pairs from LLM extraction
        - extraction_method: "groq" or "regex" (which method was used)
    """
    try:
        print("\n" + "*"*80)
        print("🌐 API ENDPOINT - /api/extract-with-template called")
        print("*"*80)
        
        # Step 1: Read file
        print(f"\n📥 Step 1: Reading file '{file.filename}'...")
        file_content = await file.read()
        print(f"✅ File read - Size: {len(file_content)} bytes")
        
        # Step 2: Perform OCR
        print(f"\n🔍 Step 2: Performing OCR...")
        ocr_text = perform_ocr(file_content, file.filename)
        print(f"✅ OCR completed - Text length: {len(ocr_text)} characters")
        print(f"📝 OCR text preview (first 200 chars): {ocr_text[:200]}...")
        
        # Step 3: LLM extraction with Groq (or fallback to regex)
        print(f"\n🤖 Step 3: Extracting structured data with LLM...")
        extracted_data = LLMExtractor.extract_structured_data(ocr_text, "AUTO")
        print(f"\n✅ LLM extraction completed")
        print(f"   Type: {type(extracted_data)}")
        print(f"   Is None: {extracted_data is None}")
        if extracted_data:
            print(f"   Keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Not a dict'}")
            print(f"   Number of fields: {len(extracted_data) if isinstance(extracted_data, dict) else 0}")
        
        detected_type = LLMExtractor._detect_document_type(ocr_text)
        print(f"✅ Document type detected: {detected_type}")
        
        # Step 4: Calculate confidence
        print(f"\n📊 Step 4: Calculating confidence score...")
        confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
        print(f"✅ Confidence score: {confidence_score}")
        
        status_value = LLMExtractor.determine_status(confidence_score)
        print(f"✅ Status: {status_value}")
        
        # Determine which extraction method was used
        from ai.llm_extractor import GROQ_AVAILABLE, USE_GROQ
        extraction_method = "groq" if (USE_GROQ and GROQ_AVAILABLE) else "regex"
        print(f"\n🔬 Extraction method: {extraction_method}")
        
        # Return key-value pairs format
        response_data = {
            "success": True,
            "extraction_method": extraction_method,
            "raw_ocr": ocr_text,
            "document_type": detected_type,
            "extracted_data": extracted_data,  # Now contains key-value pairs if using Groq
            "confidence_score": confidence_score,
            "status": status_value,
            "processed_at": datetime.now().isoformat() + "Z"
        }
        
        print(f"\n📤 Step 5: Preparing response...")
        print(f"   Response keys: {list(response_data.keys())}")
        print(f"   Response extracted_data type: {type(response_data['extracted_data'])}")
        print(f"   Response extracted_data is None: {response_data['extracted_data'] is None}")
        print("*"*80)
        print("✅ API REQUEST COMPLETED SUCCESSFULLY")
        print("*"*80 + "\n")
        
        return response_data
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR in /api/extract-with-template")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        print(f"❌ Traceback:")
        traceback.print_exc()
        print("*"*80 + "\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )

@app.get("/api/records", response_model=List[Dict[str, Any]])
def list_records():
    """Get all processed medical records."""
    records = get_all_records()
    
    return [
        {
            "record_id": r.record_id,
            "patient_id": r.patient_id,
            "document_type": r.document_type,
            "extracted_data": r.extracted_data,
            "confidence_score": r.confidence_score,
            "status": r.status,
            "processed_at": r.processed_at
        }
        for r in records
    ]

@app.get("/api/records/{record_id}", response_model=Dict[str, Any])
def get_record(record_id: str):
    """Get a specific medical record by ID."""
    record = get_record_by_id(record_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record {record_id} not found"
        )
    
    return {
        "record_id": record.record_id,
        "patient_id": record.patient_id,
        "document_type": record.document_type,
        "extracted_data": record.extracted_data,
        "confidence_score": record.confidence_score,
        "status": record.status,
        "processed_at": record.processed_at
    }

@app.post("/api/test-llm")
async def test_llm_extraction(ocr_text: str):
    """
    Test endpoint for LLM extraction without file upload.
    Useful for testing with sample OCR text.
    """
    try:
        # Extract structured data
        document_type = "AUTO"
        extracted_data = LLMExtractor.extract_structured_data(ocr_text, document_type)
        detected_type = LLMExtractor._detect_document_type(ocr_text)
        
        # Calculate confidence
        confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
        status_value = LLMExtractor.determine_status(confidence_score)
        
        return {
            "document_type": detected_type,
            "extracted_data": extracted_data,
            "confidence_score": confidence_score,
            "status": status_value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )
# ================================================================
# REDIS QUEUE ENDPOINTS (Async Processing)
# Add these endpoints to main.py after the /api/test-llm endpoint
# ================================================================

@app.post("/upload")
async def upload_document_async(file: UploadFile = File(...)):
    """
    Upload a document and queue it for async OCR + LLM processing.
    Returns a job_id that can be used to check status and get results.
    """
    if not QUEUE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Queue service not available. Use /api/extract-with-template instead."
        )
    
    job_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"[QUEUE] File saved: {file_path}")
    print(f"[QUEUE] Queueing job {job_id}...")
    
    # Import worker function
    from redis_queue_module.worker import process_document_with_llm
    
    # Enqueue job
    job = ocr_queue.enqueue(
        process_document_with_llm,
        job_id=job_id,
        file_path=file_path,
        job_timeout='10m'
    )
    
    print(f"[QUEUE] Job queued with ID: {job.id}")
    
    return {
        "job_id": job.id,
        "custom_job_id": job_id,
        "status": "QUEUED",
        "filename": file.filename
    }


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of an async processing job."""
    if not QUEUE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Queue not available")
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        response = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
        
        if job.is_finished:
            response["result"] = job.result
        if job.is_failed:
            response["error"] = str(job.exc_info)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@app.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """Get the result of a completed async processing job."""
    if not QUEUE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Queue not available")
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if not job.is_finished:
            raise HTTPException(status_code=400, detail=f"Job not finished. Status: {job.get_status()}")
        
        return {
            "job_id": job_id,
            "status": "completed",
           "result": job.result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@app.get("/queue/stats")
async def get_queue_stats():
    """Get Redis queue statistics."""
    if not QUEUE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Queue not available")
    
    return {
        "queue_name": ocr_queue.name,
        "queued_jobs": len(ocr_queue),
        "started_jobs": ocr_queue.started_job_registry.count,
        "finished_jobs": ocr_queue.finished_job_registry.count,
        "failed_jobs": ocr_queue.failed_job_registry.count,
    }


@app.delete("/cleanup")
async def cleanup_old_jobs():
    """Clean up old completed and failed jobs from Redis."""
    if not QUEUE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Queue not available")
    
    finished_registry = FinishedJobRegistry(queue=ocr_queue)
    failed_registry = FailedJobRegistry(queue=ocr_queue)
    
    finished_count = finished_registry.count
    failed_count = failed_registry.count
    
    for job_id in finished_registry.get_job_ids():
        try:
            Job.fetch(job_id, connection=redis_conn).delete()
        except:
            pass
    
    for job_id in failed_registry.get_job_ids():
        try:
            Job.fetch(job_id, connection=redis_conn).delete()
        except:
            pass
    
    return {
        "cleaned_finished": finished_count,
        "cleaned_failed": failed_count
    }

# ================================================================
# RUN SERVER
# ================================================================

if _name_ == "_main_":
    print("🚀 Starting MedScan AI - LLM Extraction Pipeline")
    print("📚 API Docs: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    print("🔬 Process Document: POST http://localhost:8000/api/process-document")
    print("\n⚠️  Auto-reload DISABLED to prevent TrOCR memory issues")
    print("   (Restart server manually after code changes)\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Disabled to prevent TrOCR memory crashes
    )