import React, { useState, useEffect } from 'react';
import { X, Check, XCircle, AlertCircle, CheckCircle } from 'lucide-react';

/**
 * VerificationModal component for viewing and editing medical record data
 * @param {Object} props
 * @param {Object} props.record - Medical record object
 * @param {boolean} props.isOpen - Whether the modal is open
 * @param {Function} props.onClose - Callback to close the modal
 */
export default function VerificationModal({ record, isOpen, onClose }) {
    const [formData, setFormData] = useState({});
    const [isClosing, setIsClosing] = useState(false);

    // Initialize form data when record changes
    useEffect(() => {
        if (record && record.extracted_data) {
            setFormData({ ...record.extracted_data });
        }
    }, [record]);

    // Reset closing state when modal opens
    useEffect(() => {
        if (isOpen) {
            setIsClosing(false);
        }
    }, [isOpen]);

    // Early return if modal is not open
    if (!isOpen && !isClosing) return null;

    /**
     * Handle input field changes
     * @param {string} key - Field key
     * @param {string} value - New value
     */
    const handleInputChange = (key, value) => {
        setFormData((prev) => ({
            ...prev,
            [key]: value,
        }));
    };

    /**
     * Handle verify and save action
     */
    const handleVerifyAndSave = () => {
        console.log('Saving verified data:', formData);
        handleClose();
    };

    /**
     * Handle close with animation
     */
    const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
            setIsClosing(false);
            onClose();
        }, 300);
    };

    /**
     * Handle backdrop click to close modal
     */
    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    };

    /**
     * Format label from camelCase or snake_case to readable text
     * @param {string} key - Field key
     * @returns {string} Formatted label
     */
    const formatLabel = (key) => {
        return key
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, (str) => str.toUpperCase())
            .trim();
    };

    const isHighConfidence = record?.confidence_score > 0.8;

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center bg-black transition-all duration-300 ${isClosing ? 'bg-opacity-0' : 'bg-opacity-50'
                } backdrop-blur-sm`}
            onClick={handleBackdropClick}
        >
            {/* Modal Container */}
            <div
                className={`w-full h-full max-w-7xl max-h-[95vh] m-4 bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 ${isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'
                    }`}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-8 py-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50">
                    <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center shadow-lg ${isHighConfidence
                                ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                                : 'bg-gradient-to-br from-amber-500 to-orange-600'
                            }`}>
                            {isHighConfidence ? (
                                <CheckCircle className="w-8 h-8 text-white" />
                            ) : (
                                <AlertCircle className="w-8 h-8 text-white" />
                            )}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Verify Medical Record</h2>
                            <p className="text-sm text-gray-600 mt-1 flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${isHighConfidence
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-amber-100 text-amber-700'
                                    }`}>
                                    {Math.round((record?.confidence_score || 0) * 100)}% Confidence
                                </span>
                                <span>•</span>
                                <span>Review and edit the AI-extracted data below</span>
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={handleClose}
                        className="p-2.5 hover:bg-white rounded-xl transition-colors duration-200 group"
                        aria-label="Close modal"
                    >
                        <X className="w-6 h-6 text-gray-600 group-hover:text-gray-900 transition-colors" />
                    </button>
                </div>

                {/* Content Area - Two Columns */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Left Column - Original Scan */}
                    <div className="w-1/2 bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col">
                        <div className="px-8 py-5 border-b border-gray-700">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                Original Scan
                            </h3>
                        </div>
                        <div className="flex-1 overflow-auto p-8 flex items-center justify-center">
                            <img
                                src={record?.file_url}
                                alt="Medical record scan"
                                className="max-w-full max-h-full object-contain rounded-xl shadow-2xl ring-1 ring-white/10"
                            />
                        </div>
                    </div>

                    {/* Right Column - AI Extracted Data */}
                    <div className="w-1/2 bg-white flex flex-col">
                        <div className="px-8 py-5 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                AI Extracted Data
                            </h3>
                            <p className="text-xs text-gray-600 mt-1">
                                Edit any field to correct the extracted information
                            </p>
                        </div>
                        <div className="flex-1 overflow-auto p-8">
                            <form className="space-y-5">
                                {record?.extracted_data &&
                                    Object.entries(record.extracted_data).map(([key, value]) => (
                                        <div key={key} className="group">
                                            <label
                                                htmlFor={key}
                                                className="block text-sm font-semibold text-gray-700 mb-2"
                                            >
                                                {formatLabel(key)}
                                            </label>
                                            <input
                                                id={key}
                                                type="text"
                                                value={formData[key] || ''}
                                                onChange={(e) => handleInputChange(key, e.target.value)}
                                                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white outline-none transition-all duration-200 group-hover:border-gray-300"
                                                placeholder={`Enter ${formatLabel(key).toLowerCase()}`}
                                            />
                                        </div>
                                    ))}

                                {/* Show message if no extracted data */}
                                {(!record?.extracted_data ||
                                    Object.keys(record.extracted_data).length === 0) && (
                                        <div className="text-center py-16 text-gray-500">
                                            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                            <p className="font-medium">No extracted data available</p>
                                            <p className="text-sm mt-1">This record doesn't contain any AI-extracted fields</p>
                                        </div>
                                    )}
                            </form>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-8 py-5 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50">
                    <div className="text-sm text-gray-600">
                        <span className="font-medium">Tip:</span> Review all fields carefully before verifying
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={handleClose}
                            className="flex items-center gap-2 px-6 py-3 text-gray-700 bg-white border-2 border-gray-300 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-semibold shadow-sm"
                        >
                            <XCircle className="w-4 h-4" />
                            Cancel
                        </button>
                        <button
                            onClick={handleVerifyAndSave}
                            className="flex items-center gap-2 px-6 py-3 text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
                        >
                            <Check className="w-4 h-4" />
                            Verify & Save
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
