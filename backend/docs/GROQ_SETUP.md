# Groq Qwen Integration - Setup Guide

## 🚀 Quick Start

The backend now supports **Groq Qwen LLM** for intelligent key-value extraction from OCR text!

### 1. Get Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the API key

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=gsk_your_actual_api_key_here
USE_GROQ=true
```

**Important**: The `.env` file is gitignored for security. Never commit your API key!

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

---

## 📊 How It Works

### Pipeline Flow

```
Document Upload → OCR (TrOCR) → LLM Extraction (Groq Qwen) → Key-Value Pairs
```

1. **OCR Processing**: TrOCR extracts text from medical documents
2. **LLM Extraction**: Groq's Qwen model maps OCR text to key-value pairs
3 **Fallback**: If Groq fails, automatically falls back to regex-based extraction

### Output Format

**Before (Nested Structure)**:
```json
{
  "patient_id": "UHID-12345",
  "medications": [
    {"name": "Metformin", "dose": "500mg", "frequency": "BD"}
  ]
}
```

**After (Key-Value Pairs)**:
```json
{
  "Patient ID": "UHID-12345",
  "Patient Name": "John Doe",
  "Diagnosis": "Type 2 Diabetes",
  "Medication 1": "Metformin 500mg - BD (After meals)",
  "Blood Pressure": "120/80 mmHg",
  "Pulse": "72 bpm"
}
```

---

## 🔧 API Endpoints

### Health Check
```bash
GET /health
```

Returns system status including Groq availability:
```json
{
  "status": "healthy",
  "ocr_available": true,
  "groq_available": true,
  "groq_enabled": true,
  "extraction_method": "groq"
}
```

### Extract with LLM
```bash
POST /api/extract-with-template
```

Upload a document and get key-value pairs:
```json
{
  "success": true,
  "extraction_method": "groq",
  "raw_ocr": "Full OCR text...",
  "document_type": "OPD_NOTE",
  "extracted_data": {
    "Patient ID": "UHID-12345",
    "Diagnosis": "..."
  },
  "confidence_score": 0.95,
  "status": "AUTO_APPROVED"
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | **Required** Your Groq API key |
| `USE_GROQ` | `true` | Enable/disable Groq extraction |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `GROQ_TEMPERATURE` | `0.1` | Model temperature (0-1) |
| `GROQ_MAX_TOKENS` | `2000` | Max tokens in response |

### Toggle Extraction Method

To use regex extraction instead of Groq:
```bash
# In .env file
USE_GROQ=false
```

---

## 🧪 Testing

### Test with FastAPI Docs

1. Open `http://localhost:8000/docs`
2. Try the `/api/extract-with-template` endpoint
3. Upload a medical document image/PDF
4. View the extracted key-value pairs

### Test with Sample OCR Text

Use the `/api/test-llm` endpoint with sample OCR text:
```bash
curl -X POST "http://localhost:8000/api/test-llm" \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "UHID: 12345\nDiagnosis: Diabetes..."}'
```

---

## 🐛 Troubleshooting

### Groq Not Available

If you see `"groq_available": false` in health check:

1. **Check API Key**: Ensure `GROQ_API_KEY` is set in `.env`
2. **Check .env Location**: Must be in `backend/` directory
3. **Restart Server**: Stop and restart `python main.py`

### Extraction Falls Back to Regex

If `"extraction_method": "regex"` instead of `"groq"`:

1. Check Groq API key is valid
2. Check internet connection
3. View server logs for error messages
4. Verify Groq API quota/limits

---

## 📝 Notes

- **Automatic Fallback**: If Groq fails, the system automatically uses regex extraction
- **Confidence Scores**: Based on number of fields extracted
- **Document Types**: Supports OPD notes, lab reports, and prescriptions
- **Security**: `.env` files are gitignored - never commit API keys!

---

## 🎯 Next Steps

1. Add your Groq API key to `.env`
2. Test with real medical documents
3. Verify extraction accuracy
4. Adjust confidence thresholds if needed

Need help? Check the logs or contact the development team!
