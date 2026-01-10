"""
Groq API Service for Medical Document Key-Value Extraction
Uses Groq's Qwen model to intelligently extract key-value pairs from OCR text.
"""
import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    """Service for interacting with Groq API for LLM-based extraction."""
    
    def __init__(self):
        """Initialize Groq client with API key."""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please create a .env file with your Groq API key."
            )
        
        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "2000"))
    
    def extract_key_value_pairs(
        self, 
        comments_text: str = "",
        diagnosis_text: str = ""
    ) -> Dict[str, Any]:
        """Normalize free-text clinical regions using Groq's LLM."""
        if not self.api_key:
            return {"error": "GROQ_API_KEY not configured"}

        system_prompt = self._get_system_prompt()
        user_prompt = self._build_extraction_prompt(comments_text, diagnosis_text)
        
        try:
            client = Groq(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "qwen-2.5-32b"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # The original error handling used ocr_text.
            # Since ocr_text is no longer an argument, we use comments_text as a preview.
            return {
                "error": str(e),
                "raw_text_preview": comments_text[:200]
            }

    def extract_full_template(self, ocr_text: str) -> Dict[str, Any]:
        """Fallback: Extract full template from raw OCR text when layout-aware extraction fails."""
        if not self.api_key:
            return {"error": "GROQ_API_KEY not configured"}

        system_prompt = self._get_full_extraction_system_prompt()
        user_prompt = self._build_full_extraction_user_prompt(ocr_text)
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "qwen-2.5-32b"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "raw_text_preview": ocr_text[:200]}

    def _get_full_extraction_system_prompt(self) -> str:
        """System prompt for full template extraction (fallback mode)."""
        return """You are a medical form-filling AI.

Your task:
- Fill ALL fields in the given JSON schema using the OCR text.
- Return null for missing fields.
- DO NOT hallucinate info.
- Return JSON strictly matching the keys below."""

    def _build_full_extraction_user_prompt(self, ocr_text: str) -> str:
        """User prompt for full template extraction (fallback mode)."""
        return f"""Fill the following medical registration form using the OCR text.

Schema:
{{
  "patient_name": null, "surname": null, "date_of_birth": null, "gender": null,
  "phone": null, "mobile": null, "email": null, "address": null,
  "suburb": null, "state": null, "occupation": null, "appointment_datetime": null,
  "procedure": null, "hospital_name": null, "hospital_address": null,
  "health_fund": null, "insurance_id": null, "gp_name": null, "referrer": null,
  "comments": null, "diagnosis": null
}}

OCR TEXT:
{ocr_text}
"""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for layout-aware medical extraction."""
        return """You are part of a medical document extraction pipeline.

The system uses Layout-aware OCR (LayoutLMv3 / Tesseract with bounding boxes).
Text positions (rows, columns, labels) are already known.

Your role is NOT to guess structure.
Your role is ONLY to:

1. Read already-identified field regions (label + value boxes)
2. Normalize the values (clean spelling, fix OCR noise)
3. Extract ONLY free-text clinical meaning from:
   - Comments
   - Diagnosis
   - Doctor notes
4. NEVER infer missing structured fields like:
   - Name, DOB, Phone, Address, Insurance, IDs
   These are filled deterministically by layout anchors.

Rules:
- Do not create or rename fields.
- Do not guess values that are not visible.
- Do not use world knowledge.
- If text is unclear, return null.
- Return JSON strictly in the provided template.
- Do not hallucinate.

Pipeline order:
Layout OCR → Field Anchoring → You (free-text normalization only) → Template → DB

Your output must be clean, medical, and deterministic."""

    def _build_extraction_prompt(
        self,
        comments_text: str = "",
        diagnosis_text: str = ""
    ) -> str:
        """Build a layout-aware prompt for free-text normalization."""
        return f"""The following text comes from specific layout regions of a fixed medical form.

Structured fields are already mapped by position.
You must only clean and normalize them.

Free-text regions (for interpretation):
- Comments:
<<<{(comments_text or "N/A")}>>>

- Diagnosis:
<<<{(diagnosis_text or "N/A")}>>>

Return JSON:
{{
  "diagnosis": null,
  "comments": null
}}

Do NOT extract names, dates, numbers, or IDs.
Do NOT invent missing data."""

    def summarize_text(self, ocr_text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Summarize OCR text using Groq's LLM."""
        prompt = f"""Please provide a clear, concise summary of this medical document.
        
Document Type: {document_type if document_type else "Unknown"}

OCR Text:
{ocr_text}

Your summary should cover the key medical details (patient issues, diagnosis, medications, key results) in 3-5 sentences.
Return ONLY a JSON object with a single key "Summary" containing the text summary."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant. Summarize medical documents clearly and accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"Raw Text Preview": ocr_text[:500] + "..."}

    def map_to_template(self, extracted_data: Dict[str, Any], target_template: str = "PatientRecord") -> Dict[str, Any]:
        """Map extracted data to a standardized template using Groq."""
        prompt = f"""
You are a medical data standardization expert.
Your task is to map the following extracted data to a standardized 'PatientRecord' JSON template.

CRITICAL: Map the MAXIMUM number of fields possible. Be thorough and intelligent about mapping.

INPUT DATA:
{json.dumps(extracted_data, indent=2)}

