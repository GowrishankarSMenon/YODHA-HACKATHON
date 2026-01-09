import React, { useState, useMemo } from 'react';
import Timeline from './Timeline';
import VerificationModal from './VerificationModal';
import TopNavigation from './TopNavigation';
import VitalsChart from './VitalsChart';
import PatientSummaryCard from './PatientSummaryCard';
import { adaptRecord } from './recordAdapter';
import { generatePatientSummary } from '../../services/aiSummaryService';
import { User, Mail, Phone, MapPin, Calendar as CalendarIcon, Activity, Sparkles } from 'lucide-react';

// Mock API data with 3 dummy records
const TEAM_API_DATA = [
    {
        record_id: 'REC001',
        document_type: 'prescription',
        extracted_data: {
            diagnosis: 'Acute upper respiratory tract infection with mild fever',
            medication: 'Amoxicillin 500mg, Paracetamol 650mg',
            dosage: '3 times daily for 5 days',
            notes: 'Patient advised to rest and increase fluid intake'
        },
        confidence_score: 0.92,
        visit_date: '2025-12-15'
    },
    {
        record_id: 'REC002',
        document_type: 'lab_report',
        extracted_data: {
            diagnosis: 'Routine blood work - All parameters within normal range',
            test_type: 'Complete Blood Count (CBC)',
            hemoglobin: '14.2 g/dL',
            wbc_count: '7800 cells/mcL',
            platelet_count: '250000 cells/mcL'
        },
        confidence_score: 0.65,
        visit_date: '2025-11-22'
    },
    {
        record_id: 'REC003',
        document_type: 'consultation_notes',
        extracted_data: {
            diagnosis: 'Type 2 Diabetes Mellitus - controlled with medication',
            chief_complaint: 'Follow-up visit for diabetes management',
            blood_sugar_fasting: '118 mg/dL',
            hba1c: '6.8%',
            treatment_plan: 'Continue Metformin 500mg twice daily, diet control'
        },
        confidence_score: 0.88,
        visit_date: '2026-01-05',
        doctor_name: 'Dr. Priya Sharma'
    }
];

/**
 * DoctorDashboard - Main dashboard component for medical record management
 */
export default function DoctorDashboard() {
    // Process mock data using adaptRecord
    const records = useMemo(() => {
        return TEAM_API_DATA.map(record => adaptRecord(record));
    }, []);

    // State for selected record
    const [selectedRecord, setSelectedRecord] = useState(null);

    // AI Summary State
    const [summary, setSummary] = useState(null);
    const [isSummaryLoading, setIsSummaryLoading] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    // Initial summary generation
    React.useEffect(() => {
        const fetchSummary = async () => {
            if (records.length === 0) return;

            setIsSummaryLoading(true);
            setSummaryError(null);
            try {
                const result = await generatePatientSummary(records);
                setSummary(result);
            } catch (err) {
                console.error("Dashboard Summary Error:", err);
                setSummaryError(err.message);
            } finally {
                setIsSummaryLoading(false);
            }
        };

        fetchSummary();
    }, [records]);

    /**
     * Handle record selection from timeline
     * @param {Object} record - Selected record
     */
    const handleSelectRecord = (record) => {
        setSelectedRecord(record);
    };

    /**
     * Handle modal close
     */
    const handleCloseModal = () => {
        setSelectedRecord(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
            {/* Top Navigation */}
            <TopNavigation />

            {/* Main Content */}
            <div className="max-w-[1920px] mx-auto p-6">
                <div className="grid grid-cols-12 gap-6">
                    {/* Sidebar - Timeline (Col-span-4) */}
                    <div className="col-span-4">
                        <div className="bg-white rounded-xl shadow-lg overflow-hidden h-[calc(100vh-10rem)] sticky top-24">
                            <Timeline records={records} onSelectRecord={handleSelectRecord} />
                        </div>
                    </div>

                    {/* Main Area (Col-span-8) */}
                    <div className="col-span-8 space-y-6">
                        {/* Enhanced Patient Header */}
                        <div className="bg-white rounded-xl shadow-lg p-6 animate-slide-in">
                            <div className="flex items-start gap-6">
                                {/* Patient Avatar */}
                                <div className="relative">
                                    <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl">
                                        <User className="w-12 h-12 text-white" />
                                    </div>
                                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
                                        <div className="w-2 h-2 bg-white rounded-full"></div>
                                    </div>
                                </div>

                                {/* Patient Info */}
                                <div className="flex-1">
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <h1 className="text-3xl font-bold text-gray-900 mb-1">Ravi Kumar</h1>
                                            <p className="text-sm text-gray-500">Patient ID: PAT-2024-1547</p>
                                        </div>
                                        <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold text-sm">
                                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                            Active Patient
                                        </div>
                                    </div>

                                    {/* Patient Details Grid */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="flex items-center gap-3 text-gray-700">
                                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                                <CalendarIcon className="w-5 h-5 text-blue-600" />
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500">Date of Birth</p>
                                                <p className="font-semibold">March 15, 1985</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 text-gray-700">
                                            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                                                <Phone className="w-5 h-5 text-purple-600" />
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500">Phone</p>
                                                <p className="font-semibold">+91 98765 43210</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 text-gray-700">
                                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                                <Mail className="w-5 h-5 text-green-600" />
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500">Email</p>
                                                <p className="font-semibold">ravi.kumar@email.com</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 text-gray-700">
                                            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                                                <MapPin className="w-5 h-5 text-amber-600" />
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500">Location</p>
                                                <p className="font-semibold">Mumbai, India</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Vitals Chart */}
                        <VitalsChart />

                        {/* AI Summary or Record Details */}
                        {!selectedRecord ? (
                            <PatientSummaryCard
                                summary={summary}
                                isLoading={isSummaryLoading}
                                error={summaryError}
                            />
                        ) : (
                            <div className="bg-white rounded-xl shadow-lg p-12 animate-fade-in relative overflow-hidden group">
                                {/* Verification Modal triggers this view - it's handled by selectedRecord state */}
                                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={handleCloseModal}
                                        className="p-2 hover:bg-gray-100 rounded-full text-gray-400 hover:text-gray-600 transition-colors"
                                        title="Back to summary"
                                    >
                                        <Activity className="w-5 h-5" />
                                    </button>
                                </div>
                                <div className="text-center">
                                    <h3 className="text-xl font-bold text-gray-800">Reviewing Extracted Data</h3>
                                    <p className="text-gray-500">Edit or verify the information extracted from the document.</p>
                                </div>
                                {/* The actual detail view would go here if not using a modal */}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Verification Modal */}
            <VerificationModal
                record={selectedRecord}
                isOpen={selectedRecord !== null}
                onClose={handleCloseModal}
            />
        </div>
    );
}
