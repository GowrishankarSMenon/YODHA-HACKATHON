# database.py
from typing import List, Optional
from models.models import Patient, MedicalRecord

# ================================================================
# IN-MEMORY STORAGE
# ================================================================

patients_db: List[Patient] = [
    # Pre-filled demo patient
    Patient(
        id="pat_001",
        name="Rahul Kumar",
        age=45,
        gender="Male",
        phone="9876543210",
        abha_id="91-2233-4455-66",
        uhid="HOSP-2025-001"
    )
]

records_db: List[MedicalRecord] = []

# ================================================================
# PATIENT OPERATIONS
# ================================================================

def get_patient_by_id(p_id: str) -> Optional[Patient]:
    """Get patient by ID."""
    for p in patients_db:
        if p.id == p_id:
            return p
    return None

def get_patient_by_uhid(uhid: str) -> Optional[Patient]:
    """Get patient by UHID."""
    for p in patients_db:
        if p.uhid == uhid:
            return p
    return None

def add_patient(patient: Patient) -> Patient:
    """Add new patient."""
    patients_db.append(patient)
    return patient

# ================================================================
# MEDICAL RECORD OPERATIONS
# ================================================================

def add_record(record: MedicalRecord) -> MedicalRecord:
    """Add new medical record."""
    records_db.append(record)
    return record

def get_records_for_patient(p_id: str) -> List[MedicalRecord]:
    """Get all records for a patient."""
    return [r for r in records_db if r.patient_id == p_id]

def get_record_by_id(rec_id: str) -> Optional[MedicalRecord]:
    """Get record by ID."""
    for r in records_db:
        if r.record_id == rec_id:
            return r
    return None

def get_all_records() -> List[MedicalRecord]:
    """Get all medical records."""
    return records_db
