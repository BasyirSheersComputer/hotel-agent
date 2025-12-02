"use client";

import { useState } from "react";
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

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            // TODO: Replace with actual backend URL when Python is ready
            const response = await fetch("http://localhost:8000/api/chat", {
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
                { role: "agent", content: "Error connecting to backend. Is Python running?" },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto p-4 bg-gray-50">
            <header className="mb-4 text-center">
                <h1 className="text-2xl font-bold text-blue-900">Club Med Resort Genius</h1>
                <p className="text-sm text-gray-500">Agent Assist System</p>
            </header>

            <div className="flex-1 overflow-y-auto bg-white rounded-lg shadow-md p-4 mb-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-400 mt-20">
                        <p>Ask a question about Club Med Cherating...</p>
                        <p className="text-xs mt-2">Example: "What are the restaurant operating hours?"</p>
                    </div>
                )}
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                            }`}
                    >
                        <div
                            className={`max-w-[85%] p-4 rounded-lg ${msg.role === "user"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-50 text-gray-900 border border-gray-200"
                                }`}
                        >
                            {msg.role === "user" ? (
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                            ) : (
                                <div className="prose prose-sm max-w-none">
                                    <ReactMarkdown
                                        components={{
                                            // Headings with clear hierarchy
                                            h1: ({ node, ...props }) => (
                                                <h1 className="text-lg font-bold text-gray-900 mt-4 mb-3 pb-2 border-b border-gray-200" {...props} />
                                            ),
                                            h2: ({ node, ...props }) => (
                                                <h2 className="text-base font-bold text-gray-900 mt-4 mb-2" {...props} />
                                            ),
                                            h3: ({ node, ...props }) => (
                                                <h3 className="text-sm font-bold text-gray-800 mt-3 mb-2" {...props} />
                                            ),
                                            // Paragraphs with proper spacing
                                            p: ({ node, ...props }) => (
                                                <p className="mb-3 leading-relaxed text-gray-800" {...props} />
                                            ),
                                            // Main unordered lists
                                            ul: ({ node, ...props }) => (
                                                <ul className="space-y-2 my-3" {...props} />
                                            ),
                                            // Main ordered lists
                                            ol: ({ node, ...props }) => (
                                                <ol className="space-y-2 my-3" {...props} />
                                            ),
                                            // List items with better hierarchy
                                            li: ({ node, children, ...props }) => {
                                                // Check if this li contains nested lists
                                                const hasNestedList = children && Array.isArray(children) &&
                                                    children.some((child: any) =>
                                                        child?.type?.name === 'ul' || child?.type?.name === 'ol'
                                                    );

                                                return (
                                                    <li className={`leading-relaxed ${hasNestedList ? 'mb-2' : ''}`} {...props}>
                                                        <div className="flex">
                                                            <span className="mr-2 text-blue-600 font-bold">•</span>
                                                            <div className="flex-1">
                                                                {children}
                                                            </div>
                                                        </div>
                                                    </li>
                                                );
                                            },
                                            // Bold text
                                            strong: ({ node, ...props }) => (
                                                <strong className="font-bold text-gray-900" {...props} />
                                            ),
                                            // Italic text
                                            em: ({ node, ...props }) => (
                                                <em className="italic text-gray-700" {...props} />
                                            ),
                                            // Code blocks
                                            code: ({ node, ...props }) => (
                                                <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-blue-700" {...props} />
                                            ),
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            )}
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-300">
                                    <p className="text-xs font-semibold text-gray-600 mb-1">Sources:</p>
                                    <ul className="text-xs text-gray-500 space-y-0.5">
                                        {msg.sources.map((src, i) => (
                                            <li key={i} className="truncate">📄 {src.split('\\').pop()}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                            <div className="flex items-center space-x-2">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                <span className="text-gray-600">Searching knowledge base...</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="flex gap-2">
                <input
                    type="text"
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="Type your question..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
                <button
                    onClick={sendMessage}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    Send
                </button>
            </div>
        </div>
    );
}
