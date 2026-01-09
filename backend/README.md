# MedScan AI - LLM-Based Extraction Backend

## Overview
LLM-powered medical document extraction pipeline that converts OCR text into structured JSON.

**Workflow:** `DOCUMENT → OCR → LLM → DATABASE → FETCH`

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
cd backend
python main.py
```

Server starts at: `http://localhost:8000`

### 3. API Documentation
Interactive docs: `http://localhost:8000/docs`

## API Endpoints

### Process Document
**POST** `/api/process-document`

Upload PDF/image → OCR → LLM extraction → Structured JSON

**Example Response:**
```json
{
  "record_id": "rec_98765",
  "patient_id": "HOSP-2025-001",
  "document_type": "OPD_NOTE",
  "extracted_data": {
    "diagnosis": "Type 2 Diabetes Mellitus",
    "blood_pressure": "130/90",
    "medications": [
      {"name": "Metformin", "dose": "500mg", "frequency": "BD"}
    ]
  },
  "confidence_score": 0.92,
  "status": "AUTO_APPROVED",
  "processed_at": "2026-01-09T10:32:40Z"
}
```

### Get All Records
**GET** `/api/records`

Returns all processed medical records.

### Get Single Record
**GET** `/api/records/{record_id}`

Fetch specific record by ID.

### Test LLM Extraction
**POST** `/api/test-llm`

Test LLM extraction with raw OCR text (no file upload).

## Document Types Supported

- **OPD_NOTE** - Out-patient department notes
- **LAB_REPORT** - Laboratory test results
- **PRESCRIPTION** - Medicine prescriptions
- **GENERAL** - Generic documents

## Auto-Approval Logic

| Confidence Score | Status |
|-----------------|--------|
| ≥ 0.90 | AUTO_APPROVED |
| 0.70 - 0.89 | PENDING_REVIEW |
| < 0.70 | REJECTED |

## Project Structure

```
backend/
├── main.py                 # FastAPI app with LLM pipeline
├── ai/
│   ├── llm_extractor.py   # LLM extraction service
│   ├── ai_engine.py       # Existing mock AI (for reference)
│   ├── sample_opd_ocr.txt # Sample OPD OCR output
│   └── sample_lab_ocr.txt # Sample lab report OCR
├── models/
│   └── models.py          # Pydantic schemas
├── database/
│   └── database.py        # In-memory storage
└── requirements.txt
```

## Testing

### Using Swagger UI
1. Go to `http://localhost:8000/docs`
2. Try **POST /api/process-document**
3. Upload a test file (or use fallback with sample OCR text)
4. Check extracted JSON

### Using cURL
```bash
# Process a document
curl -X POST "http://localhost:8000/api/process-document" \
  -F "file=@sample_opd.pdf"

# Get all records
curl "http://localhost:8000/api/records"

# Get specific record
curl "http://localhost:8000/api/records/rec_12345"
```

## Key Features

✅ Auto-detection of document type  
✅ Intelligent field extraction (diagnosis, medications, vitals, etc.)  
✅ Confidence scoring with auto-approval  
✅ Support for nested data (medications array)  
✅ Fallback OCR simulation for testing  
✅ RESTful API design  

## Notes for Hackathon

- **OCR Integration**: Your teammate implements OCR in `ai_engine.py` / `ai_worker.py`
- **LLM Simulation**: Currently using regex/pattern matching (fast for hackathon)
- **Production**: Replace with real LLM API (OpenAI, Gemini) by updating `llm_extractor.py`
- **Database**: In-memory storage for demo (easily switch to MongoDB later)

## Next Steps

1. ✅ Basic LLM extraction working
2. 🔄 Integrate real OCR from teammate
3. 🔄 Add queue management for bulk processing
4. 🔄 Frontend integration
5. 🔄 Deploy to cloud
