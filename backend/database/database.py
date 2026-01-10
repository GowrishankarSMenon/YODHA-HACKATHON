# # database.py
# from typing import List, Optional
# from models.models import Patient, MedicalRecord

# # ================================================================
# # IN-MEMORY STORAGE
# # ================================================================

# patients_db: List[Patient] = [
#     # Pre-filled demo patient
#     Patient(
#         id="pat_001",
#         name="Rahul Kumar",
#         age=45,
#         gender="Male",
#         phone="9876543210",
#         abha_id="91-2233-4455-66",
#         uhid="HOSP-2025-001"
#     )
# ]

# records_db: List[MedicalRecord] = []

# # ================================================================
# # PATIENT OPERATIONS
# # ================================================================

# def get_patient_by_id(p_id: str) -> Optional[Patient]:
#     """Get patient by ID."""
#     for p in patients_db:
#         if p.id == p_id:
#             return p
#     return None

# def get_patient_by_uhid(uhid: str) -> Optional[Patient]:
#     """Get patient by UHID."""
#     for p in patients_db:
#         if p.uhid == uhid:
#             return p
#     return None

# def add_patient(patient: Patient) -> Patient:
#     """Add new patient."""
#     patients_db.append(patient)
#     return patient

# # ================================================================
# # MEDICAL RECORD OPERATIONS
# # ================================================================

# def add_record(record: MedicalRecord) -> MedicalRecord:
#     """Add new medical record."""
#     records_db.append(record)
#     return record

# def get_records_for_patient(p_id: str) -> List[MedicalRecord]:
#     """Get all records for a patient."""
#     return [r for r in records_db if r.patient_id == p_id]

# def get_record_by_id(rec_id: str) -> Optional[MedicalRecord]:
#     """Get record by ID."""
#     for r in records_db:
#         if r.record_id == rec_id:
#             return r
#     return None

# def get_all_records() -> List[MedicalRecord]:
#     """Get all medical records."""
#     return records_db
 

from typing import List, Optional
from pymongo import MongoClient
from models.models import Patient, MedicalRecord

# ================================================================
# MONGODB CONNECTION
# ================================================================

MONGO_URI = "mongodb://localhost:27017/"  # replace with Atlas URI later
DB_NAME = "medscan_emr"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

patients_collection = db["patients"]
records_collection = db["documents"]  # medical records / OCR docs


# ================================================================
# PATIENT OPERATIONS
# ================================================================

def get_patient_by_id(p_id: str) -> Optional[Patient]:
    """Get patient by internal ID."""
    data = patients_collection.find_one({"id": p_id})
    if not data:
        return None

    data.pop("_id", None)  # remove MongoDB ObjectId
    return Patient(**data)


def get_patient_by_uhid(uhid: str) -> Optional[Patient]:
    """Get patient by UHID."""
    data = patients_collection.find_one({"uhid": uhid})
    if not data:
        return None

    data.pop("_id", None)
    return Patient(**data)


def add_patient(patient: Patient) -> Patient:
    """Add new patient to MongoDB."""
    patients_collection.insert_one(patient.model_dump())
    return patient


# ================================================================
# MEDICAL RECORD OPERATIONS
# ================================================================

def add_record(record: MedicalRecord) -> MedicalRecord:
    """Add new medical record (OCR output)."""
    records_collection.insert_one(record.model_dump())
    return record


def get_records_for_patient(p_id: str) -> List[MedicalRecord]:
    """Get all records for a patient."""
    cursor = records_collection.find({"patient_id": p_id})
    records = []

    for doc in cursor:
        doc.pop("_id", None)
        records.append(MedicalRecord(**doc))

    return records


def get_record_by_id(rec_id: str) -> Optional[MedicalRecord]:
    """Get record by record ID."""
    data = records_collection.find_one({"record_id": rec_id})
    if not data:
        return None

    data.pop("_id", None)
    return MedicalRecord(**data)


def get_all_records() -> List[MedicalRecord]:
    """Get all medical records."""
    cursor = records_collection.find()
    records = []

    for doc in cursor:
        doc.pop("_id", None)
        records.append(MedicalRecord(**doc))

    return records
