from rq import Worker, SimpleWorker
from redis_queue import ocr_queue, redis_conn

# Import from ai package (ai_engine.py is in ai/ folder)
# Keep the original import path that was working
from ai.ai_engine import ocr_page_improved
from pdf2image import convert_from_path
from PIL import Image
import os


def process_document(job_id: str, file_path: str):
    """
    Worker function that processes documents.
    This function will be called by RQ workers.
    """
    print(f"[WORKER] Processing job {job_id}")
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

    # OCR with improved function
    print("[WORKER] Running OCR...")
    result = ocr_page_improved(image)
    
    lines = result['lines']
    full_text = result['full_text']
    metadata = result['metadata']

    print(f"[RESULT] Job {job_id} - Extracted {len(lines)} lines")
    print(f"[RESULT] Confidence: {metadata['avg_confidence']:.2f}")
    
    for i, line in enumerate(lines, 1):
        print(f"  Line {i}: {line}")

    return {
        "job_id": job_id,
        "lines": lines,
        "full_text": full_text,
        "metadata": metadata,
        "status": "completed"
    }


if __name__ == "__main__":
    print("[WORKER] Starting RQ worker...")
    print(f"[WORKER] Listening to queue: {ocr_queue.name}")
    
    # Use SimpleWorker for Windows compatibility (no fork)
    from rq import SimpleWorker
    
    worker = SimpleWorker(
        queues=[ocr_queue],
        connection=redis_conn
    )
    
    print("[WORKER] Worker is ready and waiting for jobs...")
    print("[WORKER] Using SimpleWorker (Windows compatible)")
    worker.work()