"use client";

/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 * 
 * Admin KB Management Page
 * Allows admins to upload, view, and delete knowledge base documents.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import DocumentManager from "@/components/DocumentManager";

export default function AdminPage() {
    const { user, isLoading, isDemo } = useAuth();
    const router = useRouter();
    const [accessDenied, setAccessDenied] = useState(false);

    useEffect(() => {
        if (!isLoading) {
            // Check if user is admin
            if (!user) {
                router.push("/login");
            } else if (user.role !== "admin" && !accessDenied) {
                setAccessDenied(true);
            }
        }
    }, [user, isLoading, router, accessDenied]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-gray-500 text-xl font-medium">Loading...</div>
            </div>
        );
    }

    if (accessDenied) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="bg-white border border-red-200 rounded-xl p-8 shadow-sm max-w-md text-center">
                    <div className="text-4xl mb-4">🔒</div>
                    <h2 className="text-xl font-semibold text-red-600 mb-2">Access Denied</h2>
                    <p className="text-gray-600 mb-6">
                        Only administrators can access the KB Management page.
                    </p>
                    <button
                        onClick={() => router.push("/")}
                        className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium"
                    >
                        Back to Chat
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-slate-200 px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">Knowledge Base Management</h1>
                        <p className="text-slate-500 text-sm mt-1">
                            Upload and manage documents for your AI assistant
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        {isDemo && (
                            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
                                Demo Mode
                            </span>
                        )}
                        <button
                            onClick={() => router.push("/")}
                            className="px-4 py-2 text-slate-600 hover:text-slate-900 font-medium"
                        >
                            ← Back to Chat
                        </button>
                        <button
                            onClick={() => router.push("/dashboard")}
                            className="px-4 py-2 text-slate-600 hover:text-slate-900 font-medium"
                        >
                            Analytics
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                <DocumentManager isDemo={isDemo} />
            </div>
        </div>
    );
}
