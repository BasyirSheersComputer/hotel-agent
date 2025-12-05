"use client";

/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 * 
 * Language Selector Component
 * Dropdown for selecting preferred language for chat responses.
 */

import { useState, useEffect, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Language {
    code: string;
    name: string;
}

interface LanguageSelectorProps {
    selectedLanguage: string;
    onLanguageChange: (code: string) => void;
    compact?: boolean;  // For header use
}

// Fallback languages if API fails
const FALLBACK_LANGUAGES: Language[] = [
    { code: "en", name: "English" },
    { code: "zh", name: "中文 (Chinese)" },
    { code: "ms", name: "Bahasa Melayu (Malay)" },
    { code: "ja", name: "日本語 (Japanese)" },
    { code: "ko", name: "한국어 (Korean)" },
    { code: "th", name: "ไทย (Thai)" },
    { code: "vi", name: "Tiếng Việt (Vietnamese)" },
    { code: "id", name: "Bahasa Indonesia" },
    { code: "ar", name: "العربية (Arabic)" },
    { code: "fr", name: "Français (French)" },
    { code: "de", name: "Deutsch (German)" },
    { code: "es", name: "Español (Spanish)" },
];

// Flag emojis for language codes
const LANGUAGE_FLAGS: Record<string, string> = {
    en: "🇬🇧",
    zh: "🇨🇳",
    ms: "🇲🇾",
    ja: "🇯🇵",
    ko: "🇰🇷",
    th: "🇹🇭",
    vi: "🇻🇳",
    id: "🇮🇩",
    ar: "🇸🇦",
    hi: "🇮🇳",
    fr: "🇫🇷",
    de: "🇩🇪",
    es: "🇪🇸",
    ru: "🇷🇺",
};

export default function LanguageSelector({
    selectedLanguage,
    onLanguageChange,
    compact = false
}: LanguageSelectorProps) {
    const [languages, setLanguages] = useState<Language[]>(FALLBACK_LANGUAGES);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Fetch available languages
    useEffect(() => {
        const fetchLanguages = async () => {
            try {
                const token = localStorage.getItem("token");
                const res = await fetch(`${API_BASE}/api/languages`, {
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                });

                if (res.ok) {
                    const data = await res.json();
                    setLanguages(data.languages || FALLBACK_LANGUAGES);
                }
            } catch (error) {
                console.error("Failed to fetch languages:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchLanguages();
    }, []);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Get current language name
    const currentLang = languages.find(l => l.code === selectedLanguage) || languages[0];
    const flag = LANGUAGE_FLAGS[selectedLanguage] || "🌐";

    if (compact) {
        return (
            <div ref={dropdownRef} className="relative">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    disabled={loading}
                    className="flex items-center gap-1 px-2 py-1 text-sm bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                    title="Select language"
                >
                    <span>{flag}</span>
                    <span className="hidden sm:inline">{currentLang?.code.toUpperCase()}</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {isOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50 max-h-80 overflow-y-auto">
                        {languages.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => {
                                    onLanguageChange(lang.code);
                                    setIsOpen(false);
                                }}
                                className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 ${selectedLanguage === lang.code ? "bg-blue-50 text-blue-600" : "text-gray-700"
                                    }`}
                            >
                                <span>{LANGUAGE_FLAGS[lang.code] || "🌐"}</span>
                                <span>{lang.name}</span>
                                {selectedLanguage === lang.code && (
                                    <svg className="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                )}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    // Full dropdown for settings
    return (
        <div ref={dropdownRef} className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
                Response Language
            </label>
            <button
                onClick={() => setIsOpen(!isOpen)}
                disabled={loading}
                className="w-full flex items-center justify-between px-4 py-2 bg-white border border-gray-300 rounded-lg hover:border-gray-400 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <span>{flag}</span>
                    <span>{currentLang?.name || "Select language"}</span>
                </div>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {isOpen && (
                <div className="absolute left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50 max-h-60 overflow-y-auto">
                    {languages.map((lang) => (
                        <button
                            key={lang.code}
                            onClick={() => {
                                onLanguageChange(lang.code);
                                setIsOpen(false);
                            }}
                            className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2 ${selectedLanguage === lang.code ? "bg-blue-50 text-blue-600" : "text-gray-700"
                                }`}
                        >
                            <span>{LANGUAGE_FLAGS[lang.code] || "🌐"}</span>
                            <span>{lang.name}</span>
                            {selectedLanguage === lang.code && (
                                <svg className="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            )}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
