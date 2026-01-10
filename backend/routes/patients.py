from fastapi import APIRouter, HTTPException
from models.models import Patient
from database.database import (
    get_patient_by_uhid,
    add_patient
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/{uhid}", response_model=Patient)
def fetch_patient_by_uhid(uhid: str):
    patient = get_patient_by_uhid(uhid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/", response_model=Patient)
def create_patient(patient: Patient):
    existing = get_patient_by_uhid(patient.uhid)
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")
    return add_patient(patient)
