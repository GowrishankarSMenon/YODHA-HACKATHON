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
        ocr_text: str, 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract key-value pairs from OCR text using Groq's LLM.
        """
        prompt = self._build_extraction_prompt(ocr_text, document_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except json.JSONDecodeError as je:
            return {
                "error": f"JSON decode error: {str(je)}",
                "raw_text": ocr_text[:200]
            }
        except Exception as e:
            return {
                "error": str(e),
                "raw_text": ocr_text[:200]
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for strict medical form filling."""
        return """You are a medical form-filling AI.

The medical document image ALWAYS follows the SAME FIXED FORMAT.

Your task is to FILL ALL FIELDS in the given JSON schema using the OCR text.

STRICT RULES:
1. Use ONLY the keys provided in the schema
2. DO NOT create new keys
3. DO NOT rename keys
4. DO NOT omit any key
5. If a value is NOT visible in the OCR text, return null
6. DO NOT guess or hallucinate values
7. Return ONLY valid JSON (no text, no explanations)

Accuracy is more important than completeness."""

    def _build_extraction_prompt(
        self,
        ocr_text: str,
        document_type: Optional[str]
    ) -> str:
        """Build a strict template prompt for form filling."""
        return f"""Fill the following medical registration form using the OCR text below.

Return JSON ONLY.

Schema:
{{
  "patient_id": null,
  "patient_name": null,
  "surname": null,
  "date_of_birth": null,
  "gender": null,
  "phone": null,
  "mobile": null,
  "email": null,
  "address": null,
  "suburb": null,
  "state": null,
  "occupation": null,
  "appointment_datetime": null,
  "procedure": null,
  "hospital_name": null,
  "hospital_address": null,
  "health_fund": null,
  "insurance_id": null,
  "gp_name": null,
  "referrer": null,
  "comments": null
}}

OCR TEXT:
<<<
{ocr_text}
>>>"""

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
