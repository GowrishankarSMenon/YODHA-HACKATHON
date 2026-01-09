"""
Test script for Groq Qwen LLM integration
Run this to verify that your Groq API key is working correctly.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.groq_service import get_groq_service, GroqService
from ai.llm_extractor import LLMExtractor
import json

def test_groq_connection():
    """Test basic Groq API connection."""
    print("=" * 60)
    print("TEST 1: Groq API Connection")
    print("=" * 60)
    
    try:
        groq_service = get_groq_service()
        success = groq_service.test_connection()
        
        if success:
            print("✅ Groq API connection successful!")
            print(f"   Model: {groq_service.model}")
            print(f"   Temperature: {groq_service.temperature}")
            return True
        else:
            print("❌ Groq API connection failed!")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Groq: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Created a .env file in the backend directory")
        print("   2. Added GROQ_API_KEY=your_key_here to the .env file")
        print("   3. Get your API key from: https://console.groq.com/keys")
        return False

def test_key_value_extraction():
    """Test key-value extraction with sample medical document."""
    print("\n" + "=" * 60)
    print("TEST 2: Key-Value Extraction from Sample Lab Report")
    print("=" * 60)
    
    # Sample lab report OCR text
    sample_ocr = """MAX SUPER SPECIALITY HOSPITAL
Laboratory Report

Report Date: 07-Jan-2026
Sample Collected: 06-Jan-2026 08:30 AM

PATIENT INFORMATION:
Name: Priya Sharma
UHID: HOSP-2025-002
Age: 32 years | Gender: Female
Referring Doctor: Dr. Mehta

TEST: COMPLETE BLOOD COUNT (CBC)

RESULTS:
Hemoglobin: 11.2 g/dL (Normal: 12-15 g/dL) LOW
WBC Count: 8,500 cells/cumm (Normal: 4000-11000)
RBC Count: 4.2 million/cumm (Normal: 4.5-5.5)
Platelet Count: 2.5 lakh/cumm (Normal: 1.5-4.5 lakh)
ESR: 28 mm/hr (Normal: 0-20) HIGH

DIFFERENTIAL COUNT:
Neutrophils: 62% (Normal: 40-75%)
Lymphocytes: 30% (Normal: 20-45%)
Monocytes: 6% (Normal: 2-10%)
Eosinophils: 2% (Normal: 1-6%)

REMARKS:
Mild anemia detected. Iron supplementation recommended.
Slightly elevated ESR may indicate inflammation.

Lab Technician: Ramesh K.
Pathologist: Dr. Gupta MD
Lab No: LAB/2026/00234
"""
    
    try:
        # Extract using Groq
        print("\n📤 Sending OCR text to Groq Qwen model...")
        extracted_data = LLMExtractor.extract_structured_data(
            sample_ocr, 
            document_type="LAB_REPORT"
        )
        
        print("\n✅ Extraction successful!")
        print("\n📊 Extracted Key-Value Pairs:")
        print("-" * 60)
        print(json.dumps(extracted_data, indent=2))
        
        # Calculate confidence
        confidence = LLMExtractor.calculate_confidence(extracted_data, "LAB_REPORT")
        status = LLMExtractor.determine_status(confidence)
        
        print("\n" + "-" * 60)
        print(f"   Confidence Score: {confidence:.2f}")
        print(f"   Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        return False

def test_fallback_mechanism():
    """Test that fallback to regex works."""
    print("\n" + "=" * 60)
    print("TEST 3: Fallback Mechanism (Force Regex)")
    print("=" * 60)
    
    sample_ocr = """UHID: TEST-001
Diagnosis: Test Condition
Blood Pressure: 120/80
"""
    
    try:
        # Force use of regex (not Groq)
        extracted_data = LLMExtractor.extract_structured_data(
            sample_ocr,
            document_type="OPD_NOTE",
            use_groq=False  # Force regex
        )
        
        print("✅ Regex fallback working!")
        print("\n📊 Extracted Data (Regex Method):")
        print(json.dumps(extracted_data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("   GROQ QWEN LLM INTEGRATION TEST SUITE")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection Test", test_groq_connection()))
    
    # Test 2: Extraction (only if connection works)
    if results[0][1]:
        results.append(("Key-Value Extraction", test_key_value_extraction()))
    else:
        print("\n⏭️  Skipping extraction test (API not connected)")
        results.append(("Key-Value Extraction", False))
    
    # Test 3: Fallback
    results.append(("Fallback Mechanism", test_fallback_mechanism()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\n{total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed! Your Groq integration is working perfectly!")
    elif results[0][1]:  # Connection works
        print("\n⚠️  Some tests failed, but Groq connection is working.")
    else:
        print("\n❌ Groq API not connected. Please check your .env file.")
        print("\n📖 See GROQ_SETUP.md for setup instructions.")

if __name__ == "__main__":
    main()
