"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
    CreditCard,
    BarChart3,
    Settings,
    HelpCircle,
    Menu,
    X,
    LogOut,
    AlertTriangle
} from 'lucide-react';
import { useAuth, useAuthHeaders } from '@/contexts/AuthContext';

interface BillingSidebarProps {
    onCollapse: (collapsed: boolean) => void;
}

export default function BillingSidebar({ onCollapse }: BillingSidebarProps) {
    const [isOpen, setIsOpen] = useState(true);
    const [showUnsubscribeModal, setShowUnsubscribeModal] = useState(false);
    const pathname = usePathname();
    const router = useRouter();
    const { logout } = useAuth();
    const authHeaders = useAuthHeaders();
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
        onCollapse(!isOpen);
    };

    const handleUnsubscribe = async () => {
        try {
            const res = await fetch(`${API_URL}/api/billing/unsubscribe`, {
                method: "POST",
                headers: authHeaders as HeadersInit
            });

            if (res.ok) {
                alert("Subscription canceled. Access will be revoked at the end of the billing period.");
                // Redirect to survey or logout
                logout();
                router.push('/login');
            } else {
                alert("Failed to cancel subscription.");
            }
        } catch (e) {
            console.error(e);
            alert("Error connecting to server.");
        }
    };

    const menuItems = [
        { name: 'Overview', icon: CreditCard, href: '/billing' },
        { name: 'Usage Metrics', icon: BarChart3, href: '/billing?tab=usage' },
        { name: 'Properties', icon: Menu, href: '/billing?tab=properties' },
        { name: 'Support', icon: HelpCircle, href: '/billing?tab=support' },
        { name: 'Settings', icon: Settings, href: '/billing?tab=settings' },
    ];

    return (
        <>
            {/* Mobile Toggle */}
            <button
                className="md:hidden fixed top-4 left-4 z-50 p-2 bg-slate-800 rounded-lg text-white"
                onClick={toggleSidebar}
            >
                {isOpen ? <X /> : <Menu />}
            </button>

            {/* Sidebar Container */}
            <div className={`
        fixed top-0 left-0 h-full bg-slate-900 border-r border-slate-800 transition-all duration-300 z-40
        ${isOpen ? 'w-64' : 'w-20'} 
        flex flex-col
      `}>
                {/* Header */}
                <div className="p-6 flex items-center justify-between border-b border-slate-800 h-20">
                    {isOpen && <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Billing</h1>}
                    <button onClick={toggleSidebar} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hidden md:block">
                        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 py-6 px-3 space-y-2">
                    {menuItems.map((item) => (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={`
                        flex items-center px-4 py-3 rounded-lg transition-colors
                        ${pathname === item.href || (pathname === '/billing' && item.href === '/billing') // Simple active check
                                    ? 'bg-purple-600/10 text-purple-400'
                                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'}
                    `}
                        >
                            <item.icon className="h-5 w-5 min-w-[20px]" />
                            {isOpen && <span className="ml-3 font-medium truncate">{item.name}</span>}
                        </Link>
                    ))}
                </nav>

                {/* Footer / Logout */}
                <div className="p-4 border-t border-slate-800">
                    <button
                        onClick={logout}
                        className={`
                    flex items-center w-full px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors
                    ${!isOpen && 'justify-center'}
                `}
                    >
                        <LogOut className="h-5 w-5" />
                        {isOpen && <span className="ml-3 font-medium">Log out</span>}
                    </button>
                </div>
            </div>

            {/* Main Content Padding Adjuster */}
            {/* This component just renders the sidebar, the parent layout handles padding */}

            {/* Confirmation Modal */}
            {showUnsubscribeModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="bg-slate-900 max-w-md w-full rounded-2xl border border-slate-800 p-6 shadow-2xl">
                        <div className="flex items-center justify-center w-12 h-12 bg-red-500/20 rounded-full mb-4 mx-auto">
                            <AlertTriangle className="h-6 w-6 text-red-500" />
                        </div>
                        <h3 className="text-xl font-bold text-center mb-2 text-white">Cancel Subscription?</h3>
                        <p className="text-slate-400 text-center mb-6">
                            Are you sure? This will revoke access to all properties, data, and dashboard features immediately.
                            This action cannot be undone.
                        </p>
                        <div className="flex space-x-3">
                            <button
                                onClick={() => setShowUnsubscribeModal(false)}
                                className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg transition-colors"
                            >
                                Keep Plan
                            </button>
                            <button
                                onClick={handleUnsubscribe}
                                className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors"
                            >
                                Confirm Cancellation
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
