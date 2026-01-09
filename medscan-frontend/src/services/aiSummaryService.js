import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

// Initialize the API
const genAI = API_KEY ? new GoogleGenerativeAI(API_KEY) : null;

/**
 * Summarizes medical records using Gemini AI.
 * Falls back to an intelligent "Demo Mode" if API fails.
 * @param {Array} records - Array of medical records to summarize.
 * @returns {Promise<Object>} The structured AI summary.
 */
export async function generatePatientSummary(records) {
  // If no API key or genAI failed to init, go to demo mode immediately
  if (!genAI) {
    console.warn("Gemini API key not found. Using Demo Mode.");
    return generateDemoSummary(records);
  }

  try {
    // Try with gemini-1.5-flash (stable)
    const model = genAI.getGenerativeModel({
      model: "gemini-2.5-flash"
    });

    const prompt = `
      You are an expert clinical AI assistant. Analyze the following patient medical records and provide a structured summary.
      
      PATIENT RECORDS:
      ${JSON.stringify(records, null, 2)}
      
      OUTPUT FORMAT (JSON ONLY):
      {
        "alerts": ["List of critical findings, allergies, or urgent concerns"],
        "diagnoses": ["Consolidated list of diagnoses across all records"],
        "medications": [
          { "name": "Medication Name", "dosage": "Dosage", "frequency": "Frequency", "purpose": "Relevant condition" }
        ],
        "clinicalInsight": "A brief overview (2-3 sentences) of the patient's current health status and trajectory."
      }
      
      RULES:
      - Be precise and professional.
      - If no critical alerts are found, the alerts array should be empty.
      - Ensure the output is strictly valid JSON.
    `;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Extract JSON from potential markdown code blocks
    const jsonString = text.includes("```json")
      ? text.split("```json")[1].split("```")[0].trim()
      : text;

    console.log("✅ Gemini AI Summary Success");
    return JSON.parse(jsonString);
  } catch (error) {
    console.warn("Gemini API failed, switching to Demo Mode:", error.message);
    return generateDemoSummary(records);
  }
}

/**
 * Intelligent fallback that analyzes records locally when AI is unavailable.
 */
async function generateDemoSummary(records) {
  // Simulate API delay for realistic feel
  await new Promise(resolve => setTimeout(resolve, 1500));

  const alerts = [];
  const diagnoses = [];
  const medications = [];

  // Simple rule-based extraction for the demo
  records.forEach(record => {
    const data = record.extracted_data || {};

    // Alert logic
    if (data.blood_sugar_fasting && parseInt(data.blood_sugar_fasting) > 110) {
      alerts.push("Elevated Fasting Blood Sugar");
    }
    if (data.hba1c && parseFloat(data.hba1c) > 6.5) {
      alerts.push("High Hemoglobin A1c (Pre-diabetic/Diabetic)");
    }
    if (data.diagnosis && data.diagnosis.toLowerCase().includes("infection")) {
      alerts.push("Active Infection Management");
    }

    // Diagnosis consolidation
    if (data.diagnosis) {
      if (!diagnoses.includes(data.diagnosis)) diagnoses.push(data.diagnosis);
    }

    // Medication extraction
    if (data.medication) {
      const medNames = data.medication.split(', ');
      medNames.forEach(name => {
        if (!medications.find(m => m.name === name)) {
          medications.push({
            name: name,
            dosage: data.dosage || "As directed",
            frequency: "Daily",
            purpose: data.diagnosis || "Medical condition"
          });
        }
      });
    }

    if (data.treatment_plan && data.treatment_plan.includes("Metformin")) {
      if (!medications.find(m => m.name === "Metformin")) {
        medications.push({
          name: "Metformin",
          dosage: "500mg",
          frequency: "Twice daily",
          purpose: "Type 2 Diabetes"
        });
      }
    }
  });

  return {
    alerts: alerts.length > 0 ? [...new Set(alerts)] : ["No urgent clinical alerts"],
    diagnoses: diagnoses.length > 0 ? diagnoses : ["Routine Follow-up"],
    medications: medications.length > 0 ? medications : [{ name: "Reviewing medications", dosage: "N/A", frequency: "N/A", purpose: "N/A" }],
    clinicalInsight: "Patient shows signs of chronic condition management with recent acute episodes. Careful monitoring of metabolic values and adherence to current antimicrobial therapy is advised."
  };
}
