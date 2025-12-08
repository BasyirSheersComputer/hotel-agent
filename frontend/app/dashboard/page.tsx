/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 */
"use client";
import dynamic from "next/dynamic";

const Dashboard = dynamic(() => import("@/components/Dashboard"), { ssr: false });

export default function DashboardPage() {
    return <Dashboard />;
}
