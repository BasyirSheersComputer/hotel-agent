
"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Check, Loader2 } from 'lucide-react';

const PLANS = [
    {
        id: 'free',
        name: 'Starter',
        price: '$0',
        features: ['1 Property', 'Basic KB', 'Community Support']
    },
    {
        id: 'pro',
        name: 'Professional',
        price: '$49/mo',
        features: ['3 Properties', 'Advanced KB', 'Email Support', 'Analytics']
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: 'Custom',
        features: ['Unlimited Properties', 'White Label', '24/7 Priority Support', 'Dedicated Manager']
    }
];

export default function OnboardingPage() {
    const router = useRouter();
    const { register } = useAuth();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // Form Data
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [orgName, setOrgName] = useState('');
    const [selectedPlan, setSelectedPlan] = useState('free');

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Slugify org name
            const orgSlug = orgName.toLowerCase().replace(/[^a-z0-9]/g, '-');
            await register(email, password, name, orgSlug);
            setStep(2); // Move to Plan Selection
        } catch (err) {
            console.error(err);
            alert("Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handlePayment = async () => {
        setLoading(true);
        // Simulate Stripe Checkout Delay
        setTimeout(() => {
            setLoading(false);
            setStep(3); // Success
        }, 1500);
    };

    const finishOnboarding = () => {
        router.push('/super-admin/dashboard');
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-4 font-sans">
            <div className="w-full max-w-4xl">
                {/* Steps Indicator */}
                <div className="flex justify-center mb-12">
                    {[1, 2, 3].map((s) => (
                        <div key={s} className="flex items-center">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold 
                                ${step >= s ? 'bg-purple-600' : 'bg-slate-800 text-slate-500'}`}>
                                {step > s ? <Check className="h-5 w-5" /> : s}
                            </div>
                            {s < 3 && <div className={`w-20 h-1 ${step > s ? 'bg-purple-600' : 'bg-slate-800'}`} />}
                        </div>
                    ))}
                </div>

                {/* Step 1: Account Creation */}
                {step === 1 && (
                    <div className="bg-slate-900 p-8 rounded-2xl border border-slate-800 max-w-md mx-auto shadow-2xl">
                        <h2 className="text-2xl font-bold mb-6 text-center">Create your Workspace</h2>
                        <form onSubmit={handleRegister} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1 text-slate-400">Organization Name</label>
                                <input type="text" placeholder="e.g. Club Med Bali" value={orgName} onChange={e => setOrgName(e.target.value)} required
                                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent placeholder-slate-600" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1 text-slate-400">Full Name</label>
                                <input type="text" placeholder="John Doe" value={name} onChange={e => setName(e.target.value)} required
                                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent placeholder-slate-600" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1 text-slate-400">Work Email</label>
                                <input type="email" placeholder="john@company.com" value={email} onChange={e => setEmail(e.target.value)} required
                                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent placeholder-slate-600" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1 text-slate-400">Password</label>
                                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
                                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent placeholder-slate-600" />
                            </div>
                            <button type="submit" disabled={loading}
                                className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg transition-colors flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed">
                                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Get Started"}
                            </button>
                        </form>
                    </div>
                )}

                {/* Step 2: Plan Selection */}
                {step === 2 && (
                    <div>
                        <h2 className="text-3xl font-bold text-center mb-10">Select your Plan</h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            {PLANS.map((plan) => (
                                <div key={plan.id} className={`p-6 rounded-2xl border cursor-pointer transition-all
                                    ${selectedPlan === plan.id
                                        ? 'bg-purple-900/20 border-purple-500 ring-2 ring-purple-500/50'
                                        : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
                                    onClick={() => setSelectedPlan(plan.id)}
                                >
                                    <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                                    <div className="text-3xl font-bold mb-6">{plan.price}</div>
                                    <ul className="space-y-3 mb-8">
                                        {plan.features.map((f, i) => (
                                            <li key={i} className="flex items-center text-slate-400">
                                                <Check className="h-4 w-4 mr-2 text-green-500" /> {f}
                                            </li>
                                        ))}
                                    </ul>
                                    <button className={`w-full py-2 rounded-lg font-medium transition-colors
                                        ${selectedPlan === plan.id ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
                                        onClick={(e) => { e.stopPropagation(); setSelectedPlan(plan.id); }}>
                                        {selectedPlan === plan.id ? 'Selected' : 'Choose Plan'}
                                    </button>
                                </div>
                            ))}
                        </div>
                        <div className="mt-8 text-center">
                            <button onClick={handlePayment} disabled={loading}
                                className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold rounded-full shadow-lg transition-transform transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto">
                                {loading ? <Loader2 className="animate-spin" /> : 'Proceed to Checkout'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Success */}
                {step === 3 && (
                    <div className="text-center bg-slate-900 p-12 rounded-3xl border border-slate-800 max-w-lg mx-auto shadow-2xl">
                        <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Check className="h-10 w-10 text-green-500" />
                        </div>
                        <h2 className="text-3xl font-bold mb-4">Welcome Aboard!</h2>
                        <p className="text-slate-400 mb-8">
                            Your workspace <strong>{orgName}</strong> is ready.
                            Start adding your properties and knowledge base to see the magic happen.
                        </p>
                        <button onClick={finishOnboarding} className="px-6 py-3 bg-white text-slate-900 font-bold rounded-lg hover:bg-slate-200 transition-colors">
                            Go to Dashboard
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
