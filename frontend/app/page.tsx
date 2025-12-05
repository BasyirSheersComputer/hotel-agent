"use client";

/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 */
import ChatInterface from "@/components/ChatInterface";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect
  }

  return (
    <main className="min-h-screen relative">
      {/* Header / Logout */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-4">
        <div className="text-slate-400 text-sm hidden md:block">
          {user.name || user.email} ({user.org_slug || "Demo"})
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors border border-slate-700"
        >
          Sign Out
        </button>
      </div>

      <ChatInterface />
    </main>
  );
}
