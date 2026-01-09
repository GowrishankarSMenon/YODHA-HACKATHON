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

# Import OCR function from teammate's implementation
try:
    from ai.ai_engine import ocr_page
    OCR_AVAILABLE = True
    print("✅ OCR engine loaded successfully!")
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"⚠️  OCR engine not available: {e}. Using fallback simulation.")

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
    return {
        "status": "healthy",
        "service": "MedScan AI LLM Pipeline",
        "ocr_available": OCR_AVAILABLE,
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
    NEW: Extract with dual output - Raw OCR + Structured Template.
    This is the main endpoint for the web interface.
    
    Returns both:
    - raw_ocr: The plain text from OCR
    - structured_data: The LLM-extracted key-value pairs
    """
    try:
        # Step 1: Read file
        file_content = await file.read()
        
        # Step 2: Perform OCR
        ocr_text = perform_ocr(file_content, file.filename)
        
        # Step 3: LLM extraction
        extracted_data = LLMExtractor.extract_structured_data(ocr_text, "AUTO")
        detected_type = LLMExtractor._detect_document_type(ocr_text)
        
        # Step 4: Calculate confidence
        confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
        status_value = LLMExtractor.determine_status(confidence_score)
        
        # Return dual output
        return {
            "success": True,
            "raw_ocr": ocr_text,
            "document_type": detected_type,
            "structured_data": extracted_data,
            "confidence_score": confidence_score,
            "status": status_value,
            "processed_at": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
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
# RUN SERVER
# ================================================================

if __name__ == "__main__":
    print("🚀 Starting MedScan AI - LLM Extraction Pipeline")
    print("📚 API Docs: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    print("🔬 Process Document: POST http://localhost:8000/api/process-document")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
