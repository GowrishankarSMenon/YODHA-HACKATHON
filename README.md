# MedScan AI - Medical Document OCR & LLM Extraction

## 🎯 Project Overview

**MedScan AI** is a zero-downtime hospital digitization system that uses OCR (TrOCR) and LLM (Groq AI) to automatically extract structured data from scanned medical documents.

### Key Features
- ✅ **OCR Extraction**: Microsoft TrOCR model for handwritten medical document processing
- ✅ **LLM Structuring**: Groq Qwen model for intelligent key-value extraction
- ✅ **Async Processing**: Redis queue for scalable background processing
- ✅ **Sync Processing**: Immediate processing for low-latency use cases
- ✅ **Web Interface**: Browser-based document upload and visualization
- ✅ **Database Storage**: SQLite database for record persistence
- ✅ **Document Types**: OPD Notes, Lab Reports, Prescriptions

---

## 📁 Project Structure

```
d:\jyothi/
├── backend/                          # Python FastAPI backend
│   ├── main.py                       # Main API server (sync + async endpoints)
│   ├── worker.py                     # Redis queue worker (OCR + LLM processing)
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── ai/                          # AI & ML modules
│   │   ├── ai_engine.py             # TrOCR OCR implementation
│   │   ├── llm_extractor.py         # LLM extraction logic
│   │   ├── groq_service.py          # Groq API client
│   │   ├── sample_opd_ocr.txt       # Sample OCR data
│   │   └── sample_lab_ocr.txt       # Sample OCR data
│   │
│   ├── models/                      # Data models
│   │   └── models.py                # MedicalRecord model
│   │
│   ├── database/                    # Database layer
│   │   └── database.py              # SQLite CRUD operations
│   │
│   ├── redis_queue_module/          # Redis queue files
│   │   ├── redis_queue.py           # Redis connection & queue config
│   │   ├── worker.py                # (Old location - moved to root)
│   │   ├── app.py                   # Standalone queue API (reference)
│   │   ├── cleanup_redis.py         # Redis cleanup utility
│   │   ├── queue_endpoints.py       # Endpoint code reference
│   │   └── README.md                # Queue documentation
│   │
│   ├── static/                      # Web UI
│   │   └── index.html               # Single-page app for document upload
│   │
│   ├── uploads/                     # Uploaded document storage
│   ├── docs/                        # Documentation files
│   └── tests/                       # Test files
│
├── medscan-frontend/                # React frontend (alternative UI)
│   └── src/pages/DoctorDashboard/  # Doctor dashboard components
│
├── test-images/                     # Test medical documents
│   └── opd1.png                     # Sample OPD note image
│
└── .env                             # Environment variables (GROQ_API_KEY)
```

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.13)
- **OCR**: Microsoft TrOCR (transformers, torch)
- **LLM**: Groq API (Qwen 2.5 model)
- **Queue**: Redis + RQ (Redis Queue)
- **Database**: SQLite (in-memory for hackathon)
- **PDF Processing**: pdf2image, poppler
- **Image Processing**: Pillow (PIL)

### Frontend
- **Web UI**: Vanilla HTML/CSS/JavaScript
- **React UI**: Vite + React + TailwindCSS

### Infrastructure
- **Redis**: Cloud Redis (redis-10817.crce217.ap-south-1-1.ec2.cloud.redislabs.com)
- **Python Version**: 3.13
- **OS**: Windows

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python 3.13
# Install Redis (or use cloud Redis)
# Install Poppler for PDF processing
```

### Installation
```bash
cd d:\jyothi\backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with Groq API key
echo GROQ_API_KEY=your_api_key_here > .env
```

### Running the Application

**Option 1: Synchronous Processing Only**
```bash
python main.py
# Visit: http://localhost:8000
```

**Option 2: With Async Queue (Redis)**
```bash
# Terminal 1: Start worker
python worker.py

