import React, { useState, useEffect } from 'react';
import { Search, User, Phone, Calendar } from 'lucide-react';

/**
 * PatientSearchSidebar - Searchable patient list for doctor dashboard
 * @param {Array} patients - List of all patients
 * @param {Object} selectedPatient - Currently selected patient
 * @param {Function} onSelectPatient - Callback when patient is clicked
 * @param {Function} onSearch - Callback for search query changes
 * @param {boolean} isLoading - Loading state
 */
export default function PatientSearchSidebar({
    patients = [],
    selectedPatient,
    onSelectPatient,
    onSearch,
    isLoading = false
}) {
    const [searchQuery, setSearchQuery] = useState('');

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (onSearch) {
                onSearch(searchQuery);
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [searchQuery, onSearch]);

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
    };

    return (
        <div className="h-full bg-white border-r border-gray-200 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-bold text-gray-900 mb-3">Patients</h2>

                {/* Search Input */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by name..."
                        value={searchQuery}
                        onChange={handleSearchChange}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                </div>
            </div>

            {/* Patient List */}
            <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                    <div className="p-4 text-center text-gray-500">
                        <div className="animate-pulse space-y-3">
                            {[1, 2, 3, 4, 5].map((i) => (
                                <div key={i} className="h-20 bg-gray-100 rounded-lg"></div>
                            ))}
                        </div>
                    </div>
                ) : patients.length === 0 ? (
                    <div className="p-4 text-center text-gray-500">
                        <User className="w-12 h-12 mx-auto mb-2 opacity-30" />
                        <p className="text-sm">No patients found</p>
                    </div>
                ) : (
                    <div className="p-2 space-y-2">
                        {patients.map((patient) => {
                            const isSelected = selectedPatient?.uhid === patient.uhid;

                            return (
                                <button
                                    key={patient.uhid}
                                    onClick={() => onSelectPatient(patient)}
                                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${isSelected
                                            ? 'bg-blue-50 border-2 border-blue-500 shadow-md'
                                            : 'bg-white border border-gray-200 hover:border-blue-300 hover:shadow-sm'
                                        }`}
                                >
                                    {/* Patient Name & UHID */}
                                    <div className="flex items-start justify-between mb-2">
                                        <div className="flex-1 min-w-0">
                                            <h3 className={`font-semibold truncate ${isSelected ? 'text-blue-900' : 'text-gray-900'
                                                }`}>
                                                {patient.name}
                                            </h3>
                                            <p className="text-xs text-gray-500 truncate">
                                                UHID: {patient.uhid}
                                            </p>
                                        </div>
                                        {isSelected && (
                                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 flex-shrink-0 ml-2"></div>
                                        )}
                                    </div>

                                    {/* Patient Details */}
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-2 text-xs text-gray-600">
                                            <Calendar className="w-3 h-3" />
                                            <span>{patient.age} yrs • {patient.gender}</span>
                                        </div>
                                        {patient.phone && (
                                            <div className="flex items-center gap-2 text-xs text-gray-600">
                                                <Phone className="w-3 h-3" />
                                                <span>{patient.phone}</span>
                                            </div>
                                        )}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-gray-200 bg-gray-50">
                <p className="text-xs text-gray-500 text-center">
                    {patients.length} {patients.length === 1 ? 'patient' : 'patients'}
                </p>
            </div>
        </div>
    );
}
