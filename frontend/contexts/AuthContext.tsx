"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

// API URL from environment - smart default for local dev
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface User {
    user_id: string;
    email: string;
    name: string | null;
    role: string;
    org_id: string;
    org_slug: string | null;
    property_id: string | null;
    property_name: string | null;
    is_demo: boolean;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    isDemo: boolean;
    error: string | null;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string, orgSlug: string) => Promise<void>;
    logout: () => void;
    register: (email: string, password: string, name: string, orgSlug: string) => Promise<void>;
    checkAuthStatus: () => Promise<void>;
    switchProperty: (propertyId: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [state, setState] = useState<AuthState>({
        user: null,
        token: null,
        isLoading: true,
        isDemo: true,
        error: null,
    });

    // Check auth status on mount
    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            // Check if backend is in demo mode
            const statusRes = await fetch(`${API_URL}/api/auth/status`);
            const statusData = await statusRes.json();

            if (statusData.demo_mode) {
                // Demo mode - auto-login with demo user
                const loginRes = await fetch(`${API_URL}/api/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: "demo@resort-genius.com",
                        password: "demo",
                        org_slug: "demo-hotel"
                    }),
                });

                if (loginRes.ok) {
                    const data = await loginRes.json();
                    localStorage.setItem("token", data.access_token);
                    setState({
                        user: data.user,
                        token: data.access_token,
                        isLoading: false,
                        isDemo: true,
                        error: null,
                    });
                    return;
                }
            }

            // SaaS mode - check for existing token
            const storedToken = localStorage.getItem("token");
            if (storedToken) {
                const meRes = await fetch(`${API_URL}/api/auth/me`, {
                    headers: { Authorization: `Bearer ${storedToken}` },
                });

                if (meRes.ok) {
                    const user = await meRes.json();
                    setState({
                        user,
                        token: storedToken,
                        isLoading: false,
                        isDemo: user.is_demo,
                        error: null,
                    });
                    return;
                }
            }

            // No valid auth - clear state
            setState({
                user: null,
                token: null,
                isLoading: false,
                isDemo: statusData.demo_mode,
                error: null,
            });
        } catch (error) {
            console.error("Auth check failed:", error);
            setState(prev => ({ ...prev, isLoading: false, error: "Failed to connect" }));
        }
    };

    const login = async (email: string, password: string, orgSlug: string) => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        try {
            const res = await fetch(`${API_URL}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, org_slug: orgSlug }),
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || "Login failed");
            }

            const data = await res.json();
            localStorage.setItem("token", data.access_token);

            setState({
                user: data.user,
                token: data.access_token,
                isLoading: false,
                isDemo: data.user.is_demo,
                error: null,
            });
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : "Login failed";
            setState(prev => ({
                ...prev,
                isLoading: false,
                error: errorMessage,
            }));
            throw error;
        }
    };

    const register = async (email: string, password: string, name: string, orgSlug: string) => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        try {
            const res = await fetch(`${API_URL}/api/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, name, org_slug: orgSlug }),
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || "Registration failed");
            }

            const data = await res.json();
            localStorage.setItem("token", data.access_token);

            setState({
                user: data.user,
                token: data.access_token,
                isLoading: false,
                isDemo: data.user.is_demo,
                error: null,
            });
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : "Registration failed";
            setState(prev => ({
                ...prev,
                isLoading: false,
                error: errorMessage,
            }));
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setState({
            user: null,
            token: null,
            isLoading: false,
            isDemo: state.isDemo,
            error: null,
        });
    };

    // Switch active property context
    const switchProperty = async (propertyId: string) => {
        // Ideally verify property access via API or update user session
        // For now, we update local state optimistically or re-fetch me
        // Note: Token might need refresh if scopes change, but standard JWT usually just has org_id
        console.log("Switching to property:", propertyId);
        // Re-fetch user to confirm access/update context if backend facilitates it
        await checkAuthStatus();
    };

    return (
        <AuthContext.Provider value={{ ...state, login, logout, register, checkAuthStatus, switchProperty }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}

// Helper hook to get auth headers for API requests
export function useAuthHeaders() {
    const { token } = useAuth();
    return token ? { Authorization: `Bearer ${token}` } : {};
}
