"use client";

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginForm() {
    const { login, register } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Login State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [orgSlug, setOrgSlug] = useState('demo-hotel');

    // Register State
    const [orgName, setOrgName] = useState('');
    const [regOrgSlug, setRegOrgSlug] = useState('');
    const [adminName, setAdminName] = useState('');
    const [adminEmail, setAdminEmail] = useState('');
    const [adminPassword, setAdminPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await login(email, password, orgSlug);
            } else {
                await register(orgName, regOrgSlug, adminEmail, adminPassword, adminName);
            }
        } catch (err: any) {
            setError(err.message || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg">
            <div className="text-center">
                <h2 className="text-3xl font-bold text-slate-800">
                    {isLogin ? 'Welcome Back' : 'Start Free Trial'}
                </h2>
                <p className="mt-2 text-slate-600">
                    {isLogin ? 'Sign in to Resort Genius' : 'Create your organization account'}
                </p>
            </div>

            {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg border border-red-200">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                {isLogin ? (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Organization ID</label>
                            <input
                                type="text"
                                required
                                value={orgSlug}
                                onChange={(e) => setOrgSlug(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g. demo-hotel"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Email</label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </>
                ) : (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Organization Name</label>
                            <input
                                type="text"
                                required
                                value={orgName}
                                onChange={(e) => setOrgName(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g. Club Med Cherating"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Organization Slug (ID)</label>
                            <input
                                type="text"
                                required
                                value={regOrgSlug}
                                onChange={(e) => setRegOrgSlug(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g. club-med-cherating"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Admin Name</label>
                            <input
                                type="text"
                                required
                                value={adminName}
                                onChange={(e) => setAdminName(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Admin Email</label>
                            <input
                                type="email"
                                required
                                value={adminEmail}
                                onChange={(e) => setAdminEmail(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700">Password</label>
                            <input
                                type="password"
                                required
                                value={adminPassword}
                                onChange={(e) => setAdminPassword(e.target.value)}
                                className="w-full px-4 py-2 mt-1 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                    {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                </button>
            </form>

            <div className="text-center">
                <button
                    onClick={() => {
                        setIsLogin(!isLogin);
                        setError('');
                    }}
                    className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
                >
                    {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
                </button>
            </div>

            {isLogin && (
                <div className="mt-4 p-4 bg-slate-50 rounded-lg text-xs text-slate-500">
                    <p className="font-semibold mb-1">Demo Credentials:</p>
                    <p>Org ID: demo-hotel</p>
                    <p>Email: admin@demo-hotel.com</p>
                    <p>Password: admin123</p>
                </div>
            )}
        </div>
    );
}
