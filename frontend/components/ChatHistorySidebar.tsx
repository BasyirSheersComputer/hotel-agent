"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useEffect, useState } from "react";

interface ChatSession {
    session_id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

interface ChatHistorySidebarProps {
    currentSessionId?: string | null;
    onSessionSelect: (sessionId: string) => void;
    onNewChat: () => void;
}

export default function ChatHistorySidebar({
    currentSessionId,
    onSessionSelect,
    onNewChat,
}: ChatHistorySidebarProps) {
    const { token } = useAuth();
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const loadSessions = async () => {
        if (!token) return;

        try {
            const response = await fetch("/api/history/sessions", {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (!response.ok) throw new Error("Failed to load sessions");
            const data = await response.json();
            setSessions(data);
        } catch (error) {
            console.error("Error loading sessions:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadSessions();
    }, [token]);

    const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation();

        if (!confirm("Delete this conversation?")) return;

        try {
            const response = await fetch(`/api/history/session/${sessionId}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` },
            });

            if (!response.ok) throw new Error("Failed to delete session");

            // Refresh sessions list
            await loadSessions();

            // If deleted session is current, trigger new chat
            if (currentSessionId === sessionId) {
                onNewChat();
            }
        } catch (error) {
            console.error("Error deleting session:", error);
        }
    };

    return (
        <div className="w-64 h-screen border-r border-gray-700 bg-gray-900 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-700">
                <button
                    onClick={onNewChat}
                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
                >
                    + New Chat
                </button>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-2">
                {isLoading ? (
                    <div className="text-gray-400 text-center p-4">Loading...</div>
                ) : sessions.length === 0 ? (
                    <div className="text-gray-500 text-center p-4 text-sm">
                        No conversations yet
                    </div>
                ) : (
                    sessions.map((session) => (
                        <div
                            key={session.session_id}
                            onClick={() => onSessionSelect(session.session_id)}
                            className={`p-3 mb-2 rounded-lg cursor-pointer transition group ${currentSessionId === session.session_id
                                    ? "bg-gray-700 text-white"
                                    : "hover:bg-gray-800 text-gray-300"
                                }`}
                        >
                            <div className="flex justify-between items-start">
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium truncate">{session.title}</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {new Date(session.updated_at).toLocaleDateString()}
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => handleDeleteSession(session.session_id, e)}
                                    className="opacity-0 group-hover:opacity-100 ml-2 text-gray-500 hover:text-red-500 transition"
                                    title="Delete conversation"
                                >
                                    ×
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
