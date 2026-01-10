const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');
const path = require('path');
const { decryptPatient, decryptRecord } = require('./encryption');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 5005;

// Middleware
app.use(cors());
app.use(express.json());

// Serve uploaded medical record images
const uploadsPath = '/home/jayadev-narayanan/YODHA-HACKATHON/backend/uploads';
app.use('/uploads', express.static(uploadsPath));
console.log('📁 Serving uploads from:', uploadsPath);

// MongoDB Connection
const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const client = new MongoClient(uri);

let db;

async function connectDB() {
    try {
        await client.connect();
        console.log('✅ Connected to MongoDB');
        db = client.db('medscan');
    } catch (err) {
        console.error('❌ MongoDB Connection Error:', err);
    }
}

connectDB();

// ================================================================
// API ENDPOINTS
// ================================================================

/**
 * GET /api/patients
 * Fetch all patients or search by name
 * Query params: ?search=<name>
 */
app.get('/api/patients', async (req, res) => {
    try {
        const { search } = req.query;

        let query = {};
        if (search) {
            // Case-insensitive search on name field
            query.name = { $regex: search, $options: 'i' };
        }

        const patients = await db.collection('patients')
            .find(query)
            .project({ _id: 0 }) // Exclude MongoDB _id
            .toArray();

        // Decrypt sensitive fields before sending to frontend
        const decryptedPatients = patients.map(p => decryptPatient(p));

        res.json(decryptedPatients);
    } catch (err) {
        console.error('Error fetching patients:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

/**
 * GET /api/patients/:uhid
 * Fetch patient profile by UHID
 */
app.get('/api/patients/:uhid', async (req, res) => {
    try {
        const { uhid } = req.params;
        const patient = await db.collection('patients').findOne(
            { uhid: uhid },
            { projection: { _id: 0 } }
        );

        if (!patient) {
            return res.status(404).json({ error: 'Patient not found' });
        }

        // Decrypt sensitive fields
        const decryptedPatient = decryptPatient(patient);

        res.json(decryptedPatient);
    } catch (err) {
        console.error('Error fetching patient:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

/**
 * GET /api/patients/:uhid/complete
 * Fetch patient profile AND all their medical records in one call
 */
app.get('/api/patients/:uhid/complete', async (req, res) => {
    try {
        const { uhid } = req.params;

        // Fetch patient
        const patient = await db.collection('patients').findOne(
            { uhid: uhid },
            { projection: { _id: 0 } }
        );

        if (!patient) {
            return res.status(404).json({ error: 'Patient not found' });
        }

        // Fetch all records for this patient using their UHID
        const records = await db.collection('records')
            .find({ patient_id: uhid })
            .project({ _id: 0 })
            .toArray();

        // Decrypt sensitive fields
        const decryptedPatient = decryptPatient(patient);
        const decryptedRecords = records.map(r => decryptRecord(r));

        res.json({
            patient: decryptedPatient,
            records: decryptedRecords
        });
    } catch (err) {
        console.error('Error fetching complete patient data:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

/**
 * GET /api/records/:patientId
 * Fetch all medical records for a specific patient
 */
app.get('/api/records/:patientId', async (req, res) => {
    try {
        const { patientId } = req.params;
        const records = await db.collection('records')
            .find({ patient_id: patientId })
            .project({ _id: 0 })
            .toArray();

        // Decrypt sensitive fields
        const decryptedRecords = records.map(r => decryptRecord(r));

        res.json(decryptedRecords);
    } catch (err) {
        console.error('Error fetching records:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Health Check
app.get('/', (req, res) => {
    res.send('MedScan Express API Running');
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        database: db ? 'connected' : 'disconnected',
        timestamp: new Date().toISOString()
    });
});

app.listen(port, () => {
    console.log(`🚀 API Server running on http://localhost:${port}`);
    console.log(`📊 Health check: http://localhost:${port}/health`);
    console.log(`👥 Get all patients: http://localhost:${port}/api/patients`);
    console.log(`🔍 Search patients: http://localhost:${port}/api/patients?search=<name>`);
});