TARGET TEMPLATE STRUCTURE:
{{
  "patient_id": {{ "value": "UHID-123", "confidence": "HIGH/LOW/MISSING" }},
  "patient_name": {{ "value": "Name", "confidence": "HIGH/LOW/MISSING" }},
  "age": {{ "value": "45", "confidence": "HIGH/LOW/MISSING" }},
  "gender": {{ "value": "M/F", "confidence": "HIGH/LOW/MISSING" }},
  "date_of_birth": {{ "value": "YYYY-MM-DD", "confidence": "HIGH/LOW/MISSING" }},
  "address": {{ "value": "123 St, Place", "confidence": "HIGH/LOW/MISSING" }},
  "phone": {{ "value": "1234567890", "confidence": "HIGH/LOW/MISSING" }},
  "mobile": {{ "value": "9876543210", "confidence": "HIGH/LOW/MISSING" }},
  "email": {{ "value": "email@example.com", "confidence": "HIGH/LOW/MISSING" }},
  "occupation": {{ "value": "Job Title", "confidence": "HIGH/LOW/MISSING" }},

  "hospital_name": {{ "value": "Hospital Name", "confidence": "HIGH/LOW/MISSING" }},
  "hospital_address": {{ "value": "Hospital Info", "confidence": "HIGH/LOW/MISSING" }},

  "medicare_no": {{ "value": "123...", "confidence": "HIGH/LOW/MISSING" }},
  "medicare_ref": {{ "value": "Ref", "confidence": "HIGH/LOW/MISSING" }},
  "health_fund": {{ "value": "Fund Name", "confidence": "HIGH/LOW/MISSING" }},
  "health_fund_no": {{ "value": "Num", "confidence": "HIGH/LOW/MISSING" }},
  "vet_affairs": {{ "value": "N/A", "confidence": "HIGH/LOW/MISSING" }},

  "insurance_id": {{ "value": "INS-123", "confidence": "HIGH/LOW/MISSING" }},
  "insurance_type": {{ "value": "Primary/Secondary", "confidence": "HIGH/LOW/MISSING" }},
  "group_number": {{ "value": "GRP-123", "confidence": "HIGH/LOW/MISSING" }},
  "subscriber_name": {{ "value": "Subscriber", "confidence": "HIGH/LOW/MISSING" }},

  "visit_date": {{ "value": "YYYY-MM-DD HH:MM", "confidence": "HIGH/LOW/MISSING" }},
  "procedure": {{ "value": "Procedure Name", "confidence": "HIGH/LOW/MISSING" }},
  "doctor_name": {{ "value": "Dr. Name", "confidence": "HIGH/LOW/MISSING" }},
  "gp_name": {{ "value": "GP Name", "confidence": "HIGH/LOW/MISSING" }},
  "referrer": {{ "value": "Ref Doctor", "confidence": "HIGH/LOW/MISSING" }},
  "chief_complaint": {{ "value": "Complaint", "confidence": "HIGH/LOW/MISSING" }},

  "blood_pressure": {{ "value": "120/80", "confidence": "HIGH/LOW/MISSING" }},
  "pulse": {{ "value": "72 bpm", "confidence": "HIGH/LOW/MISSING" }},
  "temperature": {{ "value": "98.6°F", "confidence": "HIGH/LOW/MISSING" }},
  "weight": {{ "value": "70 kg", "confidence": "HIGH/LOW/MISSING" }},
  "spo2": {{ "value": "98%", "confidence": "HIGH/LOW/MISSING" }},

  "diagnosis": {{ "value": "Diagnosis", "confidence": "HIGH/LOW/MISSING" }},
  "comments": {{ "value": "Notes...", "confidence": "HIGH/LOW/MISSING" }},
  "test_name": {{ "value": "Test", "confidence": "HIGH/LOW/MISSING" }},
  "test_date": {{ "value": "YYYY-MM-DD", "confidence": "HIGH/LOW/MISSING" }},
  "next_visit_date": {{ "value": "YYYY-MM-DD", "confidence": "HIGH/LOW/MISSING" }},
  
  "medications": [
    {{ "name": "Med Name", "dosage": "500mg", "frequency": "BD", "confidence": "HIGH" }}
  ]
}}

MAPPING INSTRUCTIONS:
1. Map ALL possible fields from INPUT DATA to TARGET TEMPLATE (30+ fields total)
2. Look for similar/variant key names:
   - "First Name" + "Surname" → patient_name
   - "Suburb" + "Street" → address
   - "Medicare No" → medicare_no
   - "Membership No" → health_fund_no
3. Extract numeric values and units separately if needed
4. For medications, parse out name, dosage, and frequency from combined strings
5. Set confidence to "HIGH" if data clearly present, "LOW" if inferred/partial, "MISSING" if not found
6. For MISSING fields, set value to null
7. Be intelligent about synonyms:
   - "Heart Rate" = pulse
   - "Oxygen"/"O2" = spo2
   - "Body Temp" = temperature
   - "Ref" = medicare_ref
8. Extract dates and normalize to YYYY-MM-DD if possible
9. Split combined medication strings intelligently
10. Return ONLY valid JSON matching the target template structure
11. Populate ALL template fields - maximize the mapping coverage
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                 messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data mapping assistant specialized in medical records. Extract and map the maximum possible information. Output valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_groq_service = None

def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
