# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

# Import our other files
from database import database as db
from ai import ai_engine as ai
# Initialize FastAPI app


app = FastAPI()

# Enable CORS (So your Frontend can talk to this Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/")
def home():
    return {"message": "MedScan AI Backend is Running"}

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    p = db.get_patient_by_id(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p

@app.get("/patients/{patient_id}/records")
def get_patient_records(patient_id: str):
    return db.get_records_for_patient(patient_id)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 1. "Save" the file (We just skip saving to disk for MVP speed)
    print(f"Receiving file: {file.filename}")
    
    # 2. Run the Fake AI
    ai_result = ai.extract_data_from_file(file.filename)
    
    # 3. Create the Record in DB
    # Note: In a real app, we'd fuzzy match the name. 
    # Here, we hardcode to 'pat_001' if the AI sees 'Rahul Kumar'
    patient_id = "pat_001" if ai_result["patient_name"] == "Rahul Kumar" else "guest"
    
    new_record = MedicalRecord(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        doc_type=ai_result["doc_type"],
        file_url=f"/uploads/{file.filename}",
        upload_date=datetime.now(),
        status="verified" if ai_result["confidence"] > 0.8 else "flagged",
        confidence_score=ai_result["confidence"],
        extracted_data=ai_result["data"]
    )
    
    db.add_record(new_record)
    
    return {"status": "success", "record_id": new_record.id, "ai_summary": ai_result}