"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, Lock, CreditCard } from 'lucide-react';

export default function CheckoutPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { user } = useAuth();
    const planId = searchParams.get('plan') || 'pro';

    const [loading, setLoading] = useState(false);

    // Simulate payment processing
    const handlePay = async () => {
        setLoading(true);
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Mock success -> In real app, Stripe redirects back to a success URL
        // We will call the backend subscribe API here to actually provision the sub?
        // OR we return to onboarding/success which calls the API. 
        // Let's call the API here to "capture" the payment.

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            // We need email/name. If valid auth, use user. If not, use query or local storage?
            // Since we are in onboarding, we might not be fully logged in yet or we are "registering".
            // The onboarding flow Step 1 creates context state but not DB user yet?
            // Actually onboarding page does:
            // 1. Create Sub mock
            // 2. Create Org (which makes user)

            // So Checkout Page should effectively do Step 1 of the previous Onboarding flow.
            // But Checkout usually happens AFTER user details are collected.
            // Onboarding page passes state via URL or LocalStorage?
            // For simplicity, we'll assume the Onboarding Page 'handlePayment' calls this page, 
            // and this page simply redirects back to Onboarding with ?status=success&sub_id=mock_sub_123

            const info = localStorage.getItem('onboarding_info');
            const { email, name } = info ? JSON.parse(info) : { email: 'demo@user.com', name: 'Demo User' };

            const res = await fetch(`${API_URL}/api/billing/subscribe`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, name, plan_id: planId })
            });

            if (res.ok) {
                const data = await res.json();
                // Redirect back to onboarding success step
                router.push(`/onboarding?step=3&sub_id=${data.subscription_id}`);
            } else {
                alert("Payment failed");
            }

        } catch (e) {
            console.error(e);
            alert("Payment error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#f7f9fc] flex flex-col font-sans text-[#30313d]">
            {/* Stripe-like Header */}
            <div className="p-6 border-b border-gray-200 bg-white flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <div className="font-bold text-xl tracking-tight text-slate-900">Stripe</div>
                    <div className="h-4 w-[1px] bg-slate-300 mx-2"></div>
                    <div className="text-slate-500 font-medium">Resort Genius</div>
                </div>
                <div className="text-slate-500 text-sm font-medium">
                    Test Mode
                </div>
            </div>

            <div className="flex-1 flex flex-col md:flex-row max-w-5xl mx-auto w-full p-8 gap-12">
                {/* Left: Product Info */}
                <div className="flex-1 pt-8 order-2 md:order-1">
                    <div className="text-slate-500 font-medium mb-2">Subscribe to</div>
                    <h1 className="text-3xl font-bold mb-4">Resort Genius Professional</h1>
                    <div className="text-5xl font-bold mb-2">RM 10,000.00</div>
                    <div className="text-slate-500 mb-8">per month</div>

                    <div className="space-y-4">
                        <div className="flex justify-between py-3 border-t border-gray-200">
                            <span className="font-medium">Resort Genius Professional Plan</span>
                            <span>RM 10,000.00</span>
                        </div>
                        <div className="flex justify-between py-3 border-t border-gray-200">
                            <span className="font-medium text-slate-500">Subtotal</span>
                            <span className="font-medium">RM 10,000.00</span>
                        </div>
                        <div className="flex justify-between py-3 border-t border-b border-gray-200 text-lg font-bold">
                            <span>Total due today</span>
                            <span>RM 10,000.00</span>
                        </div>
                    </div>
                </div>

                {/* Right: Payment Form */}
                <div className="flex-1 bg-white p-8 rounded-lg shadow-sm border border-gray-200 h-fit order-1 md:order-2">
                    <h2 className="text-xl font-bold mb-6">Pay with card</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                            <input type="email" value="rich@estates.com" readOnly className="w-full p-3 border border-gray-300 rounded-md bg-gray-50 text-slate-500" />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Card Information</label>
                            <div className="border border-gray-300 rounded-md overflow-hidden">
                                <div className="p-3 border-b border-gray-300 flex items-center gap-3">
                                    <CreditCard className="text-slate-400 h-5 w-5" />
                                    <input type="text" placeholder="Number" className="flex-1 outline-none" defaultValue="4242 4242 4242 4242" />
                                </div>
                                <div className="flex">
                                    <input type="text" placeholder="MM / YY" className="flex-1 p-3 border-r border-gray-300 outline-none" defaultValue="12 / 24" />
                                    <input type="text" placeholder="CVC" className="w-24 p-3 outline-none" defaultValue="123" />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Name on card</label>
                            <input type="text" placeholder="Name on card" className="w-full p-3 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-[#635bff]" defaultValue="Mr Rich" />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Country or region</label>
                            <select className="w-full p-3 border border-gray-300 rounded-md bg-white">
                                <option>Malaysia</option>
                                <option>United States</option>
                            </select>
                        </div>

                        <button
                            onClick={handlePay}
                            disabled={loading}
                            className="w-full py-4 mt-4 bg-[#635bff] hover:bg-[#534ac2] text-white font-bold rounded-md transition-colors flex justify-center items-center"
                        >
                            {loading ? <Loader2 className="animate-spin" /> : "Subscribe"}
                        </button>

                        <div className="flex items-center justify-center gap-2 text-slate-400 text-xs mt-4">
                            <Lock className="h-3 w-3" />
                            Payments are secure and encrypted
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
