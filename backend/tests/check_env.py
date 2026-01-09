import os
import sys
from dotenv import load_dotenv

print(f"Python executable: {sys.executable}")
print("Loading .env...")
load_dotenv()

key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY present: {bool(key)}")
if key:
    print(f"Key length: {len(key)}")

print("\nAttempting to import groq...")
try:
    import groq
    print(f"✅ groq imported successfully. Version: {getattr(groq, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ groq import failed: {e}")

print("\nAttempting to import GroqService...")
try:
    from ai.groq_service import get_groq_service
    print("✅ GroqService imported")
    try:
        service = get_groq_service()
        print("✅ GroqService instantiated")
    except Exception as e:
        print(f"❌ GroqService instantiation failed: {e}")
except Exception as e:
    print(f"❌ GroqService import failed: {e}")
