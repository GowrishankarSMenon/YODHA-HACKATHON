# models.py
from pydantic import BaseModel, Field
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
    record_id: str                  # Changed from 'id' to match output schema
    patient_id: str                 # UHID or patient identifier
    document_type: str              # OPD_NOTE, LAB_REPORT, PRESCRIPTION, GENERAL
    extracted_data: Dict[str, Any]  # Structured data extracted by LLM
    confidence_score: float         # 0.0 to 1.0
    status: str                     # AUTO_APPROVED, PENDING_REVIEW, REJECTED
    processed_at: str               # ISO timestamp of processing
    file_url: Optional[str] = None  # Optional: path to uploaded file

class PatientRecordItem(BaseModel):
    value: Optional[str] = None
    confidence: str = "HIGH" # HIGH, LOW, MISSING
    source: str = "EXTRACTED" # EXTRACTED, MANUAL, INFERRED

class MedicationItem(BaseModel):
    name: str = Field(..., description="Name of the medication")
    dosage: Optional[str] = Field(None, description="Dosage amount e.g. 500mg")
    frequency: Optional[str] = Field(None, description="Frequency e.g. BD, OD")
    confidence: str = "HIGH"

class PatientRecord(BaseModel):
    """
    Standardized Patient Record Template - Comprehensive Medical Record.
    All fields use PatientRecordItem for confidence tracking.
    """
    # Patient Information
    patient_id: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    patient_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    surname: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    age: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    gender: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    date_of_birth: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    phone: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    mobile: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    email: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    address: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    occupation: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Hospital/Facility Info
    hospital_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    hospital_address: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Insurance/Subscriber Details
    insurance_id: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    insurance_type: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    group_number: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    subscriber_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    medicare_no: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    medicare_ref: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    health_fund: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    health_fund_no: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    vet_affairs: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Visit/Doctor Details
    visit_date: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    procedure: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    doctor_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    gp_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    referrer: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    chief_complaint: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Vitals
    blood_pressure: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    pulse: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    temperature: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    weight: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    spo2: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Clinical Details
    diagnosis: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    comments: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    test_name: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    test_date: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    next_visit_date: PatientRecordItem = Field(default_factory=lambda: PatientRecordItem(value=None, confidence="MISSING"))
    
    # Medications
    medications: List[MedicationItem] = []
    
    # Metadata for the matching process
    original_record_id: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    status: str = "DRAFT" # DRAFT, VERIFIED, SUBMITTED
