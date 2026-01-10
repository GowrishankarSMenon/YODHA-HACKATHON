groq_service.py:-

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
    
    def _init_(self):
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
        print("\n" + "="*80)
        print("🔍 GROQ SERVICE - extract_key_value_pairs() called")
        print("="*80)
        print(f"📄 Input OCR Text Length: {len(ocr_text)} characters")
        print(f"📋 Document Type: {document_type}")
        print(f"📝 First 200 chars of OCR: {ocr_text[:200]}...")
        
        # Build the prompt based on document type
        prompt = self._build_extraction_prompt(ocr_text, document_type)
        print(f"\n✉  Prompt Built - Length: {len(prompt)} characters")
        
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
            print(f"\n❌ Groq API Error: {type(e)._name_}: {e}")
            print(f"❌ Full Error: {repr(e)}")
            print("="*80)
            # Return fallback structure
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