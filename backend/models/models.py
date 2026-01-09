# models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Patient(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    phone: str
    abha_id: Optional[str] = None
    uhid: str

class MedicalRecord(BaseModel):
    id: str
    patient_id: str
    doc_type: str              # e.g., "Lab Report"
    file_url: str
    upload_date: datetime
    status: str                # "processing", "verified"
    confidence_score: float    # 0.0 to 1.0
    extracted_data: Dict[str, Any]  # The AI results go here