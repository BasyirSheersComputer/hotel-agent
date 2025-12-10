
"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useAuthHeaders } from '@/contexts/AuthContext';

// Types
interface Tenant {
    org_id: string;
    name: string;
    slug: string;
    plan: string;
    property_count: number;
    user_count: number;
    status: string;
    created_at: string;
}

interface GlobalStats {
    total_tenants: number;
    active_tenants: number;
    total_users: number;
    total_queries_24h: number;
    system_health: string;
    avg_latency_ms: number;
}

export default function SuperAdminDashboard() {
    const { user, isLoading } = useAuth();
    const headers = useAuthHeaders();
    const router = useRouter();

    const [stats, setStats] = useState<GlobalStats | null>(null);
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loadingData, setLoadingData] = useState(true);

    useEffect(() => {
        if (!isLoading && (!user || user.role !== 'super_admin')) {
            // Redirect if not super admin (commented out for dev speed, enable later)
            // router.push('/dashboard'); 
        }
    }, [user, isLoading, router]);

    useEffect(() => {
        if (user) {
            fetchData();
        }
    }, [user]); // user dependency ensures headers are ready

    const fetchData = async () => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

            const [statsRes, tenantsRes] = await Promise.all([
                fetch(`${API_URL}/api/super-admin/stats`, { headers: headers as HeadersInit }),
                fetch(`${API_URL}/api/super-admin/tenants?limit=50`, { headers: headers as HeadersInit })
            ]);

            if (statsRes.ok) setStats(await statsRes.json());
            if (tenantsRes.ok) setTenants(await tenantsRes.json());
        } catch (error) {
            console.error("Failed to fetch super admin data", error);
        } finally {
            setLoadingData(false);
        }
    };

    if (isLoading || loadingData) {
        return <div className="p-8 text-white">Loading Super Admin Controller...</div>;
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white p-8 font-sans">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        SaaS Controller
                    </h1>
                    <p className="text-slate-400">System Oversight & Tenant Management</p>
                </div>
                <div className="flex gap-4">
                    <button className="px-4 py-2 border border-slate-700 rounded-lg hover:bg-slate-800 text-sm font-medium transition-colors"
                        onClick={() => window.location.href = '/dashboard'}>
                        Back to App
                    </button>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <MetricCard title="Total Tenants" value={stats?.total_tenants || 0} subValue={`${stats?.active_tenants} Active`} />
                <MetricCard title="Total Users" value={stats?.total_users || 0} />
                <MetricCard title="24h Queries" value={stats?.total_queries_24h || 0} />
                <MetricCard title="System Health" value={stats?.system_health || "Unknown"}
                    className={stats?.system_health === "healthy" ? "text-green-400" : "text-red-400"} />
            </div>

            {/* Tenants Table */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-sm">
                <div className="p-6 border-b border-slate-800 flex justify-between items-center">
                    <h2 className="text-xl font-semibold">Tenants Directory</h2>
                    <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors">
                        Add Tenant
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-950 text-slate-400 text-sm uppercase tracking-wider">
                            <tr>
                                <th className="p-4 font-medium">Integration Name</th>
                                <th className="p-4 font-medium">Org ID</th>
                                <th className="p-4 font-medium">Plan</th>
                                <th className="p-4 font-medium">Properties</th>
                                <th className="p-4 font-medium">Users</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 text-sm">
                            {tenants.map((tenant) => (
                                <tr key={tenant.org_id} className="hover:bg-slate-800/50 transition-colors">
                                    <td className="p-4 font-medium text-white">{tenant.name}</td>
                                    <td className="p-4 text-xs font-mono text-slate-500">{tenant.org_id.substring(0, 8)}...</td>
                                    <td className="p-4"><Badge>{tenant.plan}</Badge></td>
                                    <td className="p-4 text-slate-300">{tenant.property_count}</td>
                                    <td className="p-4 text-slate-300">{tenant.user_count}</td>
                                    <td className="p-4">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium 
                                            ${tenant.status === 'active' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                                            {tenant.status}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right">
                                        <button className="text-blue-400 hover:text-blue-300 font-medium hover:underline">
                                            Manage
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {tenants.length === 0 && (
                                <tr>
                                    <td colSpan={7} className="p-8 text-center text-slate-500">
                                        No tenants found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

// Simple internal components
function MetricCard({ title, value, subValue, className = "" }: any) {
    return (
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors shadow-sm">
            <h3 className="text-slate-400 text-sm font-medium mb-2">{title}</h3>
            <div className={`text-3xl font-bold ${className}`}>{value}</div>
            {subValue && <div className="text-slate-500 text-sm mt-1">{subValue}</div>}
        </div>
    );
}

function Badge({ children }: any) {
    return (
        <span className="bg-slate-800 text-slate-300 px-2 py-1 rounded text-xs border border-slate-700 font-medium">
            {children}
        </span>
    );
}
