"""
LLM-based extraction service for medical documents.
Converts OCR extracted text into structured JSON format.
Simplified approach: Direct OCR -> Groq LLM -> Template mapping.
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

class LLMExtractor:
    """LLM-powered extraction service that maps OCR text to structured JSON."""
    
    @staticmethod
    def extract_structured_data(ocr_text: str, document_type: str = "AUTO", use_groq: bool = None, image = None) -> Dict[str, Any]:
        """
        Extract structured data from OCR text using Groq LLM.
        Simple pipeline: OCR Text → Groq LLM → Structured Data
        """
        should_use_groq = use_groq if use_groq is not None else USE_GROQ
        
        if document_type == "AUTO":
            document_type = LLMExtractor._detect_document_type(ocr_text)
        
        if should_use_groq and GROQ_AVAILABLE:
            try:
                print("🤖 Using Groq LLM for direct extraction...")
                groq_service = get_groq_service()
                
                # Single-step extraction: OCR text → Complete template
                extracted_data = groq_service.extract_full_template(ocr_text)
                
                if "error" in extracted_data:
                    print(f"⚠️ Groq error, falling back to basic extraction: {extracted_data['error']}")
                    return LLMExtractor._fallback_extraction(ocr_text, document_type)
                
                return extracted_data
                
            except Exception as e:
                print(f"❌ Groq extraction failed: {e}")
                return LLMExtractor._fallback_extraction(ocr_text, document_type)
        else:
            print("ℹ️ Groq not available, using fallback extraction")
            return LLMExtractor._fallback_extraction(ocr_text, document_type)
    
    @staticmethod
    def _fallback_extraction(ocr_text: str, document_type: str) -> Dict[str, Any]:
        """Simple regex-based fallback extraction."""
        extracted = {}
        
        # Extract common fields using regex
        uhid_match = re.search(r'(?:UHID|Patient ID|ID)[:\s]+([A-Z0-9\-]+)', ocr_text, re.IGNORECASE)
        if uhid_match:
            extracted['patient_id'] = uhid_match.group(1)
        
        name_match = re.search(r'(?:Name|Patient Name)[:\s]+([A-Za-z\s]+)', ocr_text, re.IGNORECASE)
        if name_match:
            extracted['patient_name'] = name_match.group(1).strip()
        
        dob_match = re.search(r'(?:DOB|Date of Birth)[:\s]+([0-9\/\-]+)', ocr_text, re.IGNORECASE)
        if dob_match:
            extracted['date_of_birth'] = dob_match.group(1)
        
        gender_match = re.search(r'(?:Gender|Sex)[:\s]+([MFmf])', ocr_text, re.IGNORECASE)
        if gender_match:
            extracted['gender'] = gender_match.group(1).upper()
        
        phone_match = re.search(r'(?:Phone|Mobile|Tel)[:\s]+([0-9\s\-\+]+)', ocr_text, re.IGNORECASE)
        if phone_match:
            extracted['phone'] = phone_match.group(1).strip()
        
        return extracted
    
    @staticmethod
    def match_to_patient_record(extracted_data: Dict[str, Any]) -> PatientRecord:
        """
        Match extracted data to the standardized PatientRecord template.
        NO confidence filtering - all fields are populated with HIGH confidence.
        """
        
        def get_val(field_name: str) -> PatientRecordItem:
            """Extract value and set confidence to HIGH for all fields."""
            value = extracted_data.get(field_name)
            
            # Handle nested dict structure (if present from old extraction)
            if isinstance(value, dict):
                value = value.get("value")
            
            # Convert to string if present, otherwise None
            if value is not None and value != "" and value != "null" and value != "N/A":
                return PatientRecordItem(value=str(value), confidence="HIGH")
            else:
                return PatientRecordItem(value=None, confidence="HIGH")

        # Build comprehensive record - ALL fields get HIGH confidence
        return PatientRecord(
            # Patient Info
            patient_id=get_val("patient_id"),
            patient_name=get_val("patient_name"),
            surname=get_val("surname"),
            age=get_val("age"),
            gender=get_val("gender"),
            date_of_birth=get_val("date_of_birth"),
            phone=get_val("phone"),
            mobile=get_val("mobile"),
            email=get_val("email"),
            address=get_val("address"),
            suburb=get_val("suburb"),
            state=get_val("state"),
            occupation=get_val("occupation"),
            
            # Hospital Info
            hospital_name=get_val("hospital_name"),
            hospital_address=get_val("hospital_address"),
            
            # Insurance/Subscriber
            insurance_id=get_val("insurance_id"),
            insurance_type=get_val("insurance_type"),
            group_number=get_val("group_number"),
            subscriber_name=get_val("subscriber_name"),
            medicare_no=get_val("medicare_no"),
            medicare_ref=get_val("medicare_ref"),
            health_fund=get_val("health_fund"),
            health_fund_no=get_val("health_fund_no"),
            vet_affairs=get_val("vet_affairs"),
            
            # Visit/Medical
            visit_date=get_val("visit_date") if "visit_date" in extracted_data else get_val("appointment_datetime"),
            procedure=get_val("procedure"),
            doctor_name=get_val("doctor_name"),
            gp_name=get_val("gp_name"),
            referrer=get_val("referrer"),
            chief_complaint=get_val("chief_complaint"),
            comments=get_val("comments"),
            
            # Clinical/Vitals
            blood_pressure=get_val("blood_pressure"),
            pulse=get_val("pulse"),
            temperature=get_val("temperature"),
            weight=get_val("weight"),
            spo2=get_val("spo2"),
            diagnosis=get_val("diagnosis"),
            
            # Metadata
            medications=[],
            status="VERIFIED"
        )
    
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
    def calculate_confidence(extracted_data: Dict[str, Any], document_type: str) -> float:
        """
        Calculate confidence score based on number of filled fields.
        NOTE: This is for reporting only - doesn't affect extraction anymore.
        """
        if not extracted_data:
            return 0.0
            
        filled = sum(1 for v in extracted_data.values() if v not in [None, "", "null", "N/A"])
        total = len(extracted_data)
        
        if total == 0:
            return 0.0
            
        score = round(filled / total, 2)
        return score
    
    @staticmethod
    def determine_status(confidence: float) -> str:
        """
        Determine processing status.
        All records are marked as VERIFIED now (no confidence filtering).
        """
        return "VERIFIED"
