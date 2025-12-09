"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function BillingPage() {
    const router = useRouter();
    const [loading, setLoading] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    // API Base URL - defaults to localhost:8001 (Port 8000 blocked)
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

    const handleUpgrade = async () => {
        setLoading('annual');
        setError(null);
        try {
            const token = localStorage.getItem('token');
            // Becker Style: Only one "Success" path.
            const backendPlanId = 'pro';

            const res = await fetch(`${API_BASE}/api/subscriptions/checkout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    plan_id: backendPlanId,
                    success_url: window.location.origin + '/dashboard?billing=success',
                    cancel_url: window.location.origin + '/billing?billing=cancel'
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Checkout failed');
            }

            const data = await res.json();
            window.location.href = data.url;
        } catch (e: any) {
            console.error("Checkout Error:", e);
            setError(e.message || "Connection failed");
            setLoading(null);
        }
    };

    const handlePortal = async () => {
        setLoading('portal');
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/api/subscriptions/portal`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    return_url: window.location.href
                })
            });

            const data = await res.json();
            if (data.url) window.location.href = data.url;
        } catch (e) {
            console.error(e);
            setLoading(null);
        }
    };

    return (
        <div className="min-h-screen bg-[#050B14] p-8 font-sans text-white">
            <div className="max-w-5xl mx-auto pt-10">

                {/* Header - Direct & Outcome Focused */}
                <div className="text-center mb-16">
                    <div className="inline-block bg-blue-900/30 text-blue-400 border border-blue-800/50 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest mb-6">
                        Private Access • Club Med Implementation
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight leading-tight">
                        The Revenue Defense <br className="hidden md:block" /> System.
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
                        We don't sell software. We sell <strong>completed bookings and perfect answers.</strong><br />
                        Tailor-made for Resort Operations.
                    </p>
                </div>

                {error && (
                    <div className="bg-red-900/20 text-red-400 p-4 rounded mb-8 border border-red-900/50 text-center max-w-md mx-auto">
                        {error}
                    </div>
                )}

                {/* The Offer Container */}
                <div className="relative max-w-4xl mx-auto">
                    {/* Glow Effect */}
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-[20px] blur opacity-25"></div>

                    <div className="relative bg-[#0F1623] border border-gray-800 rounded-[20px] p-8 md:p-12 overflow-hidden">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

                            {/* Left: The Specs */}
                            <div>
                                <h3 className="text-2xl font-bold text-white mb-2">Resort Genius <span className="text-blue-500">Core</span></h3>
                                <p className="text-gray-400 mb-8 text-sm">Full Outcome License • 12 Months</p>

                                <div className="space-y-5">
                                    <FeatureRow text="Instant Answer Engine (0.8s Latency)" />
                                    <FeatureRow text="Monsoon Mode & Seasonal Auto-Sync" />
                                    <FeatureRow text="Conversion Uplift Protocol" />
                                    <FeatureRow text="Full SOP Harmonization (We do the work)" />
                                    <FeatureRow text="Dedicated Concierge Manager" />
                                </div>

                                <div className="mt-10 pt-8 border-t border-gray-800">
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-4xl font-bold text-white">RM 120,000</span>
                                        <span className="text-gray-500 text-sm">/ year</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-2">
                                        Paid annually upfront. <br />
                                        <span className="text-blue-400">(~10% of projected annual upside)</span>
                                    </p>
                                </div>
                            </div>

                            {/* Right: The Guarantee & Call To Action */}
                            <div className="bg-[#1A2332] rounded-xl p-8 border border-gray-700/50 relative">
                                {/* Guarantee Badge */}
                                <div className="absolute top-0 right-0 -mr-2 -mt-2">
                                    <span className="flex h-6 w-6 relative">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-6 w-6 bg-green-500"></span>
                                    </span>
                                </div>

                                <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <span>🛡️</span> The Ironclad Guarantee
                                </h4>
                                <p className="text-gray-300 text-sm leading-relaxed mb-8">
                                    If you do not see a <strong>20% reduction in Handling Time</strong> and a <strong>measurable uplift in conversion</strong> within 90 days, we refund 100% of your payment.
                                    <br /><br />
                                    Furthermore, if at <em>any point</em> in the 12-month term you are dissatisfied with the outcome, you are entitled to a refund for the unused duration.
                                </p>

                                <button
                                    onClick={handleUpgrade}
                                    disabled={!!loading}
                                    className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold text-lg shadow-lg shadow-blue-900/50 transition-all hover:scale-[1.02] active:scale-[0.98]"
                                >
                                    {loading === 'annual' ? 'Processing...' : 'Secure Annual License'}
                                </button>

                                <p className="text-center text-[10px] text-gray-500 mt-4 uppercase tracking-wider">
                                    Limited Availability for {new Date().getFullYear()}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Links */}
                <div className="text-center mt-12 text-sm text-gray-600">
                    <button onClick={handlePortal} className="hover:text-gray-400 underline decoration-gray-700 underline-offset-4">
                        Already a partner? Manage billing
                    </button>
                </div>

            </div>
        </div>
    );
}

function FeatureRow({ text }: { text: string }) {
    return (
        <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-full bg-blue-900/50 flex items-center justify-center border border-blue-800 shrink-0">
                <svg className="w-3 h-3 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
            </div>
            <span className="text-gray-300 font-medium">{text}</span>
        </div>
    );
}
