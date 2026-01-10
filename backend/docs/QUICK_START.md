# 🚀 Groq Qwen Integration - Quick Reference

## ⚡ Quick Start (3 Steps)

### 1. Get API Key
Visit: https://console.groq.com/keys → Create API Key

### 2. Configure
```bash
# In the backend directory, create .env file:
GROQ_API_KEY=gsk_your_key_here
USE_GROQ=true
```

### 3. Test
```bash
python test_groq.py
```

---

## 📁 Files Changed

| File | Status | Description |
|------|--------|-------------|
| `ai/groq_service.py` | ✨ NEW | Groq API service module |
| `ai/llm_extractor.py` | 🔧 MODIFIED | Added Groq extraction + fallback |
| `main.py` | 🔧 MODIFIED | Updated endpoints for key-value output |
| `requirements.txt` | 🔧 MODIFIED | Added groq, python-dotenv |
| `.env.example` | ✨ NEW | Configuration template |
| `test_groq.py` | ✨ NEW | Test suite |
| `GROQ_SETUP.md` | ✨ NEW | Detailed setup guide |

---

## 🔌 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```
Returns: Groq availability status

### Extract Key-Value Pairs
```bash
POST http://localhost:8000/api/extract-with-template
Content-Type: multipart/form-data
Body: file=<your_document.pdf>
```

Response:
```json
{
  "extraction_method": "groq",  // or "regex"
  "raw_ocr": "OCR text...",
  "extracted_data": {
    "Patient ID": "...",
    "Diagnosis": "...",
    ...
  }
}
```

---

## 🎯 Key Features

✅ **AI-Powered Extraction** - Uses Groq Qwen model for intelligent key-value extraction  
✅ **Automatic Fallback** - Falls back to regex if Groq unavailable  
✅ **Key-Value Format** - Flat structure instead of nested templates  
✅ **Configurable** - Toggle between Groq and regex via environment variable  
✅ **Secure** - API keys in .env (gitignored)  
✅ **Tested** - Comprehensive test suite included  

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `groq_available: false` | Check GROQ_API_KEY in .env file |
| `extraction_method: "regex"` | Groq failed, check API key validity |
| Import errors | Run `pip install groq python-dotenv` |
| `.env` not loaded | Restart the server (python main.py) |

---

## 📚 Documentation

- **Setup Guide**: `GROQ_SETUP.md`
- **Test Script**: Run `python test_groq.py`
- **Example Config**: `.env.example`

---

## 🎓 Next Steps

1. ✍️ Add your Groq API key to `.env`
2. 🧪 Run `python test_groq.py` to verify
3. 📤 Upload documents via `/api/extract-with-template`
4. ✅ Verify key-value extraction accuracy

**Need help?** Check `GROQ_SETUP.md` for detailed instructions!
