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
    
    def extract_full_template(self, ocr_text: str) -> Dict[str, Any]:
        """
        Direct extraction: Map OCR text to complete template in ONE step.
        This is the primary extraction method - simple and accurate.
        """
        if not self.api_key:
            return {"error": "GROQ_API_KEY not configured"}

        system_prompt = """You are a medical form extraction AI.

Your task is to extract ALL available information from the OCR text and map it to the provided template.

CRITICAL RULES:
1. Extract EVERY field you can find in the OCR text
2. Return null for fields not present in the text
3. DO NOT guess or hallucinate - only use information actually in the OCR text
4. Be smart about field name variations (e.g., "First Name" maps to "patient_name")
5. Combine related fields intelligently (e.g., first name + surname = patient_name)
6. Extract dates, phone numbers, addresses exactly as they appear
7. Clean up OCR noise (e.g., "PhOne:" → phone, "D0B:" → date_of_birth)
8. If multiple values for same field, use the most complete one
9. Return valid JSON matching the exact schema provided"""

        user_prompt = f"""Extract all information from this medical document OCR text.

OCR TEXT:
{ocr_text}

REQUIRED JSON SCHEMA (fill ALL fields you can find):
{{
  "patient_id": null,
  "patient_name": null,
  "surname": null,
  "age": null,
  "date_of_birth": null,
  "gender": null,
  "phone": null,
  "mobile": null,
  "email": null,
  "address": null,
  "suburb": null,
  "state": null,
  "occupation": null,
  "hospital_name": null,
  "hospital_address": null,
  "medicare_no": null,
  "medicare_ref": null,
  "health_fund": null,
  "health_fund_no": null,
  "vet_affairs": null,
  "insurance_id": null,
  "insurance_type": null,
  "group_number": null,
  "subscriber_name": null,
  "visit_date": null,
  "appointment_datetime": null,
  "procedure": null,
  "doctor_name": null,
  "gp_name": null,
  "referrer": null,
  "chief_complaint": null,
  "blood_pressure": null,
  "pulse": null,
  "temperature": null,
  "weight": null,
  "spo2": null,
  "diagnosis": null,
  "comments": null,
  "test_name": null,
  "test_date": null,
  "next_visit_date": null
}}

MAPPING HINTS:
- "First Name" + "Surname" → combine into patient_name
- "UHID" / "Patient ID" / "ID No" → patient_id
- "DOB" / "Birth Date" → date_of_birth
- "Ph" / "Phone" / "Tel" → phone / mobile
- "BP" / "Blood Pressure" → blood_pressure
- "Temp" / "Temperature" → temperature
- "Medicare Number" → medicare_no
- "Medicare REF" / "Ref" → medicare_ref
- "Health Fund" / "Insurance" → health_fund
- "Membership No" / "Member No" → health_fund_no
- "Visit Date" / "Appointment" / "Date" → visit_date or appointment_datetime
- "Procedure" / "Treatment" → procedure
- "Doctor" / "Physician" / "GP" → doctor_name or gp_name
- "Notes" / "Comments" / "Clinical Notes" → comments
- "Diagnosis" / "Condition" → diagnosis

Extract EVERYTHING. Return complete JSON."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            extracted = json.loads(content)
            
            # Log what was extracted
            filled_fields = sum(1 for v in extracted.values() if v not in [None, "", "null", "N/A"])
            print(f"✅ Groq extracted {filled_fields} fields from OCR text")
            
            return extracted
        except Exception as e:
            print(f"❌ Groq extraction error: {e}")
            return {"error": str(e), "raw_text_preview": ocr_text[:200]}

    def extract_key_value_pairs(
        self, 
        comments_text: str = "",
        diagnosis_text: str = ""
    ) -> Dict[str, Any]:
        """Legacy method for clinical text normalization - kept for backward compatibility."""
        if not self.api_key:
            return {"error": "GROQ_API_KEY not configured"}

        system_prompt = """You are a clinical text normalizer. 
Clean up OCR noise and normalize medical terminology.
Return only the cleaned versions of comments and diagnosis."""

        user_prompt = f"""Normalize these clinical text fields:

Comments:
{comments_text or "N/A"}

Diagnosis:
{diagnosis_text or "N/A"}

Return JSON:
{{
  "comments": "<cleaned comments>",
  "diagnosis": "<cleaned diagnosis>"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=512,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {
                "error": str(e),
                "comments": comments_text,
                "diagnosis": diagnosis_text
            }

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


# Singleton instance
_groq_service = None

def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
