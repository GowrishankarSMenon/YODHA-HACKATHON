import React from 'react';
import { Calendar, FileText, Activity, Pill, FlaskConical, Stethoscope, Download, Share2, Eye } from 'lucide-react';

/**
 * Timeline component that displays medical records in chronological order
 * @param {Object} props
 * @param {Array} props.records - Array of medical records
 * @param {Function} props.onSelectRecord - Callback when a record is clicked
 */
export default function Timeline({ records = [], onSelectRecord }) {
    // Sort records by visit_date (newest first)
    const sortedRecords = [...records].sort((a, b) => {
        const dateA = new Date(a.visit_date);
        const dateB = new Date(b.visit_date);
        return dateB - dateA;
    });

    /**
     * Format date to a readable format with relative time
     * @param {string} dateString - Date in YYYY-MM-DD format
     * @returns {string} Formatted date
     */
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        const formattedDate = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });

        if (diffDays === 0) return `Today • ${formattedDate}`;
        if (diffDays === 1) return `Yesterday • ${formattedDate}`;
        if (diffDays < 7) return `${diffDays} days ago • ${formattedDate}`;
        return formattedDate;
    };

    /**
     * Get icon for document type
     */
    const getDocumentIcon = (type) => {
        switch (type) {
            case 'prescription':
                return Pill;
            case 'lab_report':
                return FlaskConical;
            case 'consultation_notes':
                return Stethoscope;
            default:
                return FileText;
        }
    };

    /**
     * Get diagnosis snippet from extracted_data
     * @param {Object} extractedData
     * @returns {string} Diagnosis snippet
     */
    const getDiagnosisSnippet = (extractedData) => {
        if (!extractedData) return 'No diagnosis available';

        const diagnosis = extractedData.diagnosis || extractedData.summary || extractedData.notes || '';

        if (typeof diagnosis === 'string') {
            return diagnosis.length > 100
                ? diagnosis.substring(0, 100) + '...'
                : diagnosis || 'No diagnosis available';
        }

        return 'No diagnosis available';
    };

    /**
     * Get confidence badge text
     * @param {number} score - Confidence score (0-1)
     * @returns {string} Badge text
     */
    const getConfidenceBadge = (score) => {
        const percentage = Math.round(score * 100);
        return `${percentage}% AI Match`;
    };

    return (
        <div className="w-full h-full flex flex-col bg-gradient-to-br from-gray-50 to-white">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 bg-white">
                <div className="flex items-center gap-3 mb-2">
                    <Activity className="w-6 h-6 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-800">Medical Timeline</h2>
                </div>
                <p className="text-sm text-gray-500">
                    {sortedRecords.length} {sortedRecords.length === 1 ? 'record' : 'records'} found
                </p>
            </div>

            {/* Timeline Content */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="relative">
                    {/* Vertical line */}
                    <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-200 via-indigo-200 to-transparent"></div>

                    {/* Timeline items */}
                    <div className="space-y-4">
                        {sortedRecords.length === 0 ? (
                            <div className="text-center py-12 text-gray-500 animate-fade-in">
                                <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                <p className="font-medium">No records found</p>
                                <p className="text-sm mt-1">Medical records will appear here</p>
                            </div>
                        ) : (
                            sortedRecords.map((record, index) => {
                                const isHighConfidence = record.confidence_score > 0.8;
                                const DocIcon = getDocumentIcon(record.document_type);

                                return (
                                    <div
                                        key={record.record_id}
                                        className="relative pl-14 animate-slide-in"
                                        style={{ animationDelay: `${index * 50}ms` }}
                                    >
                                        {/* Colored dot indicator with pulse */}
                                        <div className="absolute left-3.5 top-7 z-10">
                                            <div
                                                className={`w-4 h-4 rounded-full border-4 border-white shadow-lg ${isHighConfidence ? 'bg-green-500' : 'bg-amber-500'
                                                    }`}
                                            ></div>
                                            {index === 0 && (
                                                <div
                                                    className={`absolute inset-0 w-4 h-4 rounded-full animate-pulse ${isHighConfidence ? 'bg-green-400' : 'bg-amber-400'
                                                        } opacity-75`}
                                                ></div>
                                            )}
                                        </div>

                                        {/* Card */}
                                        <div
                                            onClick={() => onSelectRecord(record)}
                                            className="bg-white rounded-xl shadow-md hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] cursor-pointer border border-gray-100 overflow-hidden group"
                                        >
                                            {/* Card Header with Icon */}
                                            <div className="p-5 pb-4">
                                                <div className="flex items-start gap-4">
                                                    {/* Document Icon */}
                                                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform ${isHighConfidence
                                                            ? 'bg-gradient-to-br from-blue-500 to-indigo-600'
                                                            : 'bg-gradient-to-br from-amber-500 to-orange-600'
                                                        }`}>
                                                        <DocIcon className="w-6 h-6 text-white" />
                                                    </div>

                                                    {/* Content */}
                                                    <div className="flex-1 min-w-0">
                                                        {/* Title and Badge */}
                                                        <div className="flex items-start justify-between gap-2 mb-2">
                                                            <h3 className="text-lg font-bold text-gray-900 capitalize group-hover:text-blue-600 transition-colors">
                                                                {record.document_type.replace(/_/g, ' ')}
                                                            </h3>

                                                            {/* Confidence badge */}
                                                            <span
                                                                className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${isHighConfidence
                                                                        ? 'bg-green-100 text-green-700 ring-1 ring-green-200'
                                                                        : 'bg-amber-100 text-amber-700 ring-1 ring-amber-200'
                                                                    }`}
                                                            >
                                                                {getConfidenceBadge(record.confidence_score)}
                                                            </span>
                                                        </div>

                                                        {/* Date */}
                                                        <div className="flex items-center gap-2 text-gray-600 mb-3">
                                                            <Calendar className="w-4 h-4" />
                                                            <span className="text-sm font-medium">
                                                                {formatDate(record.visit_date)}
                                                            </span>
                                                        </div>

                                                        {/* Diagnosis snippet */}
                                                        <p className="text-gray-700 text-sm leading-relaxed mb-3">
                                                            {getDiagnosisSnippet(record.extracted_data)}
                                                        </p>

                                                        {/* Doctor name */}
                                                        {record.doctor_name && (
                                                            <div className="flex items-center gap-2 text-xs text-gray-500">
                                                                <Stethoscope className="w-3 h-3" />
                                                                <span>{record.doctor_name}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Card Footer with Actions */}
                                            <div className="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onSelectRecord(record);
                                                        }}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                    >
                                                        <Eye className="w-3.5 h-3.5" />
                                                        View Details
                                                    </button>
                                                    <button
                                                        onClick={(e) => e.stopPropagation()}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                                    >
                                                        <Download className="w-3.5 h-3.5" />
                                                        Download
                                                    </button>
                                                    <button
                                                        onClick={(e) => e.stopPropagation()}
                                                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                                    >
                                                        <Share2 className="w-3.5 h-3.5" />
                                                        Share
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
