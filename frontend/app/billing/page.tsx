"use client";

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth, useAuthHeaders } from '@/contexts/AuthContext';
import BillingSidebar from '@/components/BillingSidebar';
import {
    Loader2,
    CheckCircle,
    HardDrive,
    MessageSquare,
    TrendingUp,
    Download,
    AlertTriangle
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';

// Mock Data for Charts if API fails or is empty
const MOCK_USAGE_DATA = [
    { name: 'Week 1', tokens: 12000 },
    { name: 'Week 2', tokens: 19000 },
    { name: 'Week 3', tokens: 15000 },
    { name: 'Week 4', tokens: 28000 },
];

export default function BillingPage() {
    const searchParams = useSearchParams();
    const activeTab = searchParams.get('tab') || 'overview';
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const authHeaders = useAuthHeaders();
    const router = useRouter();
    const { logout } = useAuth();
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        fetchUsage();
    }, [activeTab]);

    const fetchUsage = async () => {
        try {
            const res = await fetch(`${API_URL}/api/billing/usage`, {
                headers: authHeaders as HeadersInit
            });
            if (res.ok) {
                const json = await res.json();
                setData(json);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReport = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/billing/report`, {
                method: 'POST',
                headers: authHeaders as HeadersInit
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `billing_report_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                alert("Failed to generate report");
            }
        } catch (e) {
            console.error(e);
            alert("Error downloading report");
        } finally {
            setLoading(false);
        }
    };

    const handleUnsubscribe = async () => {
        if (!confirm("Are you sure you want to cancel? This action is irreversible.")) return;

        try {
            const res = await fetch(`${API_URL}/api/billing/unsubscribe`, {
                method: "POST",
                headers: authHeaders as HeadersInit
            });

            if (res.ok) {
                alert("Subscription canceled.");
                logout();
                router.push('/login');
            } else {
                alert("Failed to cancel subscription.");
            }
        } catch (e) {
            console.error(e);
            alert("Error connecting to server.");
        }
    };

    if (loading && !data) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
                <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white flex">
            {/* Sidebar */}
            <BillingSidebar onCollapse={setSidebarOpen} />

            {/* Main Content */}
            <div className={`flex-1 transition-all duration-300 p-8 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>

                {/* Header */}
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
                        <p className="text-slate-400 mt-1">Manage your plan, usage, and invoices</p>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-bold border border-green-500/50">
                            Active
                        </span>
                        <button onClick={handleDownloadReport} className="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700">
                            <Download className="h-4 w-4 mr-2" />
                            Export Report
                        </button>
                    </div>
                </header>

                {/* Tab Content */}
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        {/* Plan Card */}
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="md:col-span-2 bg-gradient-to-br from-purple-900/50 to-slate-900 border border-purple-500/30 rounded-2xl p-6 relative overflow-hidden">
                                <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />

                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Current Plan</h3>
                                        <div className="text-4xl font-bold">{data?.plan?.name || 'Professional'}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-bold">{data?.plan?.amount || 'RM 10,000.00'}</div>
                                        <div className="text-slate-400 text-sm">/ month</div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-slate-300">Next Billing Date</span>
                                        <span className="font-mono text-white">Dec 28, 2025</span>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-2">
                                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '65%' }} />
                                    </div>
                                    <p className="text-xs text-slate-500">20 days remaining in this cycle</p>
                                </div>
                            </div>

                            {/* Stats Cards */}
                            <div className="space-y-6">
                                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                                    <div className="flex items-center space-x-3 mb-2">
                                        <MessageSquare className="h-5 w-5 text-blue-400" />
                                        <h4 className="text-slate-400 font-medium">Token Usage</h4>
                                    </div>
                                    <div className="text-2xl font-bold mb-1">
                                        {data?.metrics?.tokens?.used.toLocaleString() || '0'}
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        of {data?.metrics?.tokens?.limit.toLocaleString()} limit
                                    </div>
                                </div>

                                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                                    <div className="flex items-center space-x-3 mb-2">
                                        <HardDrive className="h-5 w-5 text-orange-400" />
                                        <h4 className="text-slate-400 font-medium">Storage</h4>
                                    </div>
                                    <div className="text-2xl font-bold mb-1">
                                        {data?.metrics?.storage?.used_mb || '0'} MB
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        of {data?.metrics?.storage?.limit_mb} MB limit
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Upsell Banner */}
                        <div className="bg-gradient-to-r from-pink-600/20 to-purple-600/20 border border-pink-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between">
                            <div className="mb-4 md:mb-0">
                                <h3 className="text-xl font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">
                                    Need more Properties?
                                </h3>
                                <p className="text-slate-300 mt-1">Upgrade to Enterprise for unlimited property management and priority support.</p>
                            </div>
                            <button className="px-6 py-3 bg-white text-slate-900 hover:bg-slate-200 font-bold rounded-lg transition-colors">
                                Upgrade Plan
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'usage' && (
                    <div className="space-y-6">
                        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                            <h3 className="text-xl font-bold mb-6">Token Consumtion History</h3>
                            <div className="h-80 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={MOCK_USAGE_DATA}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                        <XAxis dataKey="name" stroke="#64748b" />
                                        <YAxis stroke="#64748b" />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }}
                                            itemStyle={{ color: '#e2e8f0' }}
                                        />
                                        <Bar dataKey="tokens" fill="#8b5cf6" radius={[4, 4, 0, 0]}>
                                            {MOCK_USAGE_DATA.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={['#8b5cf6', '#ec4899', '#3b82f6', '#10b981'][index % 4]} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {/* Placeholder for Support */}
                {activeTab === 'support' && (
                    <div className="flex flex-col h-[600px] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                        <div className="p-4 border-b border-slate-800 bg-slate-950">
                            <h3 className="font-bold flex items-center">
                                <div className="w-3 h-3 bg-green-500 rounded-full mr-2" />
                                Billing Support Agent
                            </h3>
                        </div>
                        <div className="flex-1 p-8 flex flex-col items-center justify-center text-slate-500">
                            <MessageSquare className="h-12 w-12 mb-4 opacity-50" />
                            <p>Start a conversation to get help with your billing.</p>
                            <button className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                                Chat with Support
                            </button>
                        </div>
                    </div>
                )}

                {/* Settings / Cancel Subscription */}
                {activeTab === 'settings' && (
                    <div className="space-y-6">
                        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                            <h3 className="text-xl font-bold mb-6">General Settings</h3>
                            <p className="text-slate-400">Manage your organization settings here.</p>
                        </div>

                        <div className="bg-red-900/10 border border-red-900/50 rounded-2xl p-8">
                            <div className="flex items-start gap-4">
                                <div className="p-3 bg-red-900/20 rounded-lg">
                                    <AlertTriangle className="h-6 w-6 text-red-500" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">Danger Zone</h3>
                                    <p className="text-slate-400 mb-6 max-w-xl">
                                        Canceling your subscription will immediately revoke access to all features, including the knowledge base and dashboard. This action cannot be undone.
                                    </p>
                                    <button
                                        onClick={handleUnsubscribe}
                                        className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors"
                                    >
                                        Cancel Subscription
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
