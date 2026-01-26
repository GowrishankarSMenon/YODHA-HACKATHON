# Installation Guide

This guide covers the complete setup for the MedScan AI Backend on Windows, Linux, and macOS.

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
- **Git** installed ([Download](https://git-scm.com/downloads))

---

## 🛠️ Section 1: System Dependencies

### 1. Tesseract OCR (Required)

MedScan AI uses Tesseract for layout analysis.

**Windows**:
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer.
3. **IMPORTANT**: Add the installation path (e.g., `C:\Program Files\Tesseract-OCR`) to your System PATH environment variable.

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev
```

**macOS**:
```bash
brew install tesseract
```

### 2. Poppler (Required for PDF processing)

**Windows**:
1. Download the latest binary from [Poppler Releases](https://github.com/oschwartz10612/poppler-windows/releases/).
2. Extract the zip file.
3. Add the `bin` folder (e.g., `C:\path\to\poppler\bin`) to your System PATH.

**Linux**:
```bash
sudo apt-get install poppler-utils
```

**macOS**:
```bash
brew install poppler
```

### 3. Redis (Optional - for Async Queue)

**Windows**:
- Install via WSL (Windows Subsystem for Linux) OR
- Download the Windows port (Memurai or similar) OR
- Use Docker: `docker run -d -p 6379:6379 redis`

**Linux/macOS**:
```bash
# Linux
sudo apt-get install redis-server

# macOS
brew install redis
```

---

## 🐍 Section 2: Python Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GowrishankarSMenon/YODHA-HACKATHON.git
   cd YODHA-HACKATHON/backend
   ```

2. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Section 3: Configuration details

1. **Create .env File**:
   Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. **Add API Keys**:
   Open `.env` in a text editor and fill in your keys:

   ```env
   # Groq API (Get from console.groq.com)
   GROQ_API_KEY=gsk_...
   
   # Gemini API (Get from aistudio.google.com)
   GEMINI_API_KEY=AIza...
   ```

---

## 🚀 Section 4: Running the Application

### 1. Start the API Server
```bash
python main.py
```
Validates that:
- Database connects
- OCR engine loads (Tesseract)
- Server starts at `http://localhost:8000`

### 2. Start the Worker (If using Redis Mode)
Open a new terminal, activate venv, and run:
```bash
python worker.py
```

---

## 🧪 Verification

To verify your installation:

1. Go to `http://localhost:8000/docs`
2. Used the `/health` endpoint
3. It should return:
   ```json
   {
     "status": "healthy",
     "ocr_available": true,
     "groq_available": true
   }
   ```

If `ocr_available` is false, check your Tesseract installation path.

---

[⬅️ Back to Backend README](../README.md)
