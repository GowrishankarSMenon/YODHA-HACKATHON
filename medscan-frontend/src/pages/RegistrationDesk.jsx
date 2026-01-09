export default function RegistrationDesk() {
    return (
        <div className="min-h-screen bg-[#f5f7fb] py-8 px-6">
            <div className="max-w-4xl mx-auto">
                {/* Main Card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    {/* Page Title Bar */}
                    <div className="bg-gradient-to-r from-blue-50 to-blue-100 px-8 py-5 border-b border-blue-200">
                        <h1 className="text-2xl font-semibold text-blue-900">Registration Desk</h1>
                    </div>

                    {/* Card Content */}
                    <div className="p-8 space-y-8">
                        {/* 1. Patient Search Section */}
                        <div>
                            <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
                                Patient Search
                            </h2>

                            {/* Search Result Row */}
                            <div className="bg-gray-50 border border-gray-200 rounded-lg px-5 py-4 mb-4 flex items-center justify-between hover:bg-gray-100 transition-colors cursor-pointer">
                                <div className="flex-1">
                                    <p className="text-gray-900 font-medium">
                                        Name: Ravi Kumar | Age: 52 / Male
                                    </p>
                                </div>
                                <div className="text-gray-400">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </div>
                            </div>

                            {/* Patient Details */}
                            <div className="pl-5 space-y-2 text-sm">
                                <div className="flex items-center text-gray-600">
                                    <span className="font-medium w-28">UHID:</span>
                                    <span className="text-gray-900">UH123456</span>
                                </div>
                                <div className="flex items-center text-gray-600">
                                    <span className="font-medium w-28">Phone:</span>
                                    <span className="text-gray-900">9876543210</span>
                                </div>
                                <div className="flex items-center text-gray-600">
                                    <span className="font-medium w-28">Check-in:</span>
                                    <span className="text-gray-900">12-Apr-2022 10:05 AM</span>
                                </div>
                            </div>
                        </div>

                        {/* 2. Upcoming Appointments */}
                        <div className="border-t border-gray-100 pt-6">
                            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                                Upcoming Appointments
                            </h2>
                        </div>

                        {/* 3. Status Section */}
                        <div className="border-t border-gray-100 pt-6 space-y-4">
                            {/* Billing Status */}
                            <div className="flex items-center gap-4 bg-amber-50 border border-amber-200 rounded-lg px-5 py-4">
                                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                                    <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <p className="text-gray-900 font-medium">
                                        Billing Status: <span className="text-amber-700">Pending</span>
                                    </p>
                                </div>
                            </div>

                            {/* ABHA ID Linked */}
                            <div className="flex items-center gap-4 bg-blue-50 border border-blue-200 rounded-lg px-5 py-4">
                                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <p className="text-gray-900 font-medium">
                                        ABHA ID Linked: <span className="text-blue-700">Yes</span>
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* 4. Action Buttons */}
                        <div className="border-t border-gray-100 pt-6 flex justify-end gap-3">
                            <button className="px-6 py-2.5 border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors">
                                New Registration
                            </button>
                            <button className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">
                                Verify Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
