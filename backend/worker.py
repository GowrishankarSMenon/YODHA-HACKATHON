from rq import Worker, SimpleWorker
from redis_queue_module.redis_queue import ocr_queue, redis_conn

# Import from ai package
from ai.layoutlmv3_engine import LayoutLMv3Engine
from ai.llm_extractor import LLMExtractor
from pdf2image import convert_from_path
from PIL import Image
import os


def process_document(job_id: str, file_path: str):
    """
    Legacy worker function - performs basic OCR only.
    Kept for backwards compatibility.
    """
    print(f"[WORKER] Processing job {job_id} (basic OCR)")
    print(f"[WORKER] File path: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file
    if file_path.lower().endswith(".pdf"):
        print("[WORKER] Converting PDF to image...")
        pages = convert_from_path(file_path)
        image = pages[0]  # first page only
    else:
        print("[WORKER] Loading image...")
        image = Image.open(file_path).convert("RGB")

    #  Layout-Aware OCR
    print("[WORKER] Running Layout-Aware OCR...")
    words, _ = LayoutLMv3Engine.ocr_with_boxes(image)
    full_text = " ".join(words)
    lines = [full_text] # simplified for legacy function

    print(f"[RESULT] Job {job_id} - Extracted {len(words)} words")
    # Legacy metadata placeholder
    metadata = {'avg_confidence': 0.95, 'total_lines': 1}

    return {
        "job_id": job_id,
        "lines": lines,
        "full_text": full_text,
        "metadata": metadata,
        "status": "completed"
    }


def process_document_with_llm(job_id: str, file_path: str):
    """
    Enhanced worker function that performs OCR + LLM extraction.
    This matches the functionality in main.py's synchronous endpoints.
    
    Returns structured data with:
    - Raw OCR text
    - LLM-extracted structured data
    - Document type
    - Confidence score
    - Processing status
    """
    print(f"[WORKER-LLM] Processing job {job_id} with OCR + LLM extraction")
    print(f"[WORKER-LLM] File path: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Step 1: Read file and convert to image
    if file_path.lower().endswith(".pdf"):
        print("[WORKER-LLM] Converting PDF to image...")
        pages = convert_from_path(file_path)
        image = pages[0]  # Process first page only
    else:
        print("[WORKER-LLM] Loading image...")
        image = Image.open(file_path).convert("RGB")

    # Step 2: Perform OCR (Layout-Aware)
    print("[WORKER-LLM] Running Layout-Aware OCR...")
    # We pass the image directly to LLMExtractor which now handles spatial anchoring
    extracted_data = LLMExtractor.extract_structured_data("", "AUTO", image=image)
    
    # Extract raw text from anchored data if possible (LLMExtractor refactoring took care of this internally)
    # But for the sake of the worker result structure:
    words, _ = LayoutLMv3Engine.ocr_with_boxes(image)
    ocr_text = " ".join(words)
    
    print(f"[WORKER-LLM] OCR extracted {len(words)} words")
    ocr_metadata = {'avg_confidence': 0.95, 'total_words': len(words)}

    # Step 3: LLM Extraction and merge is already handled above in Layout-Aware pipeline
    # We just need to ensure metadata is correct
    detected_type = LLMExtractor._detect_document_type(ocr_text)
    
    print(f"[WORKER-LLM] Detected document type: {detected_type}")
    print(f"[WORKER-LLM] Extracted {len(extracted_data)} fields")

    # Step 4: Calculate confidence
    print("[WORKER-LLM] Calculating confidence score...")
    confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
    status_value = LLMExtractor.determine_status(confidence_score)
    
    print(f"[WORKER-LLM] Confidence score: {confidence_score:.2f}")
    print(f"[WORKER-LLM] Status: {status_value}")

    # Step 5: Map to Template
    print("[WORKER-LLM] Mapping to Template...")
    patient_record_obj = LLMExtractor.match_to_patient_record(extracted_data)
    patient_record = patient_record_obj.dict()

    # Step 6: Build complete result
    from ai.llm_extractor import GROQ_AVAILABLE, USE_GROQ
    extraction_method = "groq" if (USE_GROQ and GROQ_AVAILABLE) else "layout-only"
    
    from datetime import datetime
    result = {
        "job_id": job_id,
        "success": True,
        "extraction_method": extraction_method,
        "raw_ocr": ocr_text,
        "document_type": detected_type,
        "extracted_data": extracted_data,
        "confidence_score": confidence_score,
        "status": status_value,
        "ocr_metadata": ocr_metadata,
        "processed_at": datetime.now().isoformat() + "Z",
        "patient_record": patient_record
    }
    
    print(f"[WORKER-LLM] ✅ Job {job_id} completed successfully!")
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("[WORKER] Starting RQ worker with LLM extraction support...")
    print(f"[WORKER] Listening to queue: {ocr_queue.name}")
    print("=" * 70)
    
    # Use SimpleWorker for Windows compatibility (no fork)
    from rq import SimpleWorker
    
    worker = SimpleWorker(
        queues=[ocr_queue],
        connection=redis_conn
    )
    
    print("[WORKER] Worker is ready and waiting for jobs...")
    print("[WORKER] Using SimpleWorker (Windows compatible)")
    print("[WORKER] Available functions:")
    print("  - process_document (legacy, OCR only)")
    print("  - process_document_with_llm (new, OCR + LLM)")
    print("=" * 70)
    
    worker.work()
