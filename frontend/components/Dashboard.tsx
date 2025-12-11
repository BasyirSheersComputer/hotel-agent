/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 * 
 * Performance Dashboard Component
 * Displays real-time metrics and analytics for the Resort Genius system
 * Design tuned to match design.json baseline
 */
"use client";

import React, { useState, useEffect } from "react";

// API Base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types matching new API response
interface MetricsSummary {
    total_queries: number;
    avg_response_time_ms: number;
    success_rate: number;
    unique_agents: number;
    period_hours: number;

    accuracy_percent: number;
    internal_accuracy_percent: number;
    external_accuracy_percent: number;
    aht_reduction_percent: number;
    aht_delta_percent: number;

    rag_count: number;
    rag_percentage: number;
    maps_count: number;
    maps_percentage: number;

    tokens_used: number;
    estimated_cost: number;
    rate_limit_status: string;
    cost_breakdown: string;

    // New ROI Metrics
    avg_sentiment: number;
    avg_csat: number;
    booking_leads: number;
    upsell_opportunities: number;
    total_revenue_potential: number;
    sop_compliance_rate: number;
    fcr_rate: number;
    booking_conversion_rate: number;
}

interface CategoryMetric {
    category: string;
    count: number;
    avg_ai_time: number;
    accuracy: number;
}

interface HourlyTrend {
    time: string;
    queryVolume: number;
    avg_response_time_ms: number;
    success_rate: number;
}

interface AgentMetric {
    name: string;
    queryCount: number;
    avgTimeMs: number;
    accuracyPercent: number;
    lastActive: string;
}

