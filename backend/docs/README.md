# MedScan AI - Backend API Documentation

This directory contains the core logic and API documentation for the MedScan AI backend.

## 🚀 API Architecture

The backend is built with **FastAPI** and supports both synchronous and asynchronous document processing flows.

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the Web UI |
| `/api/process-document` | POST | Synchronous: Upload → OCR → LLM → DB |
| `/api/extract-with-template` | POST | Synchronous: Upload → OCR → LLM (No DB) |
| `/upload` | POST | Asynchronous: Queue document for batch processing |
| `/status/{job_id}` | GET | Check async job status |
| `/result/{job_id}` | GET | Fetch results for a completed job |
| `/api/batch-upload` | POST | Batch: Upload 2 documents for parallel processing |

## 🧠 Medical Extraction Pipeline

MedScan AI uses a multiple-stage pipeline to ensure high accuracy medical data extraction.

1. **OCR Stage**: Scanned images/PDFs are processed by `LayoutLMv3Engine`, which uses Tesseract with spatial awareness.
2. **LLM Stage**: Extracted text and spatial data are passed to the `LLMExtractor`, which uses Groq's Qwen model to map data to a standardized patient template.
3. **Validation Stage**: Data is scored for confidence based on the completeness of the extraction.

## 📁 Internal Structure

- `main.py`: The entry point for the FastAPI server.
- `worker.py`: The background worker process for Redis Queue (RQ).
- `ai/`: Contains AI services (LayoutLMv3, Groq, LLM logic).
- `models/`: Pydantic models for request/response validation.
- `database/`: Persistence layer (SQLite).

## 🛠️ Usage Examples

### Synchronous Extraction
```bash
curl -X POST "http://localhost:8000/api/extract-with-template" \
  -F "file=@presription.png"
```

### Batch Extraction (Asynchronous)
```bash
curl -X POST "http://localhost:8000/api/batch-upload" \
  -F "files=@page1.png" \
  -F "files=@page2.png"
```

## 📊 Confidence Scoring

MedScan AI categorizes records based on extraction confidence:
- **AUTO_APPROVED (≥ 0.90)**: Ready for immediate indexing.
- **PENDING_REVIEW (0.70 - 0.89)**: Requires human verification.
- **REJECTED (< 0.70)**: Extraction quality too low or mandatory fields missing.

---
Part of the MedScan AI Open Source Project.
