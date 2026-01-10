"""
LLM-based extraction service for medical documents.
Converts OCR extracted text into structured JSON format.
Supports both regex-based and Groq LLM-based extraction.
"""
import re
import os
import json
from typing import Dict, Any, List
from datetime import datetime
from models.models import PatientRecord, PatientRecordItem, MedicationItem

try:
    from ai.groq_service import get_groq_service
    GROQ_AVAILABLE = True
except Exception as e:
    GROQ_AVAILABLE = False

USE_GROQ = os.getenv("USE_GROQ", "true").lower() == "true" and GROQ_AVAILABLE

TEMPLATE_KEYS = {
    "patient_id",
    "patient_name",
    "surname",
    "date_of_birth",
    "gender",
    "phone",
    "mobile",
    "email",
    "address",
    "suburb",
    "state",
    "occupation",
    "appointment_datetime",
    "procedure",
    "hospital_name",
    "hospital_address",
    "health_fund",
    "insurance_id",
    "gp_name",
    "referrer",
    "comments"
}

def normalize_to_template(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure data follows the exact template schema."""
    if not isinstance(data, dict):
        return {key: None for key in TEMPLATE_KEYS}
    normalized = {}
    for key in TEMPLATE_KEYS:
        normalized[key] = data.get(key, None)
    return normalized

class LLMExtractor:
    """LLM-powered extraction service that maps OCR text to structured JSON."""
    
    @staticmethod
    def extract_structured_data(ocr_text: str, document_type: str = "AUTO", use_groq: bool = None) -> Dict[str, Any]:
        """Extract structured data from OCR text."""
        should_use_groq = use_groq if use_groq is not None else USE_GROQ
        
        if document_type == "AUTO":
            document_type = LLMExtractor._detect_document_type(ocr_text)
        
        # Use Groq extraction if enabled
        if should_use_groq and GROQ_AVAILABLE:
            try:
                # Use strict template extraction
                groq_service = get_groq_service()
                extracted_data = groq_service.extract_key_value_pairs(ocr_text, document_type)
                
                # 🔥 Use advanced mapping to fill the 30+ field template
                mapped_data = groq_service.map_to_template(extracted_data)
                
                # If mapping failed, return normalized extraction
                if "error" in mapped_data:
                    return normalize_to_template(extracted_data)
                
                return mapped_data
            except Exception as e:
                print(f"Extraction/Mapping error: {e}")
                pass  # Fallback to regex
        
        # Regex-based extraction (legacy)
        if document_type == "OPD_NOTE":
            return LLMExtractor._extract_opd_note(ocr_text)
        elif document_type == "LAB_REPORT":
            return LLMExtractor._extract_lab_report(ocr_text)
        elif document_type == "PRESCRIPTION":
            return LLMExtractor._extract_prescription(ocr_text)
        else:
            return LLMExtractor._extract_generic(ocr_text)
    
    @staticmethod
    def match_to_patient_record(extracted_data: Dict[str, Any]) -> PatientRecord:
        """Match extracted data to the standardized PatientRecord template."""
        
        def get_val_conf(field_name: str) -> PatientRecordItem:
            """Extract from nested value/confidence structure if available, else raw."""
            item = extracted_data.get(field_name)
            if isinstance(item, dict):
                val = item.get("value")
                conf = item.get("confidence", "HIGH")
                if val is None or val == "":
                    conf = "NOT_PRESENT_IN_DOC"
                return PatientRecordItem(value=str(val) if val is not None else None, confidence=conf)
            else:
                if item is None or item == "":
                    return PatientRecordItem(value=None, confidence="NOT_PRESENT_IN_DOC")
                return PatientRecordItem(value=str(item), confidence="HIGH")

        # Build comprehensive record
        return PatientRecord(
            # Patient Info
            patient_id=get_val_conf("patient_id"),
            patient_name=get_val_conf("patient_name"),
            surname=get_val_conf("surname"),
            age=get_val_conf("age"),
            gender=get_val_conf("gender"),
            date_of_birth=get_val_conf("date_of_birth"),
            phone=get_val_conf("phone"),
            mobile=get_val_conf("mobile"),
            email=get_val_conf("email"),
            address=get_val_conf("address"),
            occupation=get_val_conf("occupation"),
            
            # Hospital Info
            hospital_name=get_val_conf("hospital_name"),
            hospital_address=get_val_conf("hospital_address"),
            
            # Insurance/Subscriber
            insurance_id=get_val_conf("insurance_id"),
            insurance_type=get_val_conf("insurance_type"),
            group_number=get_val_conf("group_number"),
            subscriber_name=get_val_conf("subscriber_name"),
            medicare_no=get_val_conf("medicare_no"),
            medicare_ref=get_val_conf("medicare_ref"),
            health_fund=get_val_conf("health_fund"),
            health_fund_no=get_val_conf("health_fund_no"),
            vet_affairs=get_val_conf("vet_affairs"),
            
            # Visit/Medical
            visit_date=get_val_conf("visit_date"),
            procedure=get_val_conf("procedure"),
            doctor_name=get_val_conf("doctor_name"),
            gp_name=get_val_conf("gp_name"),
            referrer=get_val_conf("referrer"),
            chief_complaint=get_val_conf("chief_complaint"),
            comments=get_val_conf("comments"),
            
            # Clinical/Vitals
            blood_pressure=get_val_conf("blood_pressure"),
            pulse=get_val_conf("pulse"),
            temperature=get_val_conf("temperature"),
            weight=get_val_conf("weight"),
            spo2=get_val_conf("spo2"),
            diagnosis=get_val_conf("diagnosis"),
            
            # Metadata
            medications=[], # TODO: Handle medications list if needed
            status="VERIFIED" if extracted_data.get("patient_name") else "DRAFT"
        )
    
    @staticmethod
    def _extract_with_groq(ocr_text: str, document_type: str) -> Dict[str, Any]:
        """Extract key-value pairs using Groq API and normalize."""
        groq_service = get_groq_service()
        extracted_data = groq_service.extract_key_value_pairs(ocr_text, document_type)
        return normalize_to_template(extracted_data)
    
    @staticmethod
    def _summarize_with_groq(ocr_text: str, document_type: str) -> Dict[str, Any]:
        """Summarize document using Groq API."""
        groq_service = get_groq_service()
        return groq_service.summarize_text(ocr_text, document_type)
    
    @staticmethod
    def _detect_document_type(text: str) -> str:
        """Auto-detect document type from OCR text."""
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ["opd", "out-patient", "outpatient", "chief complaint"]):
            return "OPD_NOTE"
        elif any(keyword in text_lower for keyword in ["laboratory", "lab report", "test result", "pathologist"]):
            return "LAB_REPORT"
        elif any(keyword in text_lower for keyword in ["prescription", "rx", "medicines prescribed"]):
            return "PRESCRIPTION"
        return "GENERAL"
    
    @staticmethod
    def _extract_opd_note(text: str) -> Dict[str, Any]:
        """Extract structured data from OPD note."""
        extracted = {}
        
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        diagnosis_match = re.search(r'DIAGNOSIS[:\s]+(.*?)(?=\n[A-Z]+:|$)', text, re.IGNORECASE | re.DOTALL)
        if diagnosis_match:
            extracted['diagnosis'] = diagnosis_match.group(1).strip()
        
        bp_match = re.search(r'Blood Pressure[:\s]+(\d+/\d+)', text, re.IGNORECASE)
        if bp_match:
            extracted['blood_pressure'] = bp_match.group(1)
        
        vitals = {}
        pulse_match = re.search(r'Pulse[:\s]+(\d+)', text, re.IGNORECASE)
        temp_match = re.search(r'Temperature[:\s]+([\d.]+)', text, re.IGNORECASE)
        weight_match = re.search(r'Weight[:\s]+([\d.]+)', text, re.IGNORECASE)
        
        if pulse_match:
            vitals['pulse'] = pulse_match.group(1) + " bpm"
        if temp_match:
            vitals['temperature'] = temp_match.group(1) + "°F"
        if weight_match:
            vitals['weight'] = weight_match.group(1) + " kg"
        
        if vitals:
            extracted['vitals'] = vitals
        
        medications = []
        med_section = re.search(r'MEDICATIONS[:\s]+(.*?)(?=\n[A-Z]+:|ADVICE|$)', text, re.IGNORECASE | re.DOTALL)
        if med_section:
            med_lines = med_section.group(1).strip().split('\n')
            for line in med_lines:
                med_match = re.search(r'(?:\d+\.\s*)?([A-Za-z]+)\s+(\d+\s*mg)\s*-\s*([A-Z]+)', line, re.IGNORECASE)
                if med_match:
                    medications.append({
                        "name": med_match.group(1),
                        "dose": med_match.group(2),
                        "frequency": med_match.group(3)
                    })
        
        if medications:
            extracted['medications'] = medications
        
        complaint_match = re.search(r'CHIEF COMPLAINT[:\s]+(.*?)(?=\n[A-Z]+:|$)', text, re.IGNORECASE | re.DOTALL)
        if complaint_match:
            extracted['chief_complaint'] = complaint_match.group(1).strip()
        
        return extracted
    
    @staticmethod
    def _extract_lab_report(text: str) -> Dict[str, Any]:
        """Extract structured data from lab report."""
        extracted = {}
        
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        test_match = re.search(r'TEST[:\s]+(.*?)(?=\n|$)', text, re.IGNORECASE)
        if test_match:
            extracted['test_name'] = test_match.group(1).strip()
        
        date_match = re.search(r'Report Date[:\s]+([\d\-A-Za-z]+)', text, re.IGNORECASE)
        if date_match:
            extracted['test_date'] = date_match.group(1)
        
        results = {}
        result_lines = re.findall(r'([A-Za-z\s]+):\s*([\d.]+)\s*([a-zA-Z/%]+)', text)
        for match in result_lines:
            key = match[0].strip()
            value = f"{match[1]} {match[2]}"
            results[key] = value
        
        if results:
            extracted['results'] = results
        
        remarks_match = re.search(r'REMARKS[:\s]+(.*?)(?=\n[A-Z]+:|Lab Technician|$)', text, re.IGNORECASE | re.DOTALL)
        if remarks_match:
            extracted['remarks'] = remarks_match.group(1).strip()
        
        return extracted
    
    @staticmethod
    def _extract_prescription(text: str) -> Dict[str, Any]:
        """Extract structured data from prescription."""
        extracted = {}
        
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        medications = []
        med_lines = text.split('\n')
        for line in med_lines:
            med_match = re.search(r'([A-Za-z]+)\s+(\d+\s*mg)\s*-\s*([A-Z]+)', line, re.IGNORECASE)
            if med_match:
                medications.append({
                    "name": med_match.group(1),
                    "dose": med_match.group(2),
                    "frequency": med_match.group(3)
                })
        
        if medications:
            extracted['medications'] = medications
        
        return extracted
    
    @staticmethod
    def _extract_generic(text: str) -> Dict[str, Any]:
        """Extract basic information from generic document."""
        extracted = {}
        
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        extracted['raw_text'] = text[:500]
        
        return extracted
    
    @staticmethod
    def calculate_confidence(extracted_data: Dict[str, Any], document_type: str) -> float:
        """Calculate FORM-BASED CONFIDENCE score."""
        if not extracted_data:
            return 0.0
            
        filled = sum(1 for v in extracted_data.values() if v is not None)
        total = len(extracted_data)
        
        if total == 0:
            return 0.0
            
        score = round(filled / total, 2)
        return score
    
    @staticmethod
    def determine_status(confidence: float) -> str:
        """Determine processing status based on confidence score."""
        if confidence >= 0.85:
            return "AUTO_APPROVED"
        elif confidence >= 0.50:
            return "PENDING_REVIEW"
        else:
            return "REJECTED"

