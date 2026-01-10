import requests
import json

url = "http://localhost:8000/api/test-llm"
params = {
    "ocr_text": "Patient: John Doe. Diagnosis: Acute Bronchitis. Meds: Amoxicillin 500mg TDS. Advice: Rest for 5 days."
}

try:
    # Check Health
    print("Checking Health...")
    health_res = requests.get("http://localhost:8000/health")
    print("Health Status:")
    print(json.dumps(health_res.json(), indent=2))

    # Test Extraction
    print("\nTesting Extraction...")
    response = requests.post(url, params=params)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
