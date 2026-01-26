# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# class Patient(BaseModel):
#     id: str
#     name: str
#     age: int
#     gender: str
#     phone: str
#     abha_id: Optional[str] = None
#     uhid: str

class Patient(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    phone: str
    abha_id: Optional[str] = None
    uhid: str

    class Config:
        extra = "ignore"


# class MedicalRecord(BaseModel):
#     record_id: str                  # Changed from 'id' to match output schema
#     patient_id: str                 # UHID or patient identifier
#     document_type: str              # OPD_NOTE, LAB_REPORT, PRESCRIPTION, GENERAL
#     extracted_data: Dict[str, Any]  # Structured data extracted by LLM
#     confidence_score: float         # 0.0 to 1.0
#     status: str                     # AUTO_APPROVED, PENDING_REVIEW, REJECTED
#     processed_at: str               # ISO timestamp of processing
#     file_url: Optional[str] = None  # Optional: path to uploaded file

class MedicalRecord(BaseModel):
    record_id: str
    patient_id: str
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    status: str
    processed_at: str
    file_url: Optional[str] = None

    class Config:
        extra = "ignore"