# Terminal 2: Start server
python main.py
```

---

## 📊 API Endpoints

### Synchronous Processing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/health` | GET | Health check + system status |
| `/api/process-document` | POST | Upload + OCR + LLM + Save to DB |
| `/api/extract-with-template` | POST | Upload + OCR + LLM (no DB) |
| `/api/records` | GET | List all records |
| `/api/records/{id}` | GET | Get specific record |
| `/api/test-llm` | POST | Test LLM extraction |

### Asynchronous Processing (Queue)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Queue document for async processing |
| `/status/{job_id}` | GET | Check job status |
| `/result/{job_id}` | GET | Get completed job results |
| `/queue/stats` | GET | Queue statistics |
| `/cleanup` | DELETE | Clean up old jobs |

---

## 🔄 Data Flow Architecture

### Synchronous Flow
```
User → Browser → FastAPI → OCR (TrOCR) → LLM (Groq) → Database → Response
```

### Asynchronous Flow
```
User → Browser → FastAPI → Redis Queue
                              ↓ (immediate response)
                         Worker Process
                              ↓
                    OCR (TrOCR) → LLM (Groq)
                              ↓
                         Store in Redis
                              ↓
                    User polls /status or /result
```

---

## 💾 Data Models

### MedicalRecord
```python
{
    "record_id": "rec_abc123",           # Unique ID
    "patient_id": "HOSP-2025-001",       # UHID from extraction
    "document_type": "OPD_NOTE",         # OPD_NOTE | LAB_REPORT | PRESCRIPTION
    "extracted_data": {                  # LLM-extracted key-value pairs
        "Patient ID": "HOSP-2025-001",
        "Diagnosis": "Type 2 Diabetes",
        "Blood Pressure": "130/90 mmHg",
        "Medication 1": "Metformin 500mg - BD",
        ...
    },
    "confidence_score": 0.79,            # 0.0 - 1.0
    "status": "PENDING_REVIEW",          # AUTO_APPROVED | PENDING_REVIEW | REJECTED
    "processed_at": "2026-01-09T20:30:00Z",
    "file_url": "/uploads/filename.png"
}
```

---

## 🧠 AI/ML Components

### 1. OCR Engine (`ai/ai_engine.py`)
- **Model**: microsoft/trocr-base-handwritten
- **Function**: `ocr_page_improved(image) -> dict`
- **Output**:
  ```python
  {
      'lines': ["Line 1", "Line 2", ...],
      'full_text': "Complete text...",
      'metadata': {
          'avg_confidence': 0.92,
          'total_lines': 15
      }
  }
  ```

### 2. LLM Extractor (`ai/llm_extractor.py`)
- **Primary**: Groq API with Qwen model
- **Fallback**: Regex-based extraction
- **Function**: `LLMExtractor.extract_structured_data(ocr_text, doc_type)`
- **Output**: Dictionary of key-value pairs

### 3. Groq Service (`ai/groq_service.py`)
- **Model**: llama-3.3-70b-versatile
- **Temperature**: 0.1 (deterministic)
- **Max Tokens**: 2000
- **Response Format**: JSON only

---

## 🔍 Key Files Explained

### `main.py` (19,846 bytes)
- Main FastAPI application
- Defines all API endpoints
- Integrates OCR + LLM extraction
- Handles both sync and async processing
- Imports Redis queue for async endpoints

### `worker.py` (5,107 bytes)
- Redis queue worker process
- Contains `process_document_with_llm()` function
- Performs OCR → LLM → Result storage
- Runs as separate background process

### `ai/llm_extractor.py` (15,036 bytes)
- LLM extraction logic
- Groq API integration
- Regex fallback extraction
- Confidence scoring
- Status determination

### `ai/ai_engine.py` (9,847 bytes)
- TrOCR model loading
- OCR processing
- Image preprocessing
- Confidence calculation

### `redis_queue_module/redis_queue.py` (608 bytes)
- Redis connection configuration
- RQ queue initialization
- Connection details for cloud Redis

### `static/index.html` (15,424 bytes)
- Web-based document upload interface
- OCR output display
- Structured data visualization
-  Real-time processing feedback

