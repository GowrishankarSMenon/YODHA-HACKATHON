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

# Try to import Groq service (optional)
try:
    from ai.groq_service import get_groq_service
    GROQ_AVAILABLE = True
except Exception as e:
    GROQ_AVAILABLE = False
    print(f"⚠️ Groq service not available: {e}")

# Configuration: Use Groq by default if available
USE_GROQ = os.getenv("USE_GROQ", "true").lower() == "true" and GROQ_AVAILABLE

class LLMExtractor:
    """
    LLM-powered extraction service that maps OCR text to structured JSON.
    For hackathon: Using intelligent regex + pattern matching (simulates LLM).
    In production: Replace with actual LLM API (OpenAI, Google Gemini, etc.)
    """
    
    @staticmethod
    def extract_structured_data(
        ocr_text: str, 
        document_type: str = "AUTO",
        use_groq: bool = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from OCR text.
        
        Args:
            ocr_text: Raw text extracted from OCR
            document_type: Type of document (OPD_NOTE, LAB_REPORT, PRESCRIPTION, AUTO)
            use_groq: Force Groq usage (True/False) or None for auto-detection
        
        Returns:
            Structured JSON with extracted fields (key-value pairs if using Groq)
        """
        print("\n" + "#"*80)
        print("📊 LLM EXTRACTOR - extract_structured_data() called")
        print("#"*80)
        print(f"📄 OCR Text Length: {len(ocr_text)}")
        print(f"📋 Document Type (input): {document_type}")
        print(f"🔧 use_groq param: {use_groq}")
        print(f"🔧 USE_GROQ global: {USE_GROQ}")
        print(f"🔧 GROQ_AVAILABLE: {GROQ_AVAILABLE}")
        
        # Determine if we should use Groq
        should_use_groq = use_groq if use_groq is not None else USE_GROQ
        print(f"✅ should_use_groq: {should_use_groq}")
        
        # Auto-detect document type if not specified
        if document_type == "AUTO":
            document_type = LLMExtractor._detect_document_type(ocr_text)
            print(f"🔍 Auto-detected Document Type: {document_type}")
        
        # Use Groq extraction if enabled and available
        if should_use_groq and GROQ_AVAILABLE:
            try:
                print(f"\n🚀 Using GROQ extraction method")
                result = LLMExtractor._extract_with_groq(ocr_text, document_type)
                print(f"✅ Groq extraction returned: {type(result)}")
                print(f"📊 Groq result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            except Exception as e:
                print(f"\n❌ Groq extraction failed: {type(e).__name__}: {e}")
                print(f"🔄 Falling back to regex extraction")
                # Fallback to regex extraction
        
        # Route to appropriate regex-based extractor (original method)
        print(f"\n🔧 Using REGEX extraction method for {document_type}")
        if document_type == "OPD_NOTE":
            result = LLMExtractor._extract_opd_note(ocr_text)
        elif document_type == "LAB_REPORT":
            result = LLMExtractor._extract_lab_report(ocr_text)
        elif document_type == "PRESCRIPTION":
            result = LLMExtractor._extract_prescription(ocr_text)
        else:
            result = LLMExtractor._extract_generic(ocr_text)
        
        print(f"✅ Regex extraction returned: {type(result)}")
        print(f"📊 Regex result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print("#"*80)
        return result
    
    @staticmethod
    def _extract_with_groq(ocr_text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract key-value pairs using Groq API.
        
        Args:
            ocr_text: Raw OCR text
            document_type: Document type hint
        
        Returns:
            Dictionary of extracted key-value pairs
        """
        print(f"\n🔗 _extract_with_groq() - Getting Groq service...")
        groq_service = get_groq_service()
        print(f"✅ Groq service obtained: {type(groq_service)}")
        
        print(f"\n📞 Calling groq_service.extract_key_value_pairs()...")
        extracted_data = groq_service.extract_key_value_pairs(ocr_text, document_type)
        
        print(f"\n✅ Received data from Groq service:")
        print(f"   Type: {type(extracted_data)}")
        print(f"   Is None: {extracted_data is None}")
        if extracted_data is not None:
            print(f"   Keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Not a dict'}")
            print(f"   Content: {json.dumps(extracted_data, indent=2) if isinstance(extracted_data, dict) else str(extracted_data)}")
        
        return extracted_data
    
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
        Supports both Groq key-value format and regex structured format.
        
        Args:
            extracted_data: Extracted structured data (nested or key-value pairs)
            document_type: Type of document
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        print(f"\n📊 calculate_confidence() called")
        print(f"   Data type: {type(extracted_data)}")
        print(f"   Data is None: {extracted_data is None}")
        print(f"   Document type: {document_type}")
        
        # Detect if this is Groq key-value format (flat with human-readable keys)
        # vs regex format (nested with technical keys)
        is_groq_format = LLMExtractor._is_groq_format(extracted_data)
        print(f"   Is Groq format: {is_groq_format}")
        
        if is_groq_format:
            return LLMExtractor._calculate_groq_confidence(extracted_data, document_type)
        else:
            return LLMExtractor._calculate_regex_confidence(extracted_data, document_type)
    
    @staticmethod
    def _is_groq_format(extracted_data: Dict[str, Any]) -> bool:
        """Detect if extracted data is in Groq key-value format."""
        # Groq format characteristics:
        # - Flat structure (no nested dicts/lists)
        # - Human-readable keys (capitalized, spaces)
        # - String values
        
        if not extracted_data:
            return False
        
        # Check for common Groq keys (capitalized, human-readable)
        groq_indicators = [
            "Patient Name", "Patient ID", "UHID", 
            "Diagnosis", "Doctor", "Hospital",
            "Test Name", "Report Date", "Medication"
        ]
        
        has_groq_key = any(key in extracted_data for key in groq_indicators)
        
        # Check if mostly flat structure
        has_nested = any(isinstance(v, (dict, list)) for v in extracted_data.values())
        
        return has_groq_key and not has_nested
    
    @staticmethod
    def _calculate_groq_confidence(extracted_data: Dict[str, Any], document_type: str) -> float:
        """
        Calculate confidence for Groq-extracted key-value pairs.
        Based on number of fields extracted and data quality.
        """
        # Count extracted fields
        num_fields = len(extracted_data)
        
        # Exclude error fields
        if "error" in extracted_data:
            return 0.3
        
        # Base score on number of extracted fields
        if num_fields >= 15:
            score = 0.95  # Excellent extraction
        elif num_fields >= 10:
            score = 0.85  # Good extraction
        elif num_fields >= 6:
            score = 0.75  # Acceptable extraction
        elif num_fields >= 3:
            score = 0.60  # Minimal extraction
        else:
            score = 0.50  # Poor extraction
        
        # Bonus for critical medical fields
        critical_fields = [
            "Patient ID", "UHID", "Patient Name",
            "Diagnosis", "Test Name", "Medication",
            "Doctor", "Pathologist"
        ]
        
        critical_found = sum(1 for field in critical_fields if field in extracted_data)
        if critical_found > 0:
            score += min(critical_found * 0.02, 0.10)  # Up to +0.10 bonus
        
        # Cap at 1.0
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_regex_confidence(extracted_data: Dict[str, Any], document_type: str) -> float:
        """
        Calculate confidence for regex-extracted structured data (original method).
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
