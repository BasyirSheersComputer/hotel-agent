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
    <main className="min-h-screen relative flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200 p-0 md:p-4">
      <ChatInterface user={user} onLogout={logout} />
    </main>
  );
}
