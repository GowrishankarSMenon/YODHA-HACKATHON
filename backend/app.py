import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes

from ai_worker import ocr_page

# ================================================================
# FASTAPI SETUP
# ================================================================
app = FastAPI(title="TrOCR OCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")

# ================================================================
# OCR API
# ================================================================
@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    content = await file.read()

    if file.filename.lower().endswith(".pdf"):
        pages = convert_from_bytes(content)
        lines = ocr_page(pages[0])  # first page only
    else:
        img = Image.open(BytesIO(content)).convert("RGB")
        lines = ocr_page(img)

    return {
        "text": "\n".join(lines),
        "lines": lines
    }

# ================================================================
# RUN SERVER
# ================================================================
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
