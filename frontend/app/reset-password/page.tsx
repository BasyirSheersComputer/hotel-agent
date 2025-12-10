"use client";

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

function ResetPasswordForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get('token');

    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (password !== confirm) {
            setStatus('error');
            setMessage("Passwords do not match");
            return;
        }

        if (!token) {
            setStatus('error');
            setMessage("Missing reset token");
            return;
        }

        setStatus('loading');
        setMessage('');

        try {
            const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiBase}/api/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password: password })
            }); //Fixed syntax error in prev tool call logic? No, assuming fetch is standard.

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || 'Reset failed');

            setStatus('success');
            setMessage("Password successfully reset! Redirecting to login...");

            setTimeout(() => {
                router.push('/login');
            }, 3000);
        } catch (err: any) {
            setStatus('error');
            setMessage(err.message);
        }
    };

    if (!token) {
        return (
            <div className="text-center text-white">
                <p className="mb-4">Invalid Link.</p>
                <Link href="/login" className="text-blue-400 hover:underline">Return to Login</Link>
            </div>
        );
    }

    return (
        <div className="bg-white/10 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-white/20 w-full max-w-md">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Set New Password</h1>
                <p className="text-gray-300">Enter your new secure password</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {status === 'error' && (
                    <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
                        {message}
                    </div>
                )}
                {status === 'success' && (
                    <div className="p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-200 text-sm">
                        {message}
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">New Password</label>
                    <input
                        type="password"
                        required
                        minLength={6}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white placeholder-gray-500 transition-all"
                        placeholder="••••••••"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                    <input
                        type="password"
                        required
                        minLength={6}
                        value={confirm}
                        onChange={(e) => setConfirm(e.target.value)}
                        className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white placeholder-gray-500 transition-all"
                        placeholder="••••••••"
                    />
                </div>

                <button
                    type="submit"
                    disabled={status === 'loading' || status === 'success'}
                    className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-lg shadow-lg hover:shadow-blue-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {status === 'loading' ? 'Updating...' : 'Set Password'}
                </button>
            </form>
        </div>
    );
}

export default function ResetPasswordPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
            <Suspense fallback={<div className="text-white">Loading...</div>}>
                <ResetPasswordForm />
            </Suspense>
        </div>
    );
}
