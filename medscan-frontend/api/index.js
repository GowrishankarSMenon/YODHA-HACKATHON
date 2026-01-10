import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/medscan_emr';
mongoose.connect(MONGODB_URI)
    .then(() => console.log('✅ Connected to MongoDB'))
    .catch(err => console.error('❌ MongoDB Connection Error:', err));

// Schemas & Models
const patientSchema = new mongoose.Schema({
    id: { type: String, required: true },
    name: { type: String, required: true },
    age: { type: Number, required: true },
    gender: { type: String, required: true },
    phone: { type: String, required: true },
    abha_id: { type: String, default: null },
    uhid: { type: String, required: true, unique: true }
}, { collection: 'patients' });

const Patient = mongoose.model('Patient', patientSchema);

const medicalRecordSchema = new mongoose.Schema({
    record_id: { type: String, required: true },
    patient_id: { type: String, required: true }, // UHID
    document_type: { type: String, required: true },
    extracted_data: { type: mongoose.Schema.Types.Mixed, default: {} },
    confidence_score: { type: Number, required: true },
    status: { type: String, required: true },
    processed_at: { type: String, required: true },
    file_url: { type: String, default: null }
}, { collection: 'documents' });

const MedicalRecord = mongoose.model('MedicalRecord', medicalRecordSchema);

// Routes

// 1. Search Patient by UHID
app.get('/api/patient/:uhid', async (req, res) => {
    try {
        const { uhid } = req.params;
        const patient = await Patient.findOne({ uhid });

        if (!patient) {
            return res.status(404).json({ message: 'Patient not found' });
        }

        res.json(patient);
    } catch (error) {
        console.error('Error fetching patient:', error);
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

// 2. Upload/Save Lab Record
app.post('/api/lab-records', async (req, res) => {
    try {
        const { uhid, file_url, reviews } = req.body;

        if (!uhid || !file_url || !reviews) {
            return res.status(400).json({ message: 'Missing required fields: uhid, file_url, and reviews are required.' });
        }

        // Verify patient exists
        const patient = await Patient.findOne({ uhid });
        if (!patient) {
            return res.status(404).json({ message: 'Patient not found. Cannnot upload record for non-existent patient.' });
        }

        const record_id = `rec_${Math.random().toString(36).substr(2, 8)}`;

        const newRecord = new MedicalRecord({
            record_id,
            patient_id: uhid,
            document_type: 'LAB_REPORT',
            extracted_data: { reviews }, // Storing reviews in extracted_data as requested
            confidence_score: 1.0, // Manual upload gets 1.0
            status: 'AUTO_APPROVED',
            processed_at: new Date().toISOString() + 'Z',
            file_url
        });

        await newRecord.save();

        res.status(201).json({
            message: 'Lab record saved successfully',
            record_id: newRecord.record_id,
            patient_name: patient.name
        });
    } catch (error) {
        console.error('Error saving lab record:', error);
        res.status(500).json({ message: 'Server error', error: error.message });
    }
});

// Root route
app.get('/', (req, res) => {
    res.json({ message: 'Radiology Dashboard API is running' });
});

// Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});
