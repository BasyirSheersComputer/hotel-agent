"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const { login, isDemo, isLoading, error, user } = useAuth();
    const router = useRouter();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [orgSlug, setOrgSlug] = useState("");
    const [loginError, setLoginError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoginError("");

        try {
            await login(email, password, orgSlug);
            router.push("/");
        } catch (err: any) {
            setLoginError(err.message || "Login failed");
        }
    };

    // Redirect if already logged in
    useEffect(() => {
        if (user && !isLoading) {
            if (user.role === 'super_admin') {
                router.push('/super-admin/dashboard');
            } else if (['tenant_admin', 'property_manager', 'admin'].includes(user.role)) {
                router.push('/dashboard');
            } else {
                router.push('/');
            }
        }
    }, [user, isLoading, router]);

    // Pre-fill demo credentials
    useEffect(() => {
        if (isDemo) {
            setEmail("demo@resort-genius.com");
            setPassword("demo123");
            setOrgSlug("demo-hotel");
        }
    }, [isDemo]);

    // If demo mode AND user is authenticated, show demo indicator (success state)
    // If not authenticated, we should fall through to the login form
    if (isDemo && !isLoading && user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
                <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-8 max-w-md w-full text-center border border-slate-700/50">
                    <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl mx-auto mb-6 flex items-center justify-center">
                        <span className="text-2xl">🏨</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2">Resort Genius</h1>
                    <p className="text-cyan-400 mb-6">Demo Mode Active</p>
                    <p className="text-slate-300 mb-8">
                        You are automatically logged in as a demo user.
                        All features are available without authentication.
                    </p>
                    <button
                        onClick={() => router.push("/")}
                        className="w-full py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-xl font-medium hover:from-cyan-400 hover:to-purple-500 transition-all"
                    >
                        Continue to App
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-8 max-w-md w-full border border-slate-700/50">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl mx-auto mb-4 flex items-center justify-center">
                        <span className="text-2xl">🏨</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white">Resort Genius</h1>
                    <p className="text-slate-400 mt-1">Sign in to your account</p>
                </div>

                {/* Error Display */}
                {(loginError || error) && (
                    <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-4 py-3 rounded-xl mb-6">
                        {loginError || error}
                    </div>
                )}

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Organization
                        </label>
                        <input
                            type="text"
                            value={orgSlug}
                            onChange={(e) => setOrgSlug(e.target.value)}
                            placeholder="your-hotel"
                            className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Email
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="block text-sm font-medium text-slate-300">
                                Password
                            </label>
                            <a href="/forgot-password" className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline">
                                Forgot Password?
                            </a>
                        </div>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-xl font-medium hover:from-cyan-400 hover:to-purple-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? "Signing in..." : "Sign In"}
                    </button>
                </form>

                {/* Register Link */}
                <p className="text-center text-slate-400 mt-6">
                    Don&apos;t have an account?{" "}
                    <a href="/register" className="text-cyan-400 hover:text-cyan-300">
                        Sign up
                    </a>
                </p>
            </div>
        </div>
    );
}
