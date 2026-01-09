from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import shutil

from redis_queue import ocr_queue

# ====================================================
# CREATE APP FIRST (THIS WAS MISSING)
# ====================================================
app = FastAPI(title="OCR Queue API")

# ====================================================
# STATIC FILES (OPTIONAL UI)
# ====================================================
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    def home():
        return FileResponse("static/index.html")
else:
    @app.get("/", response_class=HTMLResponse)
    def home():
        return "<h3>OCR Queue API is running</h3><p>Visit /docs</p>"

# ====================================================
# UPLOAD ENDPOINT
# ====================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ocr_queue.enqueue(
        "worker.process_document",
        job_id=job_id,
        file_path=file_path
    )

    return {
        "job_id": job_id,
        "status": "QUEUED"
    }
