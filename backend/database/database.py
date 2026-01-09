# database.py
from typing import List, Optional
from models import Patient, MedicalRecord
from datetime import datetime

# 1. Fake In-Memory Storage
patients_db: List[Patient] = [
    # We pre-fill one patient so your demo always works
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

# 2. Helper Functions
def get_patient_by_id(p_id: str) -> Optional[Patient]:
    for p in patients_db:
        if p.id == p_id:
            return p
    return None

def add_record(record: MedicalRecord):
    records_db.append(record)
    return record

def get_records_for_patient(p_id: str) -> List[MedicalRecord]:
    return [r for r in records_db if r.patient_id == p_id]# database.py
from typing import List, Optional
from models import Patient, MedicalRecord
from datetime import datetime

# 1. Fake In-Memory Storage
patients_db: List[Patient] = [
    # We pre-fill one patient so your demo always works
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

# 2. Helper Functions
def get_patient_by_id(p_id: str) -> Optional[Patient]:
    for p in patients_db:
        if p.id == p_id:
            return p
    return None

def add_record(record: MedicalRecord):
    records_db.append(record)
    return record

def get_records_for_patient(p_id: str) -> List[MedicalRecord]:
    return [r for r in records_db if r.patient_id == p_id]