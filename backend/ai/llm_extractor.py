"""
LLM-based extraction service for medical documents.
Converts OCR extracted text into structured JSON format.
"""
import re
from typing import Dict, Any, List
from datetime import datetime

class LLMExtractor:
    """
    LLM-powered extraction service that maps OCR text to structured JSON.
    For hackathon: Using intelligent regex + pattern matching (simulates LLM).
    In production: Replace with actual LLM API (OpenAI, Google Gemini, etc.)
    """
    
    @staticmethod
    def extract_structured_data(ocr_text: str, document_type: str = "AUTO") -> Dict[str, Any]:
        """
        Extract structured data from OCR text.
        
        Args:
            ocr_text: Raw text extracted from OCR
            document_type: Type of document (OPD_NOTE, LAB_REPORT, PRESCRIPTION, AUTO)
        
        Returns:
            Structured JSON with extracted fields
        """
        # Auto-detect document type if not specified
        if document_type == "AUTO":
            document_type = LLMExtractor._detect_document_type(ocr_text)
        
        # Route to appropriate extractor
        if document_type == "OPD_NOTE":
            return LLMExtractor._extract_opd_note(ocr_text)
        elif document_type == "LAB_REPORT":
            return LLMExtractor._extract_lab_report(ocr_text)
        elif document_type == "PRESCRIPTION":
            return LLMExtractor._extract_prescription(ocr_text)
        else:
            return LLMExtractor._extract_generic(ocr_text)
    
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
        else:
            return "GENERAL"
    
    @staticmethod
    def _extract_opd_note(text: str) -> Dict[str, Any]:
        """Extract structured data from OPD note."""
        extracted = {}
        
        # Extract UHID (patient_id)
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        # Extract diagnosis
        diagnosis_match = re.search(r'DIAGNOSIS[:\s]+(.*?)(?=\n[A-Z]+:|$)', text, re.IGNORECASE | re.DOTALL)
        if diagnosis_match:
            extracted['diagnosis'] = diagnosis_match.group(1).strip()
        
        # Extract blood pressure
        bp_match = re.search(r'Blood Pressure[:\s]+(\d+/\d+)', text, re.IGNORECASE)
        if bp_match:
            extracted['blood_pressure'] = bp_match.group(1)
        
        # Extract vitals
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
        
        # Extract medications (with dose and frequency)
        medications = []
        med_section = re.search(r'MEDICATIONS[:\s]+(.*?)(?=\n[A-Z]+:|ADVICE|$)', text, re.IGNORECASE | re.DOTALL)
        
        if med_section:
            med_lines = med_section.group(1).strip().split('\n')
            for line in med_lines:
                # Match pattern: "1. Metformin 500mg - BD (After meals)"
                med_match = re.search(r'(?:\d+\.\s*)?([A-Za-z]+)\s+(\d+\s*mg)\s*-\s*([A-Z]+)', line, re.IGNORECASE)
                if med_match:
                    medications.append({
                        "name": med_match.group(1),
                        "dose": med_match.group(2),
                        "frequency": med_match.group(3)
                    })
        
        if medications:
            extracted['medications'] = medications
        
        # Extract chief complaint
        complaint_match = re.search(r'CHIEF COMPLAINT[:\s]+(.*?)(?=\n[A-Z]+:|$)', text, re.IGNORECASE | re.DOTALL)
        if complaint_match:
            extracted['chief_complaint'] = complaint_match.group(1).strip()
        
        return extracted
    
    @staticmethod
    def _extract_lab_report(text: str) -> Dict[str, Any]:
        """Extract structured data from lab report."""
        extracted = {}
        
        # Extract UHID
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        # Extract test name
        test_match = re.search(r'TEST[:\s]+(.*?)(?=\n|$)', text, re.IGNORECASE)
        if test_match:
            extracted['test_name'] = test_match.group(1).strip()
        
        # Extract test date
        date_match = re.search(r'Report Date[:\s]+([\d\-A-Za-z]+)', text, re.IGNORECASE)
        if date_match:
            extracted['test_date'] = date_match.group(1)
        
        # Extract results (key-value pairs like "Hemoglobin: 11.2 g/dL")
        results = {}
        result_lines = re.findall(r'([A-Za-z\s]+):\s*([\d.]+)\s*([a-zA-Z/%]+)', text)
        
        for match in result_lines:
            key = match[0].strip()
            value = f"{match[1]} {match[2]}"
            results[key] = value
        
        if results:
            extracted['results'] = results
        
        # Extract remarks
        remarks_match = re.search(r'REMARKS[:\s]+(.*?)(?=\n[A-Z]+:|Lab Technician|$)', text, re.IGNORECASE | re.DOTALL)
        if remarks_match:
            extracted['remarks'] = remarks_match.group(1).strip()
        
        return extracted
    
    @staticmethod
    def _extract_prescription(text: str) -> Dict[str, Any]:
        """Extract structured data from prescription."""
        extracted = {}
        
        # Extract UHID
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        # Extract medications
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
        
        # Try to extract UHID
        uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        extracted['patient_id'] = uhid_match.group(1) if uhid_match else "UNKNOWN"
        
        # Store raw text for manual review
        extracted['raw_text'] = text[:500]  # First 500 chars
        
        return extracted
    
    @staticmethod
    def calculate_confidence(extracted_data: Dict[str, Any], document_type: str) -> float:
        """
        Calculate confidence score based on extracted fields.
        
        Args:
            extracted_data: Extracted structured data
            document_type: Type of document
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_score = 0.5
        score = base_score
        
        # Define required fields per document type
        required_fields = {
            "OPD_NOTE": ["patient_id", "diagnosis", "medications"],
            "LAB_REPORT": ["patient_id", "test_name", "results"],
            "PRESCRIPTION": ["patient_id", "medications"],
            "GENERAL": ["patient_id"]
        }
        
        optional_fields = {
            "OPD_NOTE": ["blood_pressure", "vitals", "chief_complaint"],
            "LAB_REPORT": ["test_date", "remarks"],
            "PRESCRIPTION": [],
            "GENERAL": []
        }
        
        req_fields = required_fields.get(document_type, [])
        opt_fields = optional_fields.get(document_type, [])
        
        # Check required fields
        required_found = sum(1 for field in req_fields if field in extracted_data and extracted_data[field])
        if req_fields:
            score += (required_found / len(req_fields)) * 0.4
        
        # Check optional fields
        optional_found = sum(1 for field in opt_fields if field in extracted_data and extracted_data[field])
        if opt_fields:
            score += (optional_found / len(opt_fields)) * 0.1
        
        # Bonus for having all required fields
        if required_found == len(req_fields) and len(req_fields) > 0:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    @staticmethod
    def determine_status(confidence: float) -> str:
        """
        Determine processing status based on confidence score.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
        
        Returns:
            Status string (AUTO_APPROVED, PENDING_REVIEW, REJECTED)
        """
        if confidence >= 0.90:
            return "AUTO_APPROVED"
        elif confidence >= 0.70:
            return "PENDING_REVIEW"
        else:
            return "REJECTED"
