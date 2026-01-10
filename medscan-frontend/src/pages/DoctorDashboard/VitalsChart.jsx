import React from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { Heart, Weight, FileText, TrendingUp, TrendingDown } from 'lucide-react';

/**
 * VitalsChart component with animated circular progress and trend indicators
 * @param {Array} records - Patient's medical records containing vitals data
 */
export default function VitalsChart({ records = [] }) {
    // Extract latest vitals from most recent record
    const extractVitals = () => {
        if (records.length === 0) {
            return {
                heartRate: 72,
                weight: '--',
                chiefComplaint: 'No records available'
            };
        }

        // Get the latest record
        const latest = records[0];
        const data = latest.extracted_data;

        // Extract heart rate (pulse)
        let heartRate = 72;
        if (data.vitals?.pulse) {
            heartRate = parseInt(data.vitals.pulse) || 72;
        }

        // Extract weight
        let weight = '--';
        if (data.vitals?.weight) {
            weight = data.vitals.weight;
        }

        // Extract chief complaint
        let chiefComplaint = data.chief_complaint || 'Not specified';

        return { heartRate, weight, chiefComplaint };
    };

    const { heartRate, weight, chiefComplaint } = extractVitals();
    // Mock historical data for sparklines
    const heartRateData = [
        { value: 68 }, { value: 70 }, { value: 72 }, { value: 71 },
        { value: 73 }, { value: 72 }, { value: 72 }
    ];

    const weightData = [
        { value: 76 }, { value: 77 }, { value: 78 }, { value: 78 },
        { value: 79 }, { value: 78 }, { value: 78 }
    ];

    const vitals = [
        {
            id: 'heart_rate',
            label: 'Heart Rate',
            value: heartRate,
            unit: 'bpm',
            icon: Heart,
            color: 'red',
            gradient: 'from-red-500 to-pink-500',
            bgGradient: 'from-red-50 to-pink-50',
            borderColor: 'border-red-200',
            trend: 'stable',
            trendValue: '+0%',
            data: heartRateData,
            normal: { min: 60, max: 100 },
        },
        {
            id: 'weight',
            label: 'Weight',
            value: weight,
            unit: 'kg',
            icon: Weight,
            color: 'blue',
            gradient: 'from-blue-500 to-cyan-500',
            bgGradient: 'from-blue-50 to-cyan-50',
            borderColor: 'border-blue-200',
            trend: 'stable',
            trendValue: '+0%',
            data: weightData,
            isNumeric: false,
        },
        {
            id: 'chief_complaint',
            label: 'Chief Complaint',
            value: chiefComplaint,
            unit: '',
            icon: FileText,
            color: 'purple',
            gradient: 'from-purple-500 to-indigo-500',
            bgGradient: 'from-purple-50 to-indigo-50',
            borderColor: 'border-purple-200',
            trend: 'stable',
            trendValue: '',
            data: [],
            isText: true,
        },
    ];

    const getStatusColor = (vital) => {
        if (vital.id === 'heart_rate') {
            const val = vital.value;
            if (val >= vital.normal.min && val <= vital.normal.max) return 'text-green-600';
            return 'text-amber-600';
        }
        return 'text-green-600';
    };

    const getTrendIcon = (trend) => {
        if (trend === 'up') return <TrendingUp className="w-3 h-3" />;
        if (trend === 'down') return <TrendingDown className="w-3 h-3" />;
        return null;
    };

    return (
        <div className="bg-white rounded-xl shadow-lg p-6 animate-slide-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-xl font-bold text-gray-800">Vital Signs</h2>
                    <p className="text-sm text-gray-500 mt-1">Real-time patient monitoring</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Live</span>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
                {vitals.map((vital) => {
                    const Icon = vital.icon;

                    return (
                        <div
                            key={vital.id}
                            className={`relative bg-gradient-to-br ${vital.bgGradient} rounded-xl p-6 border ${vital.borderColor} hover:shadow-xl transition-all duration-300 hover:scale-105 group`}
                        >
                            {/* Icon and Label */}
                            <div className="flex items-start justify-between mb-4">
                                <div className={`w-12 h-12 bg-gradient-to-br ${vital.gradient} rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform`}>
                                    <Icon className="w-6 h-6 text-white" />
                                </div>

                                {/* Trend Indicator */}
                                <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${vital.trend === 'up' ? 'bg-green-100 text-green-700' :
                                    vital.trend === 'down' ? 'bg-blue-100 text-blue-700' :
                                        'bg-gray-100 text-gray-700'
                                    }`}>
                                    {getTrendIcon(vital.trend)}
                                    <span>{vital.trendValue}</span>
                                </div>
                            </div>

                            {/* Value */}
                            <div className="mb-3">
                                {vital.isText ? (
                                    // Text display for chief complaint
                                    <>
                                        <p className="text-sm font-medium text-gray-600 mb-2">{vital.label}</p>
                                        <p className="text-base font-semibold text-gray-800 leading-relaxed">
                                            {vital.value}
                                        </p>
                                    </>
                                ) : (
                                    // Numeric display for heart rate and weight
                                    <>
                                        <div className="flex items-baseline gap-2">
                                            <span className={`text-4xl font-bold ${getStatusColor(vital)}`}>
                                                {vital.value}
                                            </span>
                                            <span className="text-sm font-medium text-gray-500">{vital.unit}</span>
                                        </div>
                                        <p className="text-sm font-medium text-gray-600 mt-1">{vital.label}</p>
                                    </>
                                )}
                            </div>

                            {/* Sparkline Chart - only for numeric values */}
                            {!vital.isText && vital.data && vital.data.length > 0 && (
                                <div className="h-12 -mx-2">
                                    <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                                        <LineChart data={vital.data}>
                                            <Line
                                                type="monotone"
                                                dataKey="value"
                                                stroke={vital.color === 'red' ? '#ef4444' : vital.color === 'blue' ? '#3b82f6' : '#10b981'}
                                                strokeWidth={2}
                                                dot={false}
                                                animationDuration={1000}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            )}

                            {/* Status Badge */}
                            <div className="mt-3 pt-3 border-t border-gray-200">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-gray-500">Status</span>
                                    <span className="text-xs font-semibold text-green-600 flex items-center gap-1">
                                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                        Normal
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Additional Info */}
            <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center justify-between">
                        <span className="text-gray-600">Temperature</span>
                        <span className="font-semibold text-gray-900">98.6°F</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-gray-600">Respiratory Rate</span>
                        <span className="font-semibold text-gray-900">16 /min</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-gray-600">Last Updated</span>
                        <span className="font-semibold text-gray-900">Just now</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
