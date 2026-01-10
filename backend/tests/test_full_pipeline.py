import sys
import os
import json
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.getcwd())

from ai.llm_extractor import LLMExtractor
from models.models import PatientRecord

def test_extraction_mapping():
    print("Testing LLM Extraction and Mapping...")
    
    # 1. Sample OCR Text (OPD Note style)
    sample_ocr = """
    CITY HOSPITAL & RESEARCH CENTER
    123 Health Ave, Metro City
    
    PATIENT REGISTRATION FORM
    UHID: AB-12345-XY
    Patient Name: John Quincy Adams
    DOB: 15-May-1980  Age: 45  Gender: M
    Address: 456 Oak Street, Suburbia, State 5678
    Phone: 0412-345-678
    Email: john.adams@example.com
    
    Appointment: 2026-01-15 10:30 AM
    Procedure: Routine Health Checkup
    GP: Dr. Sarah Smith
    Referrer: Self
    
    Insurance: HealthCare Plus
    Policy No: HCP-99887766
    Medicare: 1234 56789 0  Ref: 1
    
    VITALS:
    BP: 120/80 mmHg
    Pulse: 72 bpm
    Temp: 98.6 F
    Weight: 75 kg
    
    Comments: Patient complains of mild back pain for 2 weeks.
    Diagnosis: Acute Lumbar Strain
    """
    
    print("\n--- Running Extraction ---")
    try:
        # Extract data using the improved LLMExtractor (which uses Groq mapping)
        extracted_data = LLMExtractor.extract_structured_data(sample_ocr, "OPD_NOTE")
        print("Raw Extracted Data Type:", type(extracted_data))
        print("Keys present in extracted data:", list(extracted_data.keys()))
        
        # 2. Match to PatientRecord
        print("\n--- Mapping to PatientRecord Template ---")
        patient_record_obj = LLMExtractor.match_to_patient_record(extracted_data)
        record_dict = patient_record_obj.dict()
        
        # 3. Validate key fields
        checks = {
            "Patient ID": record_dict["patient_id"]["value"] == "AB-12345-XY",
            "Patient Name": "John" in (record_dict["patient_name"]["value"] or ""),
            "Medicare No": record_dict["medicare_no"]["value"] is not None,
            "BP": record_dict["blood_pressure"]["value"] == "120/80 mmHg",
            "Diagnosis": "Lumbar" in (record_dict["diagnosis"]["value"] or "")
        }
        
        print("\n--- Validation Results ---")
        all_passed = True
        for name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{name}: {status} (Value: {record_dict.get(name.lower().replace(' ', '_'), {}).get('value')})")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🌟 ALL TESTS PASSED! Pipeline is mapping correctly.")
        else:
            print("\n⚠️ Some tests failed. Check extraction/mapping logic.")
            
        # Print a few mapped fields for visual check
        print("\nSample Mapped Fields:")
        print(f"Hospital: {record_dict['hospital_name']['value']}")
        print(f"Medicare: {record_dict['medicare_no']['value']} (Conf: {record_dict['medicare_no']['confidence']})")
        print(f"Insurance: {record_dict['health_fund']['value']}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY not set in environment.")
    else:
        test_extraction_mapping()
