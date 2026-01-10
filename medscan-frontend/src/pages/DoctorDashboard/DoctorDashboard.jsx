import React, { useState, useEffect } from 'react';
import Timeline from './Timeline';
import VerificationModal from './VerificationModal';
import TopNavigation from './TopNavigation';
import VitalsChart from './VitalsChart';
import PatientSummaryCard from './PatientSummaryCard';
import PatientSearchSidebar from './PatientSearchSidebar';
import { adaptRecord } from './recordAdapter';
import { generatePatientSummary } from '../../services/aiSummaryService';
import { User, Mail, Phone, MapPin, Calendar as CalendarIcon, Activity, Menu, X } from 'lucide-react';

/**
 * DoctorDashboard - Main dashboard component for medical record management
 * Now with patient search and selection capabilities
 */
export default function DoctorDashboard() {
    // Sidebar State
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    // Patient List State
    const [allPatients, setAllPatients] = useState([]);
    const [filteredPatients, setFilteredPatients] = useState([]);
    const [isPatientsLoading, setIsPatientsLoading] = useState(true);

    // Selected Patient State
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [patientRecords, setPatientRecords] = useState([]);
    const [isDataLoading, setIsDataLoading] = useState(false);
    const [dataError, setDataError] = useState(null);

    // Selected Record State (for modal)
    const [selectedRecord, setSelectedRecord] = useState(null);

    // AI Summary State
    const [summary, setSummary] = useState(null);
    const [isSummaryLoading, setIsSummaryLoading] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    /**
     * Fetch all patients on component mount
     */
    useEffect(() => {
        const fetchPatients = async () => {
            setIsPatientsLoading(true);
            try {
                const response = await fetch('http://localhost:5005/api/patients');
                if (!response.ok) throw new Error('Failed to fetch patients');
                const data = await response.json();
                setAllPatients(data);
                setFilteredPatients(data);
            } catch (err) {
                console.error('Error fetching patients:', err);
            } finally {
                setIsPatientsLoading(false);
            }
        };

        fetchPatients();
    }, []);

    /**
     * Handle patient search
     */
    const handleSearch = async (query) => {
        if (!query.trim()) {
            setFilteredPatients(allPatients);
            return;
        }

        try {
            const response = await fetch(`http://localhost:5005/api/patients?search=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            setFilteredPatients(data);
        } catch (err) {
            console.error('Search error:', err);
            // Fallback to client-side filtering
            const filtered = allPatients.filter(p =>
                p.name.toLowerCase().includes(query.toLowerCase())
            );
            setFilteredPatients(filtered);
        }
    };

    /**
     * Handle patient selection
     * Fetches complete patient data (profile + records)
     */
    const handleSelectPatient = async (patient) => {
        setSelectedPatient(patient);
        setIsDataLoading(true);
        setDataError(null);
        setSummary(null); // Clear previous summary

        try {
            // Fetch complete patient data (profile + records)
            const response = await fetch(`http://localhost:5005/api/patients/${patient.uhid}/complete`);
            if (!response.ok) throw new Error('Failed to fetch patient data');
            const data = await response.json();

            // Adapt records for UI
            const adaptedRecords = data.records.map(record => adaptRecord(record));
            setPatientRecords(adaptedRecords);
        } catch (err) {
            console.error('Error fetching patient data:', err);
            setDataError(err.message);
        } finally {
            setIsDataLoading(false);
        }
    };

    /**
     * Generate AI summary for patient records
     */
    const generateSummaryForPatient = async (records) => {
        setIsSummaryLoading(true);
        setSummaryError(null);
        try {
            const result = await generatePatientSummary(records);
            setSummary(result);
        } catch (err) {
            console.error('AI Summary Error:', err);
            setSummaryError(err.message);
        } finally {
            setIsSummaryLoading(false);
        }
    };

    /**
     * Handle manual summary regeneration
     */
    const handleRegenerateSummary = () => {
        if (patientRecords.length > 0) {
            generateSummaryForPatient(patientRecords);
        }
    };

    /**
     * Handle record selection from timeline
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

            {/* Main Content with Sidebar */}
            <div className="flex h-[calc(100vh-4rem)] relative">
                {/* Left Sidebar - Patient Search (Sliding) */}
                <div
                    className={`absolute left-0 top-0 h-full w-80 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out z-20 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                        }`}
                >
                    <PatientSearchSidebar
                        patients={filteredPatients}
                        selectedPatient={selectedPatient}
                        onSelectPatient={handleSelectPatient}
                        onSearch={handleSearch}
                        isLoading={isPatientsLoading}
                    />
                </div>

                {/* Sidebar Toggle Button */}
                <button
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className={`fixed top-20 z-30 bg-blue-600 text-white p-3 rounded-r-lg shadow-lg hover:bg-blue-700 transition-all duration-300 ${isSidebarOpen ? 'left-80' : 'left-0'
                        }`}
                    title={isSidebarOpen ? 'Hide patient list' : 'Show patient list'}
                >
                    {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>

                {/* Main Dashboard Area */}
                <div className={`flex-1 overflow-hidden transition-all duration-300 ${isSidebarOpen ? 'ml-80' : 'ml-0'
                    }`}>
                    {!selectedPatient ? (
                        // Empty State - No Patient Selected
                        <div className="h-full flex items-center justify-center p-12">
                            <div className="text-center max-w-md">
                                <User className="w-20 h-20 mx-auto mb-4 text-gray-300" />
                                <h2 className="text-2xl font-bold text-gray-700 mb-2">
                                    Select a Patient
                                </h2>
                                <p className="text-gray-500">
                                    Choose a patient from the sidebar to view their medical records and AI-generated health summary.
                                </p>
                            </div>
                        </div>
                    ) : (
                        // Patient Selected - Show Dashboard
                        <div className="h-full overflow-y-auto p-6">
                            <div className="max-w-[1920px] mx-auto">
                                <div className="grid grid-cols-12 gap-6">
                                    {/* Left Column - Timeline (Col-span-4) */}
                                    <div className="col-span-4">
                                        <div className="bg-white rounded-xl shadow-lg overflow-hidden h-[calc(100vh-10rem)] sticky top-6">
                                            <Timeline
                                                records={patientRecords}
                                                onSelectRecord={handleSelectRecord}
                                            />
                                        </div>
                                    </div>

                                    {/* Right Column - Patient Info & Summary (Col-span-8) */}
                                    <div className="col-span-8 space-y-6">
                                        {/* Patient Header */}
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
                                                            <h1 className="text-3xl font-bold text-gray-900 mb-1">
                                                                {selectedPatient.name}
                                                            </h1>
                                                            <p className="text-sm text-gray-500">
                                                                UHID: {selectedPatient.uhid}
                                                            </p>
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
                                                                <p className="text-xs text-gray-500">Age / Gender</p>
                                                                <p className="font-semibold">
                                                                    {selectedPatient.age} / {selectedPatient.gender}
                                                                </p>
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-3 text-gray-700">
                                                            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                                                                <Phone className="w-5 h-5 text-purple-600" />
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500">Phone</p>
                                                                <p className="font-semibold">{selectedPatient.phone}</p>
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-3 text-gray-700">
                                                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                                                <Mail className="w-5 h-5 text-green-600" />
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500">ABHA ID</p>
                                                                <p className="font-semibold">{selectedPatient.abha_id || '--'}</p>
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-3 text-gray-700">
                                                            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                                                                <MapPin className="w-5 h-5 text-amber-600" />
                                                            </div>
                                                            <div>
                                                                <p className="text-xs text-gray-500">Location</p>
                                                                <p className="font-semibold">Local Database</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Vitals Chart */}
                                        <VitalsChart records={patientRecords} />

                                        {/* AI Summary or Record Details */}
                                        {!selectedRecord ? (
                                            <PatientSummaryCard
                                                summary={summary}
                                                isLoading={isSummaryLoading}
                                                error={summaryError}
                                                onGenerate={handleRegenerateSummary}
                                            />
                                        ) : (
                                            <div className="bg-white rounded-xl shadow-lg p-12 animate-fade-in relative overflow-hidden group">
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
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
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
