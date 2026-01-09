"""Quick test for confidence calculation fix"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.llm_extractor import LLMExtractor

# Sample Groq-style extraction (22 fields - should be high confidence)
groq_data = {
    "Patient Name": "Priya Sharma",
    "UHID": "HOSP-2025-002",
    "Age": "32 years",
    "Gender": "Female",
    "Referring Doctor": "Dr. Mehta",
    "Report Date": "07-Jan-2026",
    "Sample Collection Date": "06-Jan-2026",
    "Sample Collection Time": "08:30 AM",
    "Lab Number": "LAB/2026/00234",
    "Lab Technician": "Ramesh K.",
    "Pathologist": "Dr. Gupta MD",
    "Hemoglobin": "11.2 g/dL",
    "WBC Count": "8,500 cells/cumm",
    "RBC Count": "4.2 million/cumm",
    "Platelet Count": "2.5 lakh/cumm",
    "ESR": "28 mm/hr",
    "Neutrophils": "62%",
    "Lymphocytes": "30%",
    "Monocytes": "6%",
    "Eosinophils": "2%",
    "Diagnosis": "Mild anemia",
    "Recommendation": "Iron supplementation"
}

# Sample regex-style extraction (should use old method)
regex_data = {
    "patient_id": "TEST-001",
    "diagnosis": "Test",
    "medications": [{"name": "Med1", "dose": "500mg"}]
}

print("Testing Confidence Calculation Fix")
print("=" * 60)

# Test Groq format
confidence_groq = LLMExtractor.calculate_confidence(groq_data, "LAB_REPORT")
status_groq = LLMExtractor.determine_status(confidence_groq)
print(f"\n✅ Groq Format (22 fields):")
print(f"   Confidence: {confidence_groq:.2f}")
print(f"   Status: {status_groq}")

# Test regex format
confidence_regex = LLMExtractor.calculate_confidence(regex_data, "OPD_NOTE")
status_regex = LLMExtractor.determine_status(confidence_regex)
print(f"\n✅ Regex Format (3 fields):")
print(f"   Confidence: {confidence_regex:.2f}")
print(f"   Status: {status_regex}")

print("\n" + "=" * 60)
if confidence_groq >= 0.90:
    print("🎉 SUCCESS! Groq confidence is now correctly calculated!")
    print(f"   Previous: 0.50 (REJECTED) → New: {confidence_groq:.2f} ({status_groq})")
else:
    print("⚠️  Confidence still low, please check the calculation logic")
