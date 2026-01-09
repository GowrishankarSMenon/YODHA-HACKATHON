import requests
import time

print("Testing server health...")
time.sleep(2)  # Wait for server to start

try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Server is running!")
        print(f"   Status: {data.get('status')}")
        print(f"   OCR Available: {data.get('ocr_available')}")
        print(f"   Groq Available: {data.get('groq_available')}")
        print(f"   Groq Enabled: {data.get('groq_enabled')}")
        print(f"   Extraction Method: {data.get('extraction_method')}")
        print(f"\n✅ Auto-reload disabled: Check for NO reload warnings")
        print(f"\n🌐 Open http://localhost:8000 to test document upload")
    else:
        print(f"❌ Server returned status {response.status_code}")
except Exception as e:
    print(f"❌ Server not responding: {e}")
    print("\nMake sure server is running with: python main.py")
