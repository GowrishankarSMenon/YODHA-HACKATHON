# ai_engine.py
import random
from typing import Dict, Any

def extract_data_from_file(filename: str) -> Dict[str, Any]:
    """
    Simulates AI extraction.
    If the file is 'blood_test.pdf', it returns perfect lab results.
    Otherwise, it returns generic data.
    """
    
    # DEMO HACK: If we upload our specific demo file
    if "blood" in filename.lower():
        return {
            "patient_name": "Rahul Kumar", # Matches our DB patient
            "doc_type": "Lab Report",
            "diagnosis": "Typhoid Fever",
            "confidence": 0.98,
            "data": {
                "test": "Widal Test",
                "result": "Positive",
                "wbc_count": "12,000"
            }
        }
    
    # Fallback for random files
    return {
        "patient_name": "Unknown",
        "doc_type": "General Record",
        "diagnosis": "Pending",
        "confidence": 0.50,
        "data": {"note": "Scanned document"}
    }