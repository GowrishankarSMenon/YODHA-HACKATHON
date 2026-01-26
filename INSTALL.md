# Installation Guide - MedScan AI

This guide will help you set up MedScan AI on your local machine or server.

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+**
- **Git**
- **Redis Server** (Local or Cloud)
- **Tesseract OCR** (Required for the fallback OCR engine)
- **Poppler** (Required for PDF to image conversion)

### 1. Tesseract OCR Installation
- **Windows**: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

### 2. Poppler Installation
- **Windows**: Download from [poppler-windows](http://blog.alivate.com.au/poppler-windows/) and add the `bin` folder to your PATH.
- **Linux**: `sudo apt install poppler-utils`
- **macOS**: `brew install poppler`

---

## 💻 Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/GowrishankarSMenon/YODHA-HACKATHON.git
cd YODHA-HACKATHON/backend
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend/` directory:
```bash
GROQ_API_KEY=your_groq_api_key
REDIS_HOST=localhost
REDIS_PORT=6379
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Update for your OS
```

---

## 🏃 Running the Application

MedScan AI can run in two modes:

### Mode 1: Synchronous (FastAPI Only)
Best for testing and lightweight extraction.
```bash
python main.py
```
Visit `http://localhost:8000` in your browser.

### Mode 2: Asynchronous (With Redis Queue)
Recommended for production and batch Processing.
1. **Start Redis**: Ensure your Redis server is running.
2. **Start the Worker**:
   ```bash
   python worker.py
   ```
3. **Start the Server**:
   ```bash
   python main.py
   ```

---

## 🐳 Docker Deployment (Coming Soon)
We are working on a Docker Compose setup to simplify deployment. Stay tuned!

## 🛠️ Troubleshooting
- **Tesseract not found**: Ensure `TESSERACT_PATH` in `.env` points to the correct executable.
- **Redis Connection Error**: Check your Redis host and port in `.env`.
- **Poppler Error**: Ensure the Poppler `bin` folder is in your system PATH.
