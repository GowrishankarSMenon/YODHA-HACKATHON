import React, { useState, useMemo } from 'react';
import Timeline from './Timeline';
import VerificationModal from './VerificationModal';
import TopNavigation from './TopNavigation';
import VitalsChart from './VitalsChart';
import { adaptRecord } from './recordAdapter';
import { User, Mail, Phone, MapPin, Calendar as CalendarIcon } from 'lucide-react';

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

                        {/* Empty State / Record Details */}
                        {!selectedRecord && (
                            <div className="bg-white rounded-xl shadow-lg p-12 animate-fade-in">
                                <div className="text-center">
                                    <div className="w-32 h-32 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                        <svg className="w-16 h-16 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-2xl font-bold text-gray-800 mb-3">No Record Selected</h3>
                                    <p className="text-gray-600 text-lg max-w-md mx-auto">
                                        Select a medical record from the timeline to verify AI-extracted data and view detailed information
                                    </p>
                                    <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
                                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                        <span>High confidence records</span>
                                        <div className="w-2 h-2 bg-amber-500 rounded-full ml-4"></div>
                                        <span>Needs review</span>
                                    </div>
                                </div>
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
