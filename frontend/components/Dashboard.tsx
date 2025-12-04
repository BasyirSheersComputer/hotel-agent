/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 * 
 * Performance Dashboard Component
 * Displays real-time metrics and analytics for the Resort Genius system
 * Design tuned to match design.json baseline
 */
"use client";

import { useState, useEffect } from "react";

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

export default function Dashboard() {
    const [timeRange, setTimeRange] = useState<number>(24);
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
            const [summaryRes, categoriesRes, trendsRes, agentsRes] =
                await Promise.all([
                    fetch(`${API_BASE}/api/metrics/summary?hours=${timeRange}`),
                    fetch(`${API_BASE}/api/metrics/categories?hours=${timeRange}`),
                    fetch(`${API_BASE}/api/metrics/trends?hours=${timeRange}`),
                    fetch(`${API_BASE}/api/metrics/agents?hours=${timeRange}`),
                ]);

            if (!summaryRes.ok) throw new Error("Failed to fetch summary metrics");

            setSummary(await summaryRes.json());
            setCategories(await categoriesRes.json());
            setTrends(await trendsRes.json());
            setAgents(await agentsRes.json());
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to fetch metrics");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 60000);
        return () => clearInterval(interval);
    }, [timeRange]);

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
        <div className="w-full min-h-screen bg-gray-50 font-sans text-slate-800">
            {/* Header */}
            <div className="w-full mx-auto mb-6 flex justify-between items-center px-4 pt-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
                    <p className="text-slate-500 text-sm mt-1">Real-time performance metrics</p>
                </div>
                <div className="flex gap-2 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
                    {[24, 48, 168].map((hours) => (
                        <button
                            key={hours}
                            onClick={() => setTimeRange(hours)}
                            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${timeRange === hours
                                ? "bg-slate-900 text-white shadow-sm"
                                : "text-slate-600 hover:bg-slate-50"
                                }`}
                        >
                            {hours === 24 ? "Today" : hours === 48 ? "48h" : "7d"}
                        </button>
                    ))}
                </div>
            </div>

            <div className="w-full mx-auto space-y-4 px-4 pb-4">
                {/* KPI Row */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <KPICard
                            label="Total Queries Today"
                            value={summary.total_queries.toLocaleString()}
                            icon="💬"
                        />
                        <KPICard
                            label="Avg Response Time"
                            value={`${summary.avg_response_time_ms.toFixed(0)}ms`}
                            icon="⚡"
                            badge={summary.avg_response_time_ms > 3000 ? { text: "Needs improvement", color: "warning" } : undefined}
                        />
                        <KPICard
                            label="Accuracy Score"
                            value={`${summary.accuracy_percent}%`}
                            icon="🎯"
                            subValues={[
                                { label: "Internal", value: `${summary.internal_accuracy_percent}%` },
                                { label: "External", value: `${summary.external_accuracy_percent}%` }
                            ]}
                        />
                        <KPICard
                            label="AHT Reduction"
                            value={`${summary.aht_reduction_percent}%`}
                            icon="📉"
                            subValues={[
                                { label: "Delta", value: `+${summary.aht_delta_percent}%`, color: "text-green-600" }
                            ]}
                        />
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                    {/* Top Row: Trends (3) + Sources/API (1) */}
                    <div className="lg:col-span-3 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-slate-900 mb-6">Hourly Trends</h3>
                        <div className="h-80 w-full">
                            <SimpleLineChart data={trends} />
                        </div>
                    </div>

                    <div className="space-y-4">
                        {/* Query Sources */}
                        {summary && (
                            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                                <h3 className="text-lg font-semibold text-slate-900 mb-4">Query Sources</h3>
                                <div className="space-y-4">
                                    <SourceBar
                                        label="RAG Queries"
                                        count={summary.rag_count}
                                        percentage={summary.rag_percentage}
                                        color="bg-slate-800"
                                    />
                                    <SourceBar
                                        label="Maps Queries"
                                        count={summary.maps_count}
                                        percentage={summary.maps_percentage}
                                        color="bg-teal-600"
                                    />
                                </div>
                            </div>
                        )}

                        {/* API Usage & Cost */}
                        {summary && (
                            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                                <h3 className="text-lg font-semibold text-slate-900 mb-4">API Usage & Cost</h3>
                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between py-2 border-b border-slate-100">
                                        <span className="text-slate-500">Tokens Used</span>
                                        <span className="font-medium text-slate-900">{summary.tokens_used.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between py-2 border-b border-slate-100">
                                        <span className="text-slate-500">Est. Cost</span>
                                        <span className="font-medium text-slate-900">${summary.estimated_cost.toFixed(4)}</span>
                                    </div>
                                    <div className="flex justify-between py-2 border-b border-slate-100">
                                        <span className="text-slate-500">Rate Limit</span>
                                        <span className="font-medium text-green-600">{summary.rate_limit_status}</span>
                                    </div>
                                    <div className="pt-2">
                                        <span className="text-slate-500 block mb-1">Breakdown</span>
                                        <span className="text-xs text-slate-700 bg-slate-50 px-2 py-1 rounded block border border-slate-100">
                                            {summary.cost_breakdown}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Bottom Row: Agents (3) + Categories (1) */}
                    <div className="lg:col-span-3 bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-hidden">
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Agent Performance</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                                    <tr>
                                        <th className="px-6 py-4 font-medium">Agent</th>
                                        <th className="px-6 py-4 font-medium text-right">Queries Handled</th>
                                        <th className="px-6 py-4 font-medium text-right">Avg Response Time</th>
                                        <th className="px-6 py-4 font-medium text-right">Accuracy</th>
                                        <th className="px-6 py-4 font-medium text-right">Last Active</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {agents.map((agent) => (
                                        <tr key={agent.name} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 font-medium text-slate-900">{agent.name}</td>
                                            <td className="px-6 py-4 text-right text-slate-600">{agent.queryCount}</td>
                                            <td className="px-6 py-4 text-right text-slate-600">{agent.avgTimeMs.toFixed(0)}ms</td>
                                            <td className="px-6 py-4 text-right">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${agent.accuracyPercent >= 90 ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                                                    }`}>
                                                    {agent.accuracyPercent}%
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right text-slate-500">
                                                {new Date(agent.lastActive).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Top Question Categories */}
                    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Top Categories</h3>
                        <div className="flex flex-wrap gap-2">
                            {categories.slice(0, 8).map((cat) => (
                                <div key={cat.category} className="group relative bg-white border border-slate-200 hover:border-blue-400 rounded-lg p-3 transition-all cursor-default w-full">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-medium text-slate-700">{cat.category}</span>
                                        <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded-full">{cat.count}</span>
                                    </div>
                                    <div className="flex justify-between text-xs text-slate-500 mt-2">
                                        <span>{cat.avg_ai_time.toFixed(0)}ms avg</span>
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
    );
}

// Sub-components

function KPICard({ label, value, icon, badge, subValues }: any) {
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
                        {subValues.map((sv: any, i: number) => (
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

function SourceBar({ label, count, percentage, color }: any) {
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

function SimpleLineChart({ data }: { data: HourlyTrend[] }) {
    if (!data.length) return <div className="h-full flex items-center justify-center text-slate-400">No data available</div>;

    const maxVal = Math.max(...data.map(d => d.queryVolume), 5);

    return (
        <div className="h-full flex items-end gap-1 pt-4">
            {data.map((d, i) => {
                const heightPercent = (d.queryVolume / maxVal) * 100;
                return (
                    <div key={i} className="flex-1 flex flex-col items-center group relative">
                        {/* Tooltip */}
                        <div className="absolute bottom-full mb-2 hidden group-hover:block z-10 bg-slate-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                            {d.queryVolume} queries at {new Date(d.time).getHours()}:00
                        </div>
                        {/* Bar (simulating line point for MVP) */}
                        <div
                            className="w-full mx-0.5 bg-purple-100 hover:bg-purple-200 rounded-t-sm transition-all relative"
                            style={{ height: `${Math.max(heightPercent, 5)}%` }}
                        >
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-purple-500 rounded-full -mt-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        {/* X Axis Label */}
                        {i % 3 === 0 && (
                            <div className="text-[10px] text-slate-400 mt-1">
                                {new Date(d.time).getHours()}h
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
