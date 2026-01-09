"""
Groq API Service for Medical Document Key-Value Extraction
Uses Groq's Qwen model to intelligently extract key-value pairs from OCR text.
"""
import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
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
        
        # Configuration
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
        
        Args:
            ocr_text: Raw text extracted from OCR
            document_type: Optional document type hint (OPD_NOTE, LAB_REPORT, PRESCRIPTION)
        
        Returns:
            Dictionary of extracted key-value pairs
        """
        # Build the prompt based on document type
        prompt = self._build_extraction_prompt(ocr_text, document_type)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = response.choices[0].message.content
            extracted_data = json.loads(result)
            
            return extracted_data
            
        except Exception as e:
            print(f"Groq API error: {e}")
            # Return fallback structure
            return {
                "error": str(e),
                "raw_text": ocr_text[:200]  # First 200 chars for reference
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for medical document extraction."""
        return """You are an expert medical document data extraction assistant. 
Your task is to extract key-value pairs from medical documents (OPD notes, lab reports, prescriptions).

RULES:
1. Extract ALL relevant information as key-value pairs
2. Use clear, descriptive keys (e.g., "Patient ID", "Diagnosis", "Blood Pressure")
3. Keep values concise and accurate
4. For medications, include dose and frequency in the value (e.g., "Metformin: 500mg BD")
5. For multiple items of the same type, number them (e.g., "Medication 1", "Medication 2")
6. Extract dates in original format
7. Include vitals, test results, diagnoses, medications, and patient identifiers
8. Return ONLY valid JSON with string keys and string values
9. If a field is not found, omit it from the output
10. Maintain medical terminology accuracy

OUTPUT FORMAT:
{
  "Patient ID": "UHID-12345",
  "Patient Name": "John Doe",
  "Date": "2024-01-15",
  "Diagnosis": "Type 2 Diabetes Mellitus",
  "Blood Pressure": "120/80 mmHg",
  "Pulse": "72 bpm",
  "Temperature": "98.6°F",
  "Medication 1": "Metformin 500mg - BD (After meals)",
  "Medication 2": "Glimepiride 2mg - OD (Before breakfast)",
  "Doctor Name": "Dr. Smith",
  "Next Visit": "2024-02-15"
}"""
    
    def _build_extraction_prompt(
        self, 
        ocr_text: str, 
        document_type: Optional[str]
    ) -> str:
        """Build the user prompt for extraction."""
        prompt = f"""Extract all key-value pairs from the following medical document OCR text.

Document Type: {document_type if document_type else "Unknown (auto-detect)"}

OCR Text:
{ocr_text}

Extract all relevant medical information as key-value pairs in JSON format.
Focus on: Patient identifiers, diagnoses, medications, vitals, test results, dates, and doctor information."""
        
        return prompt
    
    def test_connection(self) -> bool:
        """Test the Groq API connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply with 'OK' if you can read this."
                    }
                ],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"Groq connection test failed: {e}")
            return False


# Singleton instance
_groq_service = None

def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
