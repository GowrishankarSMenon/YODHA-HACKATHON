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
    from worker import process_document_with_llm
    
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
