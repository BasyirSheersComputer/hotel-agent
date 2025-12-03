"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

interface Message {
    role: "user" | "agent";
    content: string;
    sources?: string[];
}



export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

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
            // Use the cloud backend URL for the demo
            const response = await fetch("https://hotel-agent-backend-319072304914.us-central1.run.app/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userMessage.content }),
            });

            if (!response.ok) throw new Error("Network response was not ok");

            const data = await response.json();
            const agentMessage: Message = {
                role: "agent",
                content: data.answer,
                sources: data.sources,
            };
            setMessages((prev) => [...prev, agentMessage]);
        } catch (error) {
            console.error("Error:", error);
            setMessages((prev) => [
                ...prev,
                { role: "agent", content: "I apologize, but I seem to be offline. Please check your connection." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleQuickQuery = (query: string) => {
        sendMessage(query);
    };

    return (
        <div className="flex w-[95%] max-w-[1400px] h-[90vh] bg-white/85 backdrop-blur-[20px] rounded-[24px] shadow-[0_8px_30px_rgba(0,0,0,0.05)] border border-white/40 overflow-hidden flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="w-full md:w-[320px] bg-white/50 border-b md:border-b-0 md:border-r border-black/5 p-8 flex flex-col gap-8 justify-between md:justify-start">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-[#0F4C81] text-white rounded-full flex items-center justify-center font-serif font-bold text-xl">
                        RG
                    </div>
                    <h1 className="text-2xl font-serif font-semibold text-[#0F4C81]">Resort Genius</h1>
                </div>

                <div className="hidden md:block bg-gradient-to-br from-[#0F4C81] to-[#1A5F9A] text-white p-6 rounded-[16px] shadow-[0_4px_6px_rgba(0,0,0,0.05)]">
                    <h2 className="text-lg font-serif font-semibold mb-2">Club Med Cherating</h2>
                    <p className="text-sm opacity-90 flex items-center gap-2 mb-4">
                        <span className="w-2 h-2 bg-[#48BB78] rounded-full shadow-[0_0_0_2px_rgba(72,187,120,0.3)]"></span>
                        Concierge Online
                    </p>
                    <div className="flex justify-between items-center pt-2 border-t border-white/20 text-sm">
                        <span>28°C</span>
                        <span>Tropical</span>
                    </div>
                </div>

                <nav className="hidden md:block">
                    <h3 className="text-sm uppercase tracking-wider text-gray-500 mb-4 font-semibold">Quick Assist</h3>
                    <div className="flex flex-col gap-2">
                        <button onClick={() => handleQuickQuery('What are the restaurant operating hours?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🍽️</span> Dining Hours
                        </button>
                        <button onClick={() => handleQuickQuery('What activities are available today?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🏄</span> Activities
                        </button>
                        <button onClick={() => handleQuickQuery('Where is the nearest hospital?')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🏥</span> Medical Info
                        </button>
                        <button onClick={() => handleQuickQuery('Tell me about the room amenities')} className="w-full flex items-center gap-4 p-4 bg-white border border-black/5 rounded-[12px] hover:-translate-y-[2px] hover:shadow-[0_4px_6px_rgba(0,0,0,0.05)] hover:border-[#D4AF37] transition-all text-left text-[#1A202C] text-sm">
                            <span className="text-lg">🛏️</span> Room Info
                        </button>
                    </div>
                </nav>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col bg-white/30">
                <header className="p-6 md:px-8 border-b border-black/5 bg-white/50">
                    <h2 className="text-[#0F4C81] text-xl md:text-2xl font-serif font-semibold">Guest Assistance</h2>
                    <p className="text-gray-500 text-sm md:text-base">Ask me anything about the resort or local area</p>
                </header>

                <div className="flex-1 overflow-y-auto p-8 flex flex-col gap-6 scroll-smooth">
                    {messages.length === 0 && (
                        <div className="flex gap-4 max-w-[80%] animate-[fadeIn_0.3s_ease-out]">
                            <div className="w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0">
                                <img src="https://ui-avatars.com/api/?name=Resort+Genius&background=0F4C81&color=fff" alt="Agent" />
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
                            <div className="w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0">
                                <img
                                    src={msg.role === 'agent'
                                        ? 'https://ui-avatars.com/api/?name=Resort+Genius&background=0F4C81&color=fff'
                                        : 'https://ui-avatars.com/api/?name=Guest&background=D4AF37&color=fff'}
                                    alt={msg.role}
                                />
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
                                                strong: ({ node, ...props }) => <strong className="font-semibold text-inherit" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="ml-5 my-2 list-disc" {...props} />,
                                                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                                                p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
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
                                                <li key={i} className="truncate">📄 {src.split('\\').pop()}</li>
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
                            <div className="w-10 h-10 rounded-full shadow-[0_4px_6px_rgba(0,0,0,0.05)] overflow-hidden flex-shrink-0">
                                <img src="https://ui-avatars.com/api/?name=Resort+Genius&background=0F4C81&color=fff" alt="Agent" />
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

                <div className="p-8 bg-white border-t border-black/5">
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
            </main>
        </div>
    );
}
