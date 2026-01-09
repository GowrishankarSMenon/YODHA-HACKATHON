import { AlertTriangle, Activity, Pill, Heart, Info, Sparkles } from 'lucide-react';

/**
 * PatientSummaryCard - Displays AI-generated insights from medical history
 */
export default function PatientSummaryCard({ summary, isLoading, error, onGenerate }) {
    if (isLoading) {
        return (
            <div className="bg-white rounded-xl shadow-lg p-12 animate-pulse overflow-hidden relative">
                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                        <Activity className="w-8 h-8 text-blue-400 animate-bounce" />
                    </div>
                    <div className="h-6 w-48 bg-gray-200 rounded"></div>
                    <div className="h-4 w-64 bg-gray-100 rounded"></div>
                    <div className="mt-8 space-y-3 w-full max-w-md">
                        <div className="h-4 bg-gray-100 rounded w-full"></div>
                        <div className="h-4 bg-gray-100 rounded w-5/6"></div>
                    </div>
                </div>
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-red-900 mb-2">Summary Unavailable</h3>
                <p className="text-red-700">{error}</p>
                <div className="mt-6">
                    <button
                        onClick={onGenerate}
                        className="inline-flex items-center gap-2 px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors shadow-md"
                    >
                        < Sparkles className="w-4 h-4" />
                        Retry Generation
                    </button>
                </div>
                <p className="text-xs text-red-500 mt-4 italic">Check your VITE_GEMINI_API_KEY in the .env file.</p>
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="bg-white rounded-xl shadow-lg p-12 border border-blue-50 relative overflow-hidden group">
                {/* Decorative background elements */}
                <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-50 rounded-full blur-3xl group-hover:bg-blue-100 transition-colors"></div>
                <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-indigo-50 rounded-full blur-3xl group-hover:bg-indigo-100 transition-colors"></div>

                <div className="text-center relative z-10">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl transform group-hover:scale-110 transition-transform duration-500">
                        <Sparkles className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">AI Patient Summary</h3>
                    <p className="text-gray-600 text-lg max-w-md mx-auto mb-8">
                        Generate an intelligent analysis of the patient's entire medical history, identifying key diagnoses and risk factors.
                    </p>
                    <button
                        onClick={onGenerate}
                        className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
                    >
                        <Sparkles className="w-5 h-5" />
                        Generate AI Summary
                    </button>
                    <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-400">
                        <span className="flex items-center gap-1.5"><Heart className="w-4 h-4 text-rose-400" /> Bio-metrics</span>
                        <span className="flex items-center gap-1.5"><Pill className="w-4 h-4 text-blue-400" /> Medications</span>
                        <span className="flex items-center gap-1.5"><Activity className="w-4 h-4 text-emerald-400" /> Diagnoses</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden animate-fade-in border border-blue-50">
            {/* Header Accent */}
            <div className="h-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600"></div>

            <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                            <Heart className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Patient Health Summary</h2>
                            <p className="text-sm text-gray-500">AI-powered analysis of medical history</p>
                        </div>
                    </div>
                    <button
                        onClick={onGenerate}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 font-bold rounded-lg hover:bg-blue-100 transition-all text-sm group"
                    >
                        <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                        Regenerate
                    </button>
                </div>

                {/* Clinical Alerts */}
                {summary.alerts && summary.alerts.length > 0 && (
                    <div className="mb-8 p-5 bg-rose-50 border border-rose-100 rounded-2xl">
                        <div className="flex items-center gap-2 mb-4 text-rose-700 font-bold uppercase tracking-wider text-xs">
                            <AlertTriangle className="w-4 h-4" />
                            Clinical Alerts
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {summary.alerts.map((alert, idx) => (
                                <div key={idx} className="flex items-start gap-2 bg-white/60 p-3 rounded-xl border border-rose-200/50">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0"></div>
                                    <span className="text-sm font-medium text-rose-900">{alert}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Diagnoses & Insight */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    <div className="lg:col-span-1 border-r border-gray-100 pr-4">
                        <div className="flex items-center gap-2 mb-4 text-gray-600 font-bold uppercase tracking-wider text-xs">
                            <Activity className="w-4 h-4" />
                            Key Diagnoses
                        </div>
                        <div className="space-y-2">
                            {summary.diagnoses.map((d, idx) => (
                                <div key={idx} className="bg-slate-50 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-700 shadow-sm">
                                    {d}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="lg:col-span-2">
                        <div className="flex items-center gap-2 mb-4 text-gray-600 font-bold uppercase tracking-wider text-xs">
                            <Info className="w-4 h-4" />
                            Clinical Insight
                        </div>
                        <p className="text-gray-700 leading-relaxed text-lg italic bg-blue-50/30 p-4 rounded-2xl border border-blue-100/30">
                            "{summary.clinicalInsight}"
                        </p>
                    </div>
                </div>

                {/* Medications */}
                <div>
                    <div className="flex items-center gap-2 mb-4 text-gray-600 font-bold uppercase tracking-wider text-xs">
                        <Pill className="w-4 h-4" />
                        Active Medications
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {summary.medications.map((med, idx) => (
                            <div key={idx} className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-2xl p-5 hover:border-blue-400 transition-colors shadow-sm cursor-default">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-slate-900">{med.name}</h4>
                                    <span className="text-[10px] px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-bold uppercase">Rx</span>
                                </div>
                                <div className="text-sm text-slate-600 mb-1 flex items-center gap-1.5">
                                    <Activity className="w-3 h-3 opacity-50" />
                                    {med.dosage} • {med.frequency}
                                </div>
                                <div className="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
                                    Target: {med.purpose}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer Branding */}
            <div className="bg-slate-50 px-8 py-4 flex justify-between items-center border-t border-slate-100">
                <span className="text-[10px] text-slate-400 font-medium">Powered by Google Gemini 2.5 Flash</span>
                <span className="text-[10px] text-gray-400 italic">Medical Information Verification Required</span>
            </div>
        </div>
    );
}
