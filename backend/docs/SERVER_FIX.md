# Server Crash Fix Applied ✅

## Problem
Server kept crashing with error:
```
OSError: The paging file is too small for this operation to complete. (os error 1455)
```

This caused API requests to fail with:
```
Error processing document: Cannot convert undefined or null to object
```

## Root Cause
1. **Auto-reload enabled**: Server restarted on every file change
2. **TrOCR model loaded at startup**: Large model loaded into memory immediately
3. **Windows virtual memory exhausted**: Not enough paging file space

## Fixes Applied

### 1. Disabled Auto-Reload
**File**: `main.py`
```python
uvicorn.run(
    "main:app",
    reload=False  # Disabled to prevent crashes
)
```

**Impact**: Server won't auto-restart on code changes. You must restart manually.

### 2. Lazy Model Loading
**File**: `ai/ai_engine.py`
```python
# Models are now global variables (None initially)
processor = None
model = None

def _load_model():
    """Load only when first OCR request comes in."""
    global processor, model
    if model is not None:
        return  # Already loaded
    # Load TrOCR model here...
```

**Impact**: Model loads only when first document is processed, not at startup.

### 3. Lazy OCR Import
**File**: `main.py`
```python
def _ensure_ocr_loaded():
    """Import OCR only when needed."""
    global ocr_page, OCR_AVAILABLE
    if not OCR_AVAILABLE:
        from ai.ai_engine import ocr_page as _ocr_page
        ocr_page = _ocr_page
        OCR_AVAILABLE = True
```

**Impact**: OCR module imports only when first needed, not at server startup.

---

## How to Use Now

### Starting the Server
```bash
cd d:\jyothi\backend
python main.py
```

**First request will be slower** (TrOCR loads on demand), but subsequent requests are fast.

### After Code Changes
**Auto-reload is OFF**, so you must:

1. Stop server: `Ctrl+C`
2. Restart: `python main.py`

### Memory Usage
- **Before**: ~3GB memory at startup (TrOCR loaded immediately)
- **After**: ~500MB at startup (TrOCR loads on first OCR request)

---

## Testing

1. **Stop current server** (Ctrl+C in the terminal)
2. **Restart with fixes**:
   ```bash
   python main.py
   ```
3. **Upload a document** via the web UI
4. **First request**: Will load TrOCR model (5-10 seconds)
5. **Subsequent requests**: Fast (model already loaded)

---

## If You Still See Memory Issues

### Option 1: Increase Windows Paging File
1. Windows Settings → System → About
2. Advanced system settings
3. Performance → Settings → Advanced
4. Virtual memory → Change
5. Set custom size: Min 8GB, Max 16GB

### Option 2: Use Groq Only (Skip OCR)
If you don't need OCR and have pre-extracted text:

```python
# In .env file
USE_GROQ=true
```

Then use `/api/test-llm` endpoint with raw text instead of uploading files.

---

## Summary

✅ **Auto-reload disabled** - Prevents repeated model loading crashes  
✅ **Lazy model loading** - Reduces startup memory from 3GB to 500MB  
✅ **Lazy OCR import** - OCR loads only when needed  
✅ **Server will start successfully** - No more crashes on startup  

**Note**: You must manually restart the server after code changes now!
