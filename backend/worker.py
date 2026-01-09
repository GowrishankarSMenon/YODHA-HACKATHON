from rq import Worker
from redis_queue import ocr_queue, redis_conn

from ai.ai_engine import ocr_page
from pdf2image import convert_from_path
from PIL import Image
import os


def process_document(job_id: str, file_path: str):
    print(f"[WORKER] Processing job {job_id}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    # Read file
    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path)
        image = pages[0]  # first page only
    else:
        image = Image.open(file_path).convert("RGB")

    # OCR
    lines = ocr_page(image)

    print(f"[RESULT] Job {job_id}")
    for line in lines:
        print(line)

    return {
        "job_id": job_id,
        "lines": lines
    }


if __name__ == "__main__":
    worker = Worker(
        queues=[ocr_queue],
        connection=redis_conn
    )
    worker.work()
