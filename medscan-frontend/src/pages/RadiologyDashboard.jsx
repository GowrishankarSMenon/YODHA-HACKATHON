import { useState } from 'react';
import { Search, Upload, User, Clipboard, CheckCircle2, AlertCircle, Loader2, FileText, ImageIcon } from 'lucide-react';

export default function RadiologyDashboard() {
    const [uhid, setUhid] = useState('');
    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Lab record form state
    const [photoUrl, setPhotoUrl] = useState('');
    const [reviews, setReviews] = useState('');
    const [uploading, setUploading] = useState(false);

    const API_BASE_URL = 'http://localhost:5000/api';

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!uhid.trim()) return;

        setLoading(true);
        setError('');
        setPatient(null);
        setSuccess('');

        try {
            const response = await fetch(`${API_BASE_URL}/patient/${uhid}`);
            const data = await response.json();

            if (response.ok) {
                setPatient(data);
            } else {
                setError(data.message || 'Patient not found');
            }
        } catch (err) {
            setError('Could not connect to the Radiology API. Make sure it is running on port 5000.');
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!patient || !photoUrl || !reviews) {
            setError('Please search for a patient and fill in all fields.');
            return;
        }

        setUploading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch(`${API_BASE_URL}/lab-records`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    uhid: patient.uhid,
                    file_url: photoUrl,
                    reviews: reviews
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('Lab record uploaded successfully!');
                setPhotoUrl('');
                setReviews('');
            } else {
                setError(data.message || 'Upload failed');
            }
        } catch (err) {
            setError('Error connecting to API. ' + err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans pb-12">
            {/* Navigation Header */}
            <header className="border-b border-slate-800 bg-[#1e293b]/50 backdrop-blur-md sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500 rounded-lg shadow-lg shadow-blue-500/20">
                            <ImageIcon className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                            Radiology Portal
                        </h1>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-slate-400">
                        <span>Connected to EMR</span>
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-6 py-8 max-w-5xl">
                {/* Search Section */}
                <div className="mb-8">
                    <div className="bg-[#1e293b] rounded-2xl border border-slate-800 p-8 shadow-xl">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Search className="w-5 h-5 text-blue-400" />
                            Patient Lookup
                        </h2>
                        <form onSubmit={handleSearch} className="flex gap-3">
                            <input
                                type="text"
                                placeholder="Enter Patient UHID (e.g., UH123456)"
                                value={uhid}
                                onChange={(e) => setUhid(e.target.value)}
                                className="flex-1 bg-[#0f172a] border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-slate-100 placeholder:text-slate-500"
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 shadow-lg shadow-blue-600/20 active:scale-95"
                            >
                                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                                Search
                            </button>
                        </form>
                        {error && (
                            <div className="mt-4 flex items-center gap-2 text-rose-400 bg-rose-400/10 border border-rose-400/20 p-3 rounded-xl text-sm">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                {error}
                            </div>
                        )}
                    </div>
                </div>

                {/* Dashboard Grid */}
                {patient ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Patient Profile Card */}
                        <div className="md:col-span-1 space-y-6">
                            <div className="bg-[#1e293b] rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
                                <div className="h-24 bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center">
                                    <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-full border border-white/30 flex items-center justify-center shadow-inner">
                                        <User className="w-8 h-8 text-white" />
                                    </div>
                                </div>
                                <div className="p-6 text-center">
                                    <h3 className="text-xl font-bold text-white mb-1">{patient.name}</h3>
                                    <p className="text-blue-400 text-sm font-semibold mb-4">{patient.uhid}</p>
                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                        <div className="bg-[#0f172a] p-2 rounded-lg border border-slate-800">
                                            <p className="text-slate-500 text-xs">Age</p>
                                            <p className="font-semibold">{patient.age} Yrs</p>
                                        </div>
                                        <div className="bg-[#0f172a] p-2 rounded-lg border border-slate-800">
                                            <p className="text-slate-500 text-xs">Gender</p>
                                            <p className="font-semibold">{patient.gender}</p>
                                        </div>
                                    </div>
                                    <div className="mt-4 text-left border-t border-slate-800 pt-4 space-y-2">
                                        <div className="flex justify-between items-center text-xs">
                                            <span className="text-slate-500">Phone</span>
                                            <span className="text-slate-300 font-medium">{patient.phone}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-xs">
                                            <span className="text-slate-500">ABHA ID</span>
                                            <span className="text-slate-300 font-medium">{patient.abha_id || 'Not Linked'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-blue-600/10 border border-blue-500/20 rounded-2xl p-6">
                                <h4 className="flex items-center gap-2 text-blue-400 font-semibold mb-2">
                                    <Clipboard className="w-4 h-4" />
                                    Radiology Notice
                                </h4>
                                <p className="text-sm text-slate-400 leading-relaxed italic">
                                    "Ensure all DICOM images are verified before final submission to EMR."
                                </p>
                            </div>
                        </div>

                        {/* Record Upload Section */}
                        <div className="md:col-span-2">
                            <div className="bg-[#1e293b] rounded-2xl border border-slate-800 p-8 shadow-xl h-full">
                                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                    <Upload className="w-6 h-6 text-indigo-400" />
                                    New Lab Record Entry
                                </h2>

                                <form onSubmit={handleUpload} className="space-y-6">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-400 mb-2">
                                            Lab Record Photo URL
                                        </label>
                                        <div className="relative group">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                                                <ImageIcon className="w-5 h-5" />
                                            </div>
                                            <input
                                                type="text"
                                                placeholder="https://cloud.storage.com/record-image.jpg"
                                                value={photoUrl}
                                                onChange={(e) => setPhotoUrl(e.target.value)}
                                                className="w-full bg-[#0f172a] border border-slate-700 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-slate-100 placeholder:text-slate-600"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-slate-400 mb-2">
                                            Radiology Reviews / Findings
                                        </label>
                                        <div className="relative group">
                                            <div className="absolute left-4 top-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                                                <FileText className="w-5 h-5" />
                                            </div>
                                            <textarea
                                                rows="5"
                                                placeholder="Ex: Patient shows mild cardiomegaly but lung fields are clear. No evidence of pneumonia."
                                                value={reviews}
                                                onChange={(e) => setReviews(e.target.value)}
                                                className="w-full bg-[#0f172a] border border-slate-700 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-slate-100 placeholder:text-slate-600 resize-none"
                                            ></textarea>
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={uploading}
                                        className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 disabled:opacity-50 text-white py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-3 shadow-xl shadow-indigo-600/20 active:scale-[0.98]"
                                    >
                                        {uploading ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Submitting to EMR...
                                            </>
                                        ) : (
                                            <>
                                                <CheckCircle2 className="w-5 h-5" />
                                                Submit Radiology Report
                                            </>
                                        )}
                                    </button>

                                    {success && (
                                        <div className="flex items-center gap-3 text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 p-4 rounded-xl animate-in zoom-in-95 duration-300">
                                            <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                                            <div>
                                                <p className="font-bold">Success!</p>
                                                <p className="text-sm opacity-90">{success}</p>
                                            </div>
                                        </div>
                                    )}
                                </form>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-slate-600 border-2 border-dashed border-slate-800 rounded-3xl bg-[#1e293b]/20">
                        <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-4">
                            <User className="w-10 h-10" />
                        </div>
                        <p className="text-lg font-medium">Search for a patient by UHID to begin</p>
                        <p className="text-sm">Radiology records will be linked automatically to the patient profile</p>
                    </div>
                )}
            </main>
        </div>
    );
}
