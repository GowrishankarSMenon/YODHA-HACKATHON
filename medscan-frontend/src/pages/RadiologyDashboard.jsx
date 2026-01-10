import { useState } from 'react';

export default function RadiologyDashboard() {
    const [selectedStudy, setSelectedStudy] = useState(0);

    const studies = [
        { id: 0, name: 'Chest X-Ray', date: 'Apr 12, 2024' },
        { id: 1, name: 'CT Scan Brain', date: 'Apr 05, 2024' },
        { id: 2, name: 'MRI Spine', date: 'Mar 19, 2024' },
        { id: 3, name: 'Ultrasound Abdomen', date: 'Feb 10, 2024' },
    ];

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-blue-600 text-white shadow-md">
                <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-semibold">Radiology & PACS Dashboard</h1>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Search Icon */}
                        <button className="w-9 h-9 bg-blue-500 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </button>
                        {/* Notifications Icon */}
                        <button className="w-9 h-9 bg-blue-500 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                        </button>
                        {/* User Avatar */}
                        <div className="w-9 h-9 bg-blue-800 rounded-full flex items-center justify-center font-semibold">
                            RK
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-12 gap-6">
                    {/* LEFT SIDEBAR - PACS Worklist */}
                    <div className="col-span-3">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 className="text-lg font-semibold text-gray-800 mb-4">PACS Worklist</h2>
                            <div className="space-y-2">
                                {studies.map((study) => (
                                    <label
                                        key={study.id}
                                        className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${selectedStudy === study.id
                                                ? 'bg-blue-50 border-2 border-blue-300'
                                                : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                                            }`}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedStudy === study.id}
                                            onChange={() => setSelectedStudy(study.id)}
                                            className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                        />
                                        <div className="flex-1">
                                            <p className="font-medium text-gray-900 text-sm">{study.name}</p>
                                            <p className="text-xs text-gray-500 mt-0.5">{study.date}</p>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* RIGHT CONTENT PANEL - Imaging Report */}
                    <div className="col-span-9">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
                            <h2 className="text-xl font-semibold text-gray-800 mb-6">
                                Imaging Report: Ravi Kumar
                            </h2>

                            {/* 1. Image Section */}
                            <div className="mb-8">
                                <div className="bg-gray-900 rounded-lg border-2 border-gray-300 p-8 flex items-center justify-center">
                                    <div className="text-center">
                                        <svg className="w-48 h-48 mx-auto text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        <p className="text-gray-400 mt-4 text-sm">Chest X-Ray Image Placeholder</p>
                                    </div>
                                </div>
                            </div>

                            {/* 2. Findings Card */}
                            <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-5">
                                <h3 className="text-base font-semibold text-gray-800 mb-3">Findings:</h3>
                                <ul className="space-y-2 text-gray-700">
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 mt-1">•</span>
                                        <span>Mild Cardiomegaly</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 mt-1">•</span>
                                        <span>Left Basal Infiltrate</span>
                                    </li>
                                </ul>
                            </div>

                            {/* 3. Impression Card */}
                            <div className="mb-8 bg-amber-50 border border-amber-200 rounded-lg p-5">
                                <h3 className="text-base font-semibold text-gray-800 mb-3">Impression:</h3>
                                <ul className="space-y-2 text-gray-700">
                                    <li className="flex items-start gap-2">
                                        <span className="text-amber-600 mt-1">•</span>
                                        <span>Suggestive of Early Pneumonia</span>
                                    </li>
                                </ul>
                            </div>

                            {/* 4. Action Buttons */}
                            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                                <div className="flex gap-3">
                                    <button className="px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">
                                        View DICOM
                                    </button>
                                    <button className="px-5 py-2.5 border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors">
                                        Generate Report
                                    </button>
                                </div>
                                <button className="px-6 py-2.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors shadow-md">
                                    Save & Send to EMR
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
