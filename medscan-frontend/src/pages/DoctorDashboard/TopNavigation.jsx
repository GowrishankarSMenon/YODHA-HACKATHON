import React, { useState } from 'react';
import { Search, Filter, Bell, User, ChevronDown } from 'lucide-react';

/**
 * TopNavigation component with search, filters, and user menu
 */
export default function TopNavigation() {
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState('all');

    const filters = [
        { id: 'all', label: 'All Records' },
        { id: 'prescription', label: 'Prescriptions' },
        { id: 'lab_report', label: 'Lab Reports' },
        { id: 'consultation', label: 'Consultations' },
    ];

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
            <div className="max-w-[1920px] mx-auto px-6 py-4">
                <div className="flex items-center justify-between gap-6">
                    {/* Logo and Brand */}
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">MediTrack</h1>
                            <p className="text-xs text-gray-500">Medical Records System</p>
                        </div>
                    </div>

                    {/* Search Bar */}
                    <div className="flex-1 max-w-2xl">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search records, diagnoses, medications..."
                                className="w-full pl-11 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>
                    </div>

                    {/* Filter Buttons */}
                    <div className="flex items-center gap-2">
                        {filters.map((filter) => (
                            <button
                                key={filter.id}
                                onClick={() => setActiveFilter(filter.id)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeFilter === filter.id
                                        ? 'bg-blue-600 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {filter.label}
                            </button>
                        ))}
                    </div>

                    {/* Right Actions */}
                    <div className="flex items-center gap-3">
                        {/* Notifications */}
                        <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                        </button>

                        {/* User Menu */}
                        <div className="flex items-center gap-2 pl-3 border-l border-gray-200">
                            <div className="text-right">
                                <p className="text-sm font-medium text-gray-900">Dr. Sarah Chen</p>
                                <p className="text-xs text-gray-500">Cardiologist</p>
                            </div>
                            <button className="flex items-center gap-1 p-1 hover:bg-gray-100 rounded-lg transition-colors">
                                <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                                    <User className="w-5 h-5 text-white" />
                                </div>
                                <ChevronDown className="w-4 h-4 text-gray-500" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
