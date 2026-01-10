import json
import os
import sys

# Add backend directory to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai.llm_extractor import LLMExtractor
from backend.models.models import PatientRecord

def run_simulation():
    print("\n" + "="*80)
    print("🏥 PATIENT RECORD MATCHING SIMULATION")
    print("="*80)
    
    # 1. Sample Extracted Data (from User Prompt)
    sample_data = {
        "doctor_name": "Dr. Ebin Amson",
        "diagnosis": "Type 2 Diabetes Mellitus",
        "blood_pressure": "130/90",
        "medications": [
            {
                "name": "Metformin",
                "dosage": "500mg",
                "frequency": "BD"
            }
        ],
        # Intentionally missing some fields to test "MISSING" confidence
        # "patient_name": "John Doe",  <-- Missing
        # "visit_date": "2023-11-14",  <-- Missing in extracted_data main block (though in prompt it was outside)
    }
    
    print("📄 INPUT DATA (Extracted from OCR/LLM):")
    print(json.dumps(sample_data, indent=2))
    
    # 2. Match to Template
    print("\n🔄 Matching to PatientRecord Template...")
    try:
        record = LLMExtractor.match_to_patient_record(sample_data)
        
        # 3. Print Results
        print("\n" + "-"*80)
        print("✅ MATCHED PATIENT RECORD (Console Verification)")
        print("-"*80)
        
        # Helper to print fields with status
        def print_field(label, item):
            status_icon = "[OK]" if item.confidence == "HIGH" else "[MISS]" if item.confidence == "MISSING" else "[?]"
            val = item.value if item.value else "[MISSING]"
            print(f"{status_icon} {label:<20}: {val:<30} (Confidence: {item.confidence})")
            
        print_field("Patient Name", record.patient_name)
        print_field("Diagnosis", record.diagnosis)
        print_field("Blood Pressure", record.blood_pressure)
        print_field("Visit Date", record.visit_date)
        
        print("\n[+] Medications:")
        if not record.medications:
            print("   [None]")
        else:
            for i, med in enumerate(record.medications):
                print(f"   {i+1}. {med.name} - {med.dosage or 'N/A'} - {med.frequency or 'N/A'} (Conf: {med.confidence})")
        
        print("-"*80)
        
        # 4. Highlight Actions Required
        missing_fields = []
        if record.patient_name.confidence == "MISSING": missing_fields.append("Patient Name")
        if record.diagnosis.confidence == "MISSING": missing_fields.append("Diagnosis")
        if record.visit_date.confidence == "MISSING": missing_fields.append("Visit Date")
        
        if missing_fields:
            print(f"\n[!] ACTION REQUIRED: The following fields are missing or low confidence:")
            for field in missing_fields:
                print(f"   - {field}")
            print("\n[i] Staff must verify/fill these fields manually before submission.")
        else:
            print("\n[OK] All critical fields matched with high confidence.")
            
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simulation()