---

## 🔐 Environment Variables

Required in `.env`:
```bash
GROQ_API_KEY=gsk_...                    # Groq API key
USE_GROQ=true                            # Enable Groq extraction
GROQ_MODEL=llama-3.3-70b-versatile       # Model name
GROQ_TEMPERATURE=0.1                     # Temperature
GROQ_MAX_TOKENS=2000                     # Max tokens
```

---

## 📈 Processing Pipeline Details

### Step 1: Document Upload
```python
# User uploads opd1.png via /upload or /api/extract-with-template
file_content = await file.read()
# File saved to uploads/job_id.png
```

### Step 2: OCR Extraction
```python
# Convert to image
image = Image.open(BytesIO(file_content)).convert("RGB")

# Run TrOCR
ocr_result = ocr_page_improved(image)
# Result: {"lines": [...], "full_text": "...", "metadata": {...}}
```

###  Step 3: LLM Extraction
```python
# Send to Groq API
extracted_data = LLMExtractor.extract_structured_data(ocr_text, "AUTO")

# Groq processes text and returns:
# {"Patient ID": "HOSP-2025-001", "Diagnosis": "...", ...}
```

### Step 4: Post-Processing
```python
# Detect document type
detected_type = LLMExtractor._detect_document_type(ocr_text)
# Returns: OPD_NOTE, LAB_REPORT, or PRESCRIPTION

# Calculate confidence
confidence_score = LLMExtractor.calculate_confidence(extracted_data, detected_type)
# Returns: 0.0 - 1.0

# Determine status
status = LLMExtractor.determine_status(confidence_score)
# Returns: AUTO_APPROVED (>0.9), PENDING_REVIEW (>0.7), or REJECTED (<0.7)
```

### Step 5: Storage/Response
- **Sync**: Return JSON response immediately
- **Async**: Store in Redis, user polls for results

---

## 🏗️ Redis Queue Architecture

### Queue Configuration
- **Host**: redis-10817.crce217.ap-south-1-1.ec2.cloud.redislabs.com
- **Port**: 10817
- **Queue Name**: ocr_queue
- **Worker**: RQ SimpleWorker (Windows compatible)

### Job Lifecycle
1. **QUEUED**: Job added to Redis queue
2. **STARTED**: Worker picks up job
3. **FINISHED**: Processing complete, result stored
4. **FAILED**: Error occurred during processing

---

## 🧪 Testing

### Test Documents
Located in `test-images/`:
- `opd1.png` - OPD consultation note

### Sample Test Commands
```powershell
# Upload document
$response = Invoke-WebRequest -Uri "http://localhost:8000/upload" -Method POST -Form @{file=Get-Item "..\test-images\opd1.png"}

# Check status
$jobId = ($response.Content | ConvertFrom-Json).job_id
Invoke-WebRequest -Uri "http://localhost:8000/status/$jobId"

# Get results
Invoke-WebRequest -Uri "http://localhost:8000/result/$jobId"
```

---

## 🐛 Common Issues

**Issue**: Redis queue import error
**Solution**: Folder renamed to `redis_queue_module` to avoid Python's built-in `queue` module

**Issue**: TrOCR memory crashes
**Solution**: Auto-reload disabled in uvicorn, lazy loading of OCR model

**Issue**: Groq API errors
**Solution**: Check `.env` file for valid `GROQ_API_KEY`

---

## 📚 Dependencies

Main packages (from requirements.txt):
```
fastapi
uvicorn
python-multipart
pillow
pdf2image
transformers
torch
sentencepiece
protobuf
redis
rq
groq
python-dotenv
```

---

## 👥 Project Team
- YODHA HACKATHON Team
- MedScan AI - Zero-Downtime Hospital Digitization

---

## 📄 License
Hackathon Project

---

## 🔗 Related Documentation
- **User Flow Guide**: See `COMPLETE_USER_FLOW.md`
- **Demo Script**: See `REDIS_DEMO_FLOW.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **Implementation Plan**: See `implementation_plan.md`
