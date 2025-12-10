"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import LanguageSelector from "./LanguageSelector";

// API URL from environment - smart default for local dev
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Language storage key
const LANGUAGE_STORAGE_KEY = "resort_genius_language";

interface Message {
    role: "user" | "agent";
    content: string;
    sources?: string[];

    detectedLanguage?: string;
}

interface ChatSession {
    session_id: string;
    title: string;
    updated_at: string;
}

interface ChatInterfaceProps {
    user?: {
        name?: string | null;
        email?: string | null;
        org_slug?: string | null;
    } | null;
    onLogout?: () => void;
}

export default function ChatInterface({ user, onLogout }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState("en");
    const [isHeaderVisible, setIsHeaderVisible] = useState(true);
    const [isHistoryOpen, setIsHistoryOpen] = useState(false); // Drawer state
    // Sidebar is always visible on desktop now

    // History state
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [isHistoryLoading, setIsHistoryLoading] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const lastScrollTop = useRef(0);

    // Load saved language preference
    useEffect(() => {
        const savedLang = localStorage.getItem(LANGUAGE_STORAGE_KEY);
        if (savedLang) {
            setLanguage(savedLang);
        }
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            const token = localStorage.getItem("token");
            if (!token) return;

            const response = await fetch(`${API_URL}/api/history/sessions`, {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setSessions(data);
            }
        } catch (error) {
            console.error("Failed to fetch history:", error);
        }
    };

    const loadSession = async (sessionId: string) => {
        if (currentSessionId === sessionId) return;

        try {
            setIsHistoryLoading(true);
            const token = localStorage.getItem("token");
            const response = await fetch(`${API_URL}/api/history/session/${sessionId}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                const loadedMessages: Message[] = data.map((msg: { role: string; content: string }) => ({
                    role: msg.role === "assistant" ? "agent" : msg.role as "user" | "agent",
                    content: msg.content
                })).reverse();

                setMessages(loadedMessages);
                setCurrentSessionId(sessionId);
            }
        } catch (error) {
            console.error("Failed to load session:", error);
        } finally {
            setIsHistoryLoading(false);
        }
    };

    const createNewSession = () => {
        setMessages([]);
        setCurrentSessionId(null);
        setInput("");
    };

    // Save language preference
    const handleLanguageChange = (newLang: string) => {
        setLanguage(newLang);
        localStorage.setItem(LANGUAGE_STORAGE_KEY, newLang);
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const sendMessage = async (queryOverride?: string) => {
        const query = queryOverride || input;
        if (!query.trim()) return;

        const userMessage: Message = { role: "user", content: query };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            // Use configured API URL with language parameter
            const token = localStorage.getItem("token");
            const response = await fetch(`${API_URL}/api/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    query: userMessage.content,
                    language: language !== "en" ? language : undefined,  // Only send if not English
                    session_id: currentSessionId // Send current session ID if exists
                }),
            });

            if (!response.ok) throw new Error("Network response was not ok");

            const data = await response.json();
            const agentMessage: Message = {
                role: "agent",
                content: data.answer,
                sources: data.sources,
                detectedLanguage: data.detected_language,
            };
            setMessages((prev) => [...prev, agentMessage]);

            // Update session ID if new
            if (data.session_id && data.session_id !== currentSessionId) {
                setCurrentSessionId(data.session_id);
                fetchSessions(); // Refresh list to show new session
            }
        } catch (error) {
            console.error("Error:", error);
            setMessages((prev) => [
                ...prev,
                { role: "agent", content: `I apologize, but I seem to be offline. Please check your connection. (Error: ${error instanceof Error ? error.message : String(error)})` },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleQuickQuery = (query: string) => {
        sendMessage(query);
    };

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const { scrollTop } = e.currentTarget;
        // Only toggle on mobile (check width or just rely on CSS classes to disable effect on desktop)
        // We'll update state regardless, but CSS will control visibility
        if (scrollTop > lastScrollTop.current && scrollTop > 10) {
            setIsHeaderVisible(false);
        } else if (scrollTop < lastScrollTop.current) {
            setIsHeaderVisible(true);
        }
        lastScrollTop.current = scrollTop;
    };

    return (
        <div className="flex w-full max-w-[1400px] h-[100dvh] md:h-[90vh] bg-white/85 backdrop-blur-[20px] rounded-none md:rounded-[24px] shadow-[0_8px_30px_rgba(0,0,0,0.05)] border-0 md:border border-white/40 overflow-hidden flex-col md:flex-row transition-all duration-300 relative">
            {/* Sidebar */}
            {/* Sidebar */}
            {/* Sidebar - Static on Desktop */}
            <aside className="hidden md:flex w-[320px] bg-white/50 border-r border-black/5 flex-col gap-4 p-8 pb-32 overflow-hidden z-40">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-[#0F4C81] text-white rounded-full flex items-center justify-center font-serif font-bold text-xl shrink-0">
                        RG
                    </div>
                    <h1 className="text-2xl font-serif font-semibold text-[#0F4C81] whitespace-nowrap">Resort Genius</h1>
                </div>

                <div className="bg-gradient-to-br from-[#0F4C81] to-[#1A5F9A] text-white p-6 rounded-[16px] shadow-[0_4px_6px_rgba(0,0,0,0.05)]">
                    <h2 className="text-lg font-serif font-semibold mb-2">Club Med Cherating</h2>
                    <p className="text-sm opacity-90 flex items-center gap-2">
                        <span className="w-2 h-2 bg-[#48BB78] rounded-full shadow-[0_0_0_2px_rgba(72,187,120,0.3)]"></span>
                        Concierge Online
                    </p>
                </div>

                <div className="flex-1" />

                <nav>
                    <h3 className="text-sm uppercase tracking-wider text-gray-500 mb-4 font-semibold">Quick Assist</h3>
                    <div className="flex flex-col gap-2">
                        <button onClick={() => handleQuickQuery('What are the check-in and check-out times?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🕒</span> Check-in / Check-out
                        </button>
                        <button onClick={() => handleQuickQuery('What are the restaurant operating hours?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🍽️</span> Dining Hours
                        </button>
                        <button onClick={() => handleQuickQuery('What activities are available today?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🏄</span> Activities
                        </button>
                    </div>
                </nav>
            </aside >

            {/* Desktop Sidebar Footer (User Profile) */}
            <div className="hidden md:flex absolute bottom-0 left-0 w-[320px] p-8 border-t border-black/5 bg-white/50 backdrop-blur-sm items-center justify-between z-20">
                <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 rounded-full bg-[#0F4C81] text-white flex items-center justify-center text-xs font-bold shrink-0">
                        {user?.name?.[0] || user?.email?.[0] || "U"}
                    </div>
                    <div className="flex flex-col min-w-0">
                        <span className="text-sm font-semibold text-[#1A202C] truncate">{user?.name || user?.email}</span>
                        <span className="text-xs text-gray-500 truncate">{user?.org_slug || "Demo Org"}</span>
                    </div>
                </div>
                <button
                    onClick={onLogout}
                    className="p-2 text-gray-500 hover:text-[#0F4C81] hover:bg-black/5 rounded-lg transition-colors"
                    title="Sign Out"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <polyline points="16 17 21 12 16 7" />
                        <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                </button>
            </div >

            {/* Main Chat Area */}
            < main className="flex-1 flex flex-col bg-white/30" >
                <header className={`
                    border-b border-black/5 bg-white/50 flex justify-between items-center
                    transition-all duration-300 ease-in-out overflow-hidden
                    ${isHeaderVisible ? 'max-h-24 p-4 opacity-100' : 'max-h-0 p-0 border-0 opacity-0'}
                    md:max-h-none md:p-6 md:px-8 md:opacity-100 md:border-b
                `}>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsHistoryOpen(!isHistoryOpen)}
                            className="p-2 -ml-2 text-gray-500 hover:text-[#0F4C81] hover:bg-black/5 rounded-lg transition-colors"
                        >
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="3" y1="12" x2="21" y2="12"></line>
                                <line x1="3" y1="6" x2="21" y2="6"></line>
                                <line x1="3" y1="18" x2="21" y2="18"></line>
                            </svg>
                        </button>
                        <div>
                            <h2 className="text-[#0F4C81] text-xl md:text-2xl font-serif font-semibold">Guest Assistance</h2>
                            <p className="text-gray-500 text-sm md:text-base hidden md:block">Ask me anything about the resort or local area</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <LanguageSelector
                            selectedLanguage={language}
                            onLanguageChange={handleLanguageChange}
                            compact={true}
                        />
                        {/* Mobile Logout */}
                        <button
                            onClick={onLogout}
                            className="md:hidden p-2 text-gray-500 hover:text-[#0F4C81] hover:bg-black/5 rounded-lg transition-colors"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                                <polyline points="16 17 21 12 16 7" />
                                <line x1="21" y1="12" x2="9" y2="12" />
                            </svg>
                        </button>
                    </div>
                </header>

                <div
                    className="flex-1 overflow-y-auto min-h-0 p-4 md:p-8 flex flex-col gap-4 md:gap-6 scroll-smooth"
                    onScroll={handleScroll}
                >
                    {messages.length === 0 && (
                        <div className="flex gap-4 max-w-[80%] animate-[fadeIn_0.3s_ease-out]">
                            <div className="w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0 bg-[#0F4C81] text-white flex items-center justify-center font-bold text-xs">
                                RG
                            </div>
                            <div className="bg-white text-[#1A202C] p-6 rounded-[16px] rounded-tl-none shadow-[0_4px_6px_rgba(0,0,0,0.05)] relative text-sm md:text-base leading-relaxed">
                                <p>Welcome to Club Med Cherating! I'm your personal AI concierge. How can I assist you with your stay today?</p>
                                <span className="block text-[0.7rem] mt-1.5 opacity-70">Just now</span>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`flex gap-4 max-w-[80%] animate-[fadeIn_0.3s_ease-out] ${msg.role === "user" ? "self-end flex-row-reverse" : "self-start"}`}
                        >
                            <div className={`w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0 flex items-center justify-center font-bold text-xs ${msg.role === 'agent' ? 'bg-[#0F4C81] text-white' : 'bg-[#D4AF37] text-white'}`}>
                                {msg.role === 'agent' ? 'RG' : 'G'}
                            </div>
                            <div className={`p-6 rounded-[16px] shadow-[0_4px_6px_rgba(0,0,0,0.05)] relative text-sm md:text-base leading-relaxed ${msg.role === "user"
                                ? "bg-[#0F4C81] text-white rounded-tr-none"
                                : "bg-white text-[#1A202C] rounded-tl-none"
                                }`}>
                                {msg.role === "user" ? (
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                ) : (
                                    <div className="prose prose-sm max-w-none">
                                        <ReactMarkdown
                                            components={{
                                                strong: (props) => <strong className="font-semibold text-inherit" {...props} />,
                                                ul: (props) => <ul className="ml-5 my-2 list-disc" {...props} />,
                                                li: (props) => <li className="mb-1" {...props} />,
                                                p: (props) => <p className="mb-2 last:mb-0" {...props} />,
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                )}
                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-black/10">
                                        <p className="text-xs font-semibold opacity-80 mb-1">Sources:</p>
                                        <ul className="text-xs opacity-70 space-y-0.5">
                                            {msg.sources.map((src, i) => (
                                                <li key={i} className="truncate">📄 {src.split(/[/\\]/).pop()}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                <span className="block text-[0.7rem] mt-1.5 opacity-70">
                                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-4 max-w-[80%] animate-[fadeIn_0.3s_ease-out]">
                            <div className="w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0 bg-[#0F4C81] text-white flex items-center justify-center font-bold text-xs">
                                RG
                            </div>
                            <div className="bg-white text-[#1A202C] p-6 rounded-[16px] rounded-tl-none shadow-[0_4px_6px_rgba(0,0,0,0.05)] relative">
                                <div className="flex gap-1 py-1">
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_both_-0.32s]"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_both_-0.16s]"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_both]"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 md:p-8 bg-white border-t border-black/5">
                    <div className="flex gap-4 bg-[#F0F4F8] p-2 rounded-[24px] border border-black/5 focus-within:bg-white focus-within:border-[#1A5F9A] focus-within:shadow-[0_0_0_3px_rgba(15,76,129,0.1)] transition-all">
                        <input
                            type="text"
                            className="flex-1 border-none bg-transparent px-6 py-4 font-sans text-base outline-none text-[#1A202C] placeholder:text-gray-500"
                            placeholder="Type your question here..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        />
                        <button
                            onClick={() => sendMessage()}
                            disabled={isLoading || !input.trim()}
                            className="w-12 h-12 bg-[#0F4C81] text-white rounded-full flex items-center justify-center hover:bg-[#1A5F9A] hover:scale-105 disabled:bg-gray-500 disabled:cursor-not-allowed disabled:transform-none transition-all"
                            aria-label="Send message"
                        >
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                </div>
            </main >
            {/* History Drawer Overlay */}
            <HistoryDrawer
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
                sessions={sessions}
                currentSessionId={currentSessionId}
                onLoadSession={(id: string) => {
                    loadSession(id);
                    setIsHistoryOpen(false);
                }}
                onCreateSession={() => {
                    createNewSession();
                    setIsHistoryOpen(false);
                }}
            />
        </div>
    );
}

interface HistoryDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    sessions: ChatSession[];
    currentSessionId: string | null;
    onLoadSession: (id: string) => void;
    onCreateSession: () => void;
}

function HistoryDrawer({ isOpen, onClose, sessions, currentSessionId, onLoadSession, onCreateSession }: HistoryDrawerProps) {
    if (!isOpen) return null;

    return (
        <div className="absolute inset-0 z-50 flex overflow-hidden">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm animate-[fadeIn_0.2s_ease-out]" onClick={onClose} />

            {/* Drawer Panel */}
            <div className="relative w-full max-w-[320px] bg-[#F8FAFC] shadow-[4px_0_24px_rgba(0,0,0,0.1)] flex flex-col h-full animate-[slideIn_0.3s_cubic-bezier(0.16,1,0.3,1)] border-r border-white/50">
                <div className="p-6 border-b border-black/5 flex justify-between items-center bg-white/50 backdrop-blur-md">
                    <div className="flex items-center gap-3 text-[#0F4C81] font-serif font-bold text-xl">
                        <span className="text-2xl">📁</span> History
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-black/5 rounded-full transition-colors text-gray-500 hover:text-red-500">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>

                <div className="p-4">
                    <button
                        onClick={onCreateSession}
                        className="w-full py-3 bg-[#0F4C81] text-white rounded-[16px] font-medium hover:bg-[#1A5F9A] hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-[0_4px_10px_rgba(15,76,129,0.2)]"
                    >
                        <span className="text-lg font-bold">+</span> Start New Chat
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 px-2">Recent Sessions</h3>
                    {sessions.map((session) => (
                        <button
                            key={session.session_id}
                            onClick={() => onLoadSession(session.session_id)}
                            className={`w-full text-left p-4 rounded-[12px] transition-all border group relative overflow-hidden ${currentSessionId === session.session_id
                                ? 'bg-white border-[#0F4C81]/20 shadow-md transform scale-[1.02] z-10'
                                : 'bg-white/50 border-transparent hover:bg-white hover:border-black/5 hover:shadow-sm'
                                }`}
                        >
                            {currentSessionId === session.session_id && (
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#0F4C81]" />
                            )}
                            <div className={`truncate mb-1 font-medium ${currentSessionId === session.session_id ? 'text-[#0F4C81]' : 'text-gray-700 group-hover:text-[#0F4C81]'}`}>
                                {session.title}
                            </div>
                            <div className="text-[10px] opacity-50 flex items-center gap-1">
                                <span>📅</span> {new Date(session.updated_at).toLocaleDateString()}
                            </div>
                        </button>
                    ))}
                    {sessions.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-12 opacity-40">
                            <span className="text-5xl mb-4 grayscale">📝</span>
                            <p className="text-sm font-medium">No history yet</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