// Error Boundary Component
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean, error: Error | null }> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("Dashboard Error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="flex items-center justify-center min-h-screen bg-red-50 p-6">
                    <div className="bg-white rounded-xl border border-red-200 p-8 shadow-sm max-w-lg w-full">
                        <h2 className="text-xl font-bold text-red-800 mb-4">Something went wrong.</h2>
                        <div className="p-4 bg-slate-50 rounded-lg text-sm font-mono text-slate-700 overflow-auto max-h-60">
                            {this.state.error && this.state.error.toString()}
                        </div>
                        <p className="mt-4 text-slate-500 text-sm">Please refresh the page or check the console.</p>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default function Dashboard() {
    return (
        <ErrorBoundary>
            <DashboardContent />
        </ErrorBoundary>
    );
}

function DashboardContent() {
    const [showSuccess, setShowSuccess] = useState(false);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            const params = new URLSearchParams(window.location.search);
            if (params.get('billing') === 'success') {
                setShowSuccess(true);
                window.history.replaceState({}, '', '/dashboard');
            }
        }
    }, []);

    const [timeRange, setTimeRange] = useState<number>(24);
    const [viewMode, setViewMode] = useState<'preset' | 'custom'>('preset');
    const [customDates, setCustomDates] = useState<{ start: string; end: string }>({ start: "", end: "" });

    const [summary, setSummary] = useState<MetricsSummary | null>(null);
    const [categories, setCategories] = useState<CategoryMetric[]>([]);
    const [trends, setTrends] = useState<HourlyTrend[]>([]);
    const [agents, setAgents] = useState<AgentMetric[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchMetrics = async () => {
        setLoading(true);
        setError(null);
        try {
            let query = `?hours=${timeRange}`;
            if (viewMode === 'custom' && customDates.start && customDates.end) {
                query = `?start_date=${customDates.start}T00:00:00&end_date=${customDates.end}T23:59:59`;
            }

            const [summaryRes, categoriesRes, trendsRes, agentsRes] =
                await Promise.all([
                    fetch(`${API_BASE}/api/metrics/summary${query}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }),
                    fetch(`${API_BASE}/api/metrics/categories${query}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }),
                    fetch(`${API_BASE}/api/metrics/trends${query}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }),
                    fetch(`${API_BASE}/api/metrics/agents${query}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }),
                ]);

            if (!summaryRes.ok) throw new Error("Failed to fetch summary metrics");

            setSummary(await summaryRes.json());
            setCategories(await categoriesRes.json());
            setTrends(await trendsRes.json());
            setAgents(await agentsRes.json());
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : "Failed to fetch metrics");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (viewMode === 'custom' && (!customDates.start || !customDates.end)) return;
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 10000); // Slower refresh for chunks
        return () => clearInterval(interval);
    }, [timeRange, viewMode, customDates]);

    const downloadReport = () => {
        let query = `?hours=${timeRange}`;
        if (viewMode === 'custom' && customDates.start && customDates.end) {
            query = `?start_date=${customDates.start}T00:00:00&end_date=${customDates.end}T23:59:59`;
        }

        // Use direct navigation to trigger browser download handler
        // This avoids client-side Blob issues and plays better with browser security
        const url = `${API_BASE}/api/reports/export${query}`;
        window.open(url, '_blank');
    };

    if (loading && !summary) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="text-gray-500 text-xl font-medium">Loading analytics...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="bg-white border border-red-200 rounded-xl p-6 shadow-sm max-w-md">
                    <h2 className="text-lg font-semibold text-red-600 mb-2">Error Loading Dashboard</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button onClick={fetchMetrics} className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 font-medium">Retry</button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#F0F4F8] p-0 md:p-6">
            <div className="w-full max-w-[1400px] h-[100dvh] md:h-[90vh] bg-white/85 backdrop-blur-[20px] rounded-none md:rounded-[24px] shadow-[0_8px_30px_rgba(0,0,0,0.05)] border-0 md:border border-white/40 overflow-hidden flex flex-col relative font-sans text-slate-800 transition-all duration-300">

                {/* Header with Consistent Padding */}
                <div className="w-full flex flex-col md:flex-row justify-between items-center p-6 md:p-8 border-b border-black/5 bg-white/50 gap-4">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-serif font-bold text-[#0F4C81]">Analytics Dashboard</h1>
                        <p className="text-slate-500 text-sm mt-1">CFO ROI Metrics & Performance</p>
                    </div>

                    <div className="flex flex-col md:flex-row gap-3 items-center">
                        {/* Period Selector */}
                        <div className="flex gap-1 bg-white p-1 rounded-lg border border-black/5 shadow-sm">
                            {[24, 48, 168, 720].map((hours) => (
                                <button
                                    key={hours}
                                    onClick={() => { setTimeRange(hours); setViewMode('preset'); }}
                                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${timeRange === hours && viewMode === 'preset'
                                        ? "bg-[#0F4C81] text-white shadow-sm"
                                        : "text-slate-600 hover:bg-slate-50"
                                        }`}
                                >
                                    {hours === 24 ? "Today" : hours === 48 ? "48h" : hours === 168 ? "7d" : "30d"}
                                </button>
                            ))}
                            <button
                                onClick={() => setViewMode('custom')}
                                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${viewMode === 'custom'
                                    ? "bg-[#0F4C81] text-white shadow-sm"
                                    : "text-slate-600 hover:bg-slate-50"
                                    }`}
                            >
                                Custom
                            </button>
                        </div>

                        {/* Custom Date Inputs */}
                        {viewMode === 'custom' && (
                            <div className="flex gap-2 items-center bg-white p-1 rounded-lg border border-black/5 shadow-sm">
                                <input
                                    type="date"
                                    className="text-sm border-none focus:ring-0 text-slate-600 bg-transparent"
                                    onChange={(e) => setCustomDates(prev => ({ ...prev, start: e.target.value }))}
                                />
                                <span className="text-slate-300">-</span>
                                <input
                                    type="date"
                                    className="text-sm border-none focus:ring-0 text-slate-600 bg-transparent"
                                    onChange={(e) => setCustomDates(prev => ({ ...prev, end: e.target.value }))}
                                />
                            </div>
                        )}

                        {/* Billing Button */}
                        <button
                            onClick={() => window.location.href = '/billing'}
                            className="flex items-center gap-2 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
                        >
                            <span>💳</span> Subscription
                        </button>

                        {/* Export Buttons */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => {
                                    let query = `?hours=${timeRange}`;
                                    if (viewMode === 'custom' && customDates.start && customDates.end) {
                                        query = `?start_date=${customDates.start}T00:00:00&end_date=${customDates.end}T23:59:59`;
                                    }
                                    const url = `${API_BASE}/api/reports/export-pdf${query}`;
                                    window.open(url, '_blank');
                                }}
                                className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-800 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
                                title="Download PDF Report"
                            >
                                <span>📄</span> PDF
                            </button>
                            <button
                                onClick={downloadReport}
                                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
                            >
                                <span>📥</span> Export CSV
                            </button>
                        </div>
                    </div>
                </div>

                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 scroll-smooth">
                    {/* ROI Quadrants */}
                    {summary && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {/* Efficiency Quadrant */}
                            <KPICard
                                label="Efficiency (Speed)"
                                value={`${(summary.avg_response_time_ms || 0).toFixed(0)}ms`}
                                icon="⚡"
                                badge={{ text: "AHT", color: "neutral" }}
                                subValues={[
                                    { label: "Queries", value: summary.total_queries || 0 },
                                    { label: "AHT Saved", value: `${summary.aht_reduction_percent || 0}%`, color: "text-green-600" }
                                ]}
                            />

                            {/* Accuracy Quadrant */}
                            <KPICard
                                label="Accuracy & Quality"
                                value={`${summary.sop_compliance_rate || 0}%`}
                                icon="✅"
                                badge={{ text: "SOP Compliant", color: "success" }}
                                subValues={[
                                    { label: "Accuracy", value: `${summary.accuracy_percent || 0}%` },
                                    { label: "FCR", value: `${summary.fcr_rate || 0}%` }
                                ]}
                            />

                            {/* Revenue Quadrant */}
                            <KPICard
                                label="Revenue Impact"
                                value={`$${(summary.total_revenue_potential || 0).toLocaleString()}`}
                                icon="💰"
                                badge={{ text: "Potential", color: "success" }}
                                subValues={[
                                    { label: "Leads", value: summary.booking_leads || 0 },
                                    { label: "Upsells", value: summary.upsell_opportunities || 0 }
                                ]}
                            />

                            {/* CSAT Quadrant */}
                            <KPICard
                                label="Customer Satisfaction"
                                value={`${(summary.avg_csat || 0).toFixed(1)}/5`}
                                icon="💖"
                                badge={{ text: "CSAT", color: "neutral" }}
                                subValues={[
                                    { label: "Sentiment", value: (summary.avg_sentiment || 0) > 0 ? "Positive" : "Neutral" },
                                    { label: "Score", value: (summary.avg_sentiment || 0).toFixed(2) }
                                ]}
                            />
                        </div>
                    )}

                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        {/* Top Row: Trends (3) + Sources/API (1) */}
                        <div className="lg:col-span-3 bg-white/60 rounded-[16px] border border-black/5 p-6 shadow-sm">
                            <h3 className="text-lg font-serif font-semibold text-[#0F4C81] mb-6">Hourly Trends</h3>
                            <div className="h-80 w-full">
                                {(() => {
                                    // Calculate Chart Range Logic
                                    let start = 0;
                                    let end = 0;

                                    if (viewMode === 'custom' && customDates.start && customDates.end) {
                                        // Custom Date Range (Start 00:00 to End 23:59)
                                        start = new Date(`${customDates.start}T00:00:00`).getTime();
                                        end = new Date(`${customDates.end}T23:59:59`).getTime();
                                    } else {
                                        // Preset (Rolling from Now? Or Start of Day?)
                                        // "Today" (24h) usually implies last 24h in this context, or today 00:00?
                                        // The selector says "24h", "48h". Let's stick to Rolling window as implied by "24h".
                                        // If user wants Calendar Today, we'd need a "Today" button separate from "24h".
                                        // But wait, the button label is "Today" for 24h.
                                        // If label is "Today", let's make it start at 00:00 today?
                                        // Actually, consistency with "48h" implies duration.
                                        // Let's use: End = Now, Start = Now - hours.
                                        const now = new Date();
                                        now.setMinutes(0, 0, 0);
                                        end = now.getTime();
                                        start = end - (timeRange * 3600 * 1000);
                                    }

                                    return (
                                        <SimpleLineChart
                                            data={trends}
                                            rangeStart={start}
                                            rangeEnd={end}
                                        />
                                    );
                                })()}
                            </div>
                        </div>

                        <div className="space-y-6">
                            {/* Query Sources */}
                            {summary && (
                                <div className="bg-white/60 rounded-[16px] border border-black/5 p-6 shadow-sm">
                                    <h3 className="text-lg font-serif font-semibold text-[#0F4C81] mb-4">Query Sources</h3>
                                    <div className="space-y-4">
                                        <SourceBar
                                            label="RAG Queries"
                                            count={summary.rag_count || 0}
                                            percentage={summary.rag_percentage || 0}
                                            color="bg-[#0F4C81]"
                                        />
                                        <SourceBar
                                            label="Maps Queries"
                                            count={summary.maps_count || 0}
                                            percentage={summary.maps_percentage || 0}
                                            color="bg-[#1A5F9A]"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* API Usage & Cost */}
                            {summary && (
                                <div className="bg-white/60 rounded-[16px] border border-black/5 p-6 shadow-sm">
                                    <h3 className="text-lg font-serif font-semibold text-[#0F4C81] mb-4">API Usage & Cost</h3>
                                    <div className="space-y-3 text-sm">
                                        <div className="flex justify-between py-2 border-b border-black/5">
                                            <span className="text-slate-500">Tokens Used</span>
                                            <span className="font-medium text-slate-900">{(summary.tokens_used || 0).toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between py-2 border-b border-black/5">
                                            <span className="text-slate-500">Est. Cost</span>
                                            <span className="font-medium text-slate-900">${(summary.estimated_cost || 0).toFixed(4)}</span>
                                        </div>
                                        <div className="flex justify-between py-2 border-b border-black/5">
                                            <span className="text-slate-500">Rate Limit</span>
                                            <span className="font-medium text-green-600">{summary.rate_limit_status || "Unknown"}</span>
                                        </div>
                                        <div className="pt-2">
                                            <span className="text-slate-500 block mb-1">Breakdown</span>
                                            <span className="text-xs text-slate-700 bg-slate-50 px-2 py-1 rounded block border border-slate-100">
                                                {summary.cost_breakdown || "N/A"}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Bottom Row: Agents (3) + Categories (1) */}
                        <div className="lg:col-span-3 bg-white/60 rounded-[16px] border border-black/5 p-6 shadow-sm overflow-hidden">
                            <h3 className="text-lg font-serif font-semibold text-[#0F4C81] mb-4">Agent Performance</h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 border-b border-black/5">
                                        <tr>
                                            <th className="px-6 py-4 font-medium">Agent</th>
                                            <th className="px-6 py-4 font-medium text-right">Queries Handled</th>
                                            <th className="px-6 py-4 font-medium text-right">Avg Response Time</th>
                                            <th className="px-6 py-4 font-medium text-right">Accuracy</th>
                                            <th className="px-6 py-4 font-medium text-right">Last Active</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-black/5">
                                        {agents.map((agent) => (
                                            <tr key={agent.name} className="hover:bg-slate-50/50 transition-colors">
                                                <td className="px-6 py-4 font-medium text-slate-900">{agent.name}</td>
                                                <td className="px-6 py-4 text-right text-slate-600">{agent.queryCount}</td>
                                                <td className="px-6 py-4 text-right text-slate-600">{(agent.avgTimeMs || 0).toFixed(0)}ms</td>
                                                <td className="px-6 py-4 text-right">
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${agent.accuracyPercent >= 90 ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                                                        }`}>
                                                        {agent.accuracyPercent}%
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-right text-slate-500">
                                                    {(() => {
                                                        try {
                                                            // Ensure ISO format for cross-browser compatibility
                                                            const validDateStr = (agent.lastActive || "").replace(' ', 'T');
                                                            const date = new Date(validDateStr);
                                                            if (isNaN(date.getTime())) return "N/A";
                                                            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                                                        } catch (e) {
                                                            return "N/A";
                                                        }
                                                    })()}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Top Question Categories */}
                        <div className="bg-white/60 rounded-[16px] border border-black/5 p-6 shadow-sm">
                            <h3 className="text-lg font-serif font-semibold text-[#0F4C81] mb-4">Top Categories</h3>
                            <div className="flex flex-wrap gap-2">
                                {categories.slice(0, 8).map((cat) => (
                                    <div key={cat.category} className="group relative bg-white border border-black/5 hover:border-[#0F4C81] rounded-[12px] p-3 transition-all cursor-default w-full shadow-sm hover:shadow-md">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="font-medium text-slate-700">{cat.category}</span>
                                            <span className="text-xs font-bold text-[#0F4C81] bg-[#0F4C81]/10 px-2 py-0.5 rounded-full">{cat.count}</span>
                                        </div>
                                        <div className="flex justify-between text-xs text-slate-500 mt-2">
                                            <span>{(cat.avg_ai_time || 0).toFixed(0)}ms avg</span>
                                            <span className={cat.accuracy >= 90 ? "text-green-600" : "text-yellow-600"}>
                                                {cat.accuracy}% acc
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Success Modal */}
            {showSuccess && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center border-t-4 border-green-500 relative animate-in zoom-in-95 duration-300">
                        <button
                            onClick={() => setShowSuccess(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                        >
                            ✕
                        </button>
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <span className="text-3xl">🛡️</span>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">System Secured!</h2>
                        <p className="text-gray-600 mb-6">
                            Your <strong>Annual License</strong> is active. The Revenue Defense System is now fully operational.
                        </p>
                        <div className="bg-slate-50 rounded-lg p-4 mb-6 text-left text-sm text-slate-700">
                            <div className="flex justify-between mb-2">
                                <span>Status:</span>
                                <span className="font-bold text-green-600">ACTIVE</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Plan:</span>
                                <span className="font-medium">Resort Genius Core</span>
                            </div>
                        </div>
                        <button
                            onClick={() => setShowSuccess(false)}
                            className="w-full py-3 bg-[#0F4C81] hover:bg-[#1A5F9A] text-white font-bold rounded-lg transition-colors"
                        >
                            Access Dashboard
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Sub-components

interface KPICardProps {
    label: string;
    value: string | number;
    icon: string;
    badge?: {
        text: string;
        color: "warning" | "success" | "neutral";
    };
    subValues?: {
        label: string;
        value: string | number;
        color?: string;
    }[];
}

function KPICard({ label, value, icon, badge, subValues }: KPICardProps) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between h-full">
            <div className="flex justify-between items-start mb-2">
                <div className="p-2 bg-slate-50 rounded-lg text-xl">{icon}</div>
                {badge && (
                    <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded-full ${badge.color === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-700'
                        }`}>
                        {badge.text}
                    </span>
                )}
            </div>
            <div>
                <h4 className="text-slate-500 text-sm font-medium mb-1">{label}</h4>
                <div className="text-2xl font-bold text-slate-900">{value}</div>
                {subValues && (
                    <div className="flex gap-3 mt-2 text-xs">
                        {subValues.map((sv, i) => (
                            <div key={i} className="flex items-center gap-1">
                                <span className="text-slate-400">{sv.label}:</span>
                                <span className={`font-medium ${sv.color || 'text-slate-700'}`}>{sv.value}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

interface SourceBarProps {
    label: string;
    count: number;
    percentage: number;
    color: string;
}

function SourceBar({ label, count, percentage, color }: SourceBarProps) {
    return (
        <div>
            <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-slate-700">{label}</span>
                <span className="text-slate-500">{percentage}% ({count})</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                    className={`h-full rounded-full ${color}`}
                    style={{ width: `${Math.max(percentage, 5)}%` }}
                />
            </div>
        </div>
    );
}

import {
    ComposedChart,
    Bar,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

// ... (existing helper functions if any)

interface SimpleLineChartProps {
    data: HourlyTrend[];
    rangeStart: number;
    rangeEnd: number;
}

function SimpleLineChart({ data, rangeStart, rangeEnd }: SimpleLineChartProps) {
    console.log("Chart Debug:", { rangeStart, rangeEnd, dataLen: data.length });
    const durationHours = (rangeEnd - rangeStart) / (1000 * 3600);
    const isDaily = durationHours > 50;

    // 1. Map existing data
    const chartMap = new Map();
    data.forEach(d => {
        try {
            const date = new Date((d.time || "").replace(' ', 'T'));
            if (!isNaN(date.getTime())) {
                const key = isDaily
                    ? new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime()
                    : (date.setMinutes(0, 0, 0), date.getTime());

                // Aggregate if collision (for daily)
                if (chartMap.has(key)) {
                    const existing = chartMap.get(key);
                    const totalVol = existing.queryVolume + d.queryVolume;
                    // Weighted avg for response time
                    const weightedTime = (existing.avg_response_time_ms * existing.queryVolume + d.avg_response_time_ms * d.queryVolume) / (totalVol || 1);

                    chartMap.set(key, {
                        ...existing,
                        queryVolume: totalVol,
                        avg_response_time_ms: weightedTime
                    });
                } else {
                    chartMap.set(key, { ...d });
                }
            }
        } catch { }
    });

    // 2. Zero-Fill Loop
    const filledData = [];
    let current = rangeStart;
    const step = isDaily ? 24 * 3600 * 1000 : 3600 * 1000;

    // Safety limit
    let iterations = 0;
    while (current <= rangeEnd && iterations < 1000) {
        iterations++;
        const key = current; // Already normalized by loop step logic if we align current correctly?
        // Actually current starts at specific time. If Daily, we want 00:00 of that day.

        let normalizedKey = current;
        const dateObj = new Date(current);

        if (isDaily) {
            normalizedKey = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()).getTime();
        } else {
            // Ensure hour alignment?
            // If rangeStart is not hour aligned, this loop might be offset.
            // But lets assume passed timestamps are reasonable.
        }

        const existing = chartMap.get(normalizedKey);

        // Format Label
        let label = "";
        if (isDaily) {
            // "Dec 10"
            label = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        } else {
            // Hourly
            // Always show Day if range >= 24h to avoid "14:00" (Yesterday) vs "14:00" (Today) collision
            if (durationHours >= 24) {
                label = `${dateObj.getDate()}/${dateObj.getMonth() + 1} ${dateObj.getHours().toString().padStart(2, '0')}:00`;
            } else {
                label = dateObj.getHours().toString().padStart(2, '0') + ":00";
            }
        }

        if (existing) {
            filledData.push({
                ...existing,
                name: label,
                response_time: parseFloat((existing.avg_response_time_ms || 0).toFixed(0))
            });
        } else {
            filledData.push({
                time: dateObj.toISOString(),
                queryVolume: 0,
                avg_response_time_ms: 0,
                success_rate: 0,
                name: label,
                response_time: 0
            });
        }

        current += step;
    }

    return (
        <div className="h-full w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                    data={filledData}
                    margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                >
                    <CartesianGrid stroke="#f5f5f5" vertical={false} />
                    <XAxis
                        dataKey="name"
                        scale="band"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        interval="preserveStartEnd"
                        minTickGap={30}
                    />
                    <YAxis
                        yAxisId="left"
                        orientation="left"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        label={{ value: 'Queries', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#94a3b8', fontSize: 10 } }}
                    />
                    <YAxis
                        yAxisId="right"
                        orientation="right"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        unit="ms"
                        label={{ value: 'Avg Time (ms)', angle: 90, position: 'insideRight', style: { textAnchor: 'middle', fill: '#94a3b8', fontSize: 10 } }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#fff',
                            borderRadius: '12px',
                            border: '1px solid #e2e8f0',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                            fontSize: '12px'
                        }}
                        itemStyle={{ padding: 0 }}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar
                        yAxisId="left"
                        dataKey="queryVolume"
                        name="Query Volume"
                        barSize={isDaily ? 40 : 20} // Thicker bars for daily
                        fill="#0F4C81"
                        radius={[4, 4, 0, 0]}
                    />
                    <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="response_time"
                        name="Avg Response Time"
                        stroke="#D4AF37"
                        strokeWidth={2}
                        dot={isDaily} // Show dots for daily points
                        activeDot={{ r: 4 }}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
}
