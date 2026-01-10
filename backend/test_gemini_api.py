"""
Test script to verify Gemini API key is loaded and working
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("GEMINI API KEY DIAGNOSTIC TEST")
print("=" * 60)

# Check if API key is set
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY is NOT set!")
    print("\nPlease add to your .env file:")
    print("GEMINI_API_KEY=your_actual_key_here")
    print("\nGet your key from: https://aistudio.google.com/apikey")
    exit(1)

print(f"✅ GEMINI_API_KEY is set!")
print(f"   Key starts with: {api_key[:10]}...")
print(f"   Key length: {len(api_key)} characters")

# Test if we can import the required libraries
print("\n" + "=" * 60)
print("CHECKING DEPENDENCIES")
print("=" * 60)

try:
    from google import genai
    print("✅ google-genai library is installed")
except ImportError as e:
    print(f"❌ google-genai library not found: {e}")
    print("\nRun: pip install google-genai")
    exit(1)

try:
    from PIL import Image
    print("✅ PIL library is installed")
except ImportError as e:
    print(f"❌ PIL library not found: {e}")
    exit(1)

# Try to initialize Gemini
print("\n" + "=" * 60)
print("TESTING GEMINI API CONNECTION")
print("=" * 60)

try:
    print("→ Initializing Gemini model...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Gemini model initialized successfully!")
    
    # Try a simple test
    print("\n→ Testing API with a simple prompt...")
    response = model.generate_content("Say 'API is working!'")
    print(f"✅ API Response: {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Gemini API is configured correctly.")
    print("The Malayalam OCR should work now.")
    print("\nIf you're still seeing sample text:")
    print("1. Make sure you RESTARTED the server after adding the API key")
    print("2. Check that the Malayalam checkbox is CHECKED")
    print("3. Look at the terminal logs for errors")
    
except Exception as e:
    print(f"\n❌ GEMINI API ERROR: {e}")
    print(f"\nError type: {type(e).__name__}")
    print("\nPossible issues:")
    print("1. API key is invalid")
    print("2. Network connectivity problems")
    print("3. API quota exceeded")
    print("\nPlease check your API key at: https://aistudio.google.com/apikey")
    exit(1)
