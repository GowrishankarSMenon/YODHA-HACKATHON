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
        print("\n" + "="*80)
        print("🔍 GROQ SERVICE - extract_key_value_pairs() called")
        print("="*80)
        print(f"📄 Input OCR Text Length: {len(ocr_text)} characters")
        print(f"📋 Document Type: {document_type}")
        print(f"📝 First 200 chars of OCR: {ocr_text[:200]}...")
        
        # Build the prompt based on document type
        prompt = self._build_extraction_prompt(ocr_text, document_type)
        print(f"\n✉️  Prompt Built - Length: {len(prompt)} characters")
        
        try:
            print("\n🚀 Calling Groq API...")
            print(f"   Model: {self.model}")
            print(f"   Temperature: {self.temperature}")
            print(f"   Max Tokens: {self.max_tokens}")
            
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
            
            print("\n✅ Groq API Response Received")
            
            # Parse the response
            result = response.choices[0].message.content
            print(f"\n📦 Raw Response Content Type: {type(result)}")
            print(f"📦 Raw Response Content Length: {len(result) if result else 0}")
            print(f"📦 Raw Response (first 500 chars): {result[:500] if result else 'None'}")
            
            print("\n🔄 Parsing JSON...")
            extracted_data = json.loads(result)
            
            print(f"\n✅ JSON Parsed Successfully!")
            print(f"📊 Extracted Data Type: {type(extracted_data)}")
            print(f"📊 Extracted Data Keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Not a dict'}")
            print(f"📊 Number of Fields: {len(extracted_data) if isinstance(extracted_data, dict) else 0}")
            print(f"📊 Full Extracted Data: {json.dumps(extracted_data, indent=2)}")
            print("="*80)
            
            return extracted_data
            
        except json.JSONDecodeError as je:
            print(f"\n❌ JSON Decode Error: {je}")
            print(f"❌ Failed to parse: {result[:500] if result else 'No result'}")
            print("="*80)
            # Return fallback structure
            return {
                "error": f"JSON decode error: {str(je)}",
                "raw_text": ocr_text[:200]  # First 200 chars for reference
            }
        except Exception as e:
            print(f"\n❌ Groq API Error: {type(e).__name__}: {e}")
            print(f"❌ Full Error: {repr(e)}")
            print("="*80)
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
    


    def summarize_text(
        self, 
        ocr_text: str, 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize OCR text using Groq's LLM.
        
        Args:
            ocr_text: Raw text extracted from OCR
            document_type: Optional document type hint
        
        Returns:
            Dictionary with a single 'Summary' key
        """
        print("\n" + "="*80)
        print("📝 GROQ SERVICE - summarize_text() called")
        print("="*80)
        
        prompt = f"""Please provide a clear, concise summary of this medical document.
        
Document Type: {document_type if document_type else "Unknown"}

OCR Text:
{ocr_text}

Your summary should cover the key medical details (patient issues, diagnosis, medications, key results) in 3-5 sentences.
Return ONLY a JSON object with a single key "Summary" containing the text summary."""

        try:
            print("\n🚀 Calling Groq API for summary...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful medical assistant. Summarize medical documents clearly and accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3, # Slightly higher for more natural language
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            print(f"\n✅ Summary received: {result[:100]}...")
            
            return json.loads(result)
            
        except Exception as e:
            print(f"\n❌ Summary generation failed: {e}")
            return {
                "Raw Text Preview": ocr_text[:500] + "..."
            }

    def map_to_template(
        self, 
        extracted_data: Dict[str, Any], 
        target_template: str = "PatientRecord"
    ) -> Dict[str, Any]:
        """
        Map extracted data to a standardized template using Groq.
        """
        print("\n" + "="*80)
        print("🔄 GROQ SERVICE - map_to_template() called")
        print("="*80)
        
        prompt = f"""
You are a medical data standardization expert.
Your task is to map the following extracted data to a standardized 'PatientRecord' JSON template.

INPUT DATA:
{json.dumps(extracted_data, indent=2)}

TARGET TEMPLATE STRUCTURE:
{{
  "patient_name": {{ "value": "Name", "confidence": "HIGH/LOW/MISSING" }},
  "diagnosis": {{ "value": "Diagnosis", "confidence": "HIGH/LOW/MISSING" }},
  "blood_pressure": {{ "value": "120/80", "confidence": "HIGH/LOW/MISSING" }},
  "visit_date": {{ "value": "YYYY-MM-DD", "confidence": "HIGH/LOW/MISSING" }},
  "medications": [
    {{ "name": "Med Name", "dosage": "500mg", "frequency": "BD", "confidence": "HIGH" }}
  ]
}}

INSTRUCTIONS:
1. Map fields from INPUT DATA to the TARGET TEMPLATE.
2. If a field is missing or has very low confidence in the input, set "value" to null and "confidence" to "MISSING" or "LOW".
3. For medications, normalize the list.
4. Return ONLY valid JSON matching the target template structure.
"""

        try:
            print("\n🚀 Calling Groq API for template matching...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data mapping assistant. Output valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            print(f"\n✅ Template mapping received: {result[:100]}...")
            
            return json.loads(result)
            
        except Exception as e:
            print(f"\n❌ Template mapping failed: {e}")
            # Return empty structure on failure
            return {{
                "error": str(e)
            }}


# Singleton instance
_groq_service = None

def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
