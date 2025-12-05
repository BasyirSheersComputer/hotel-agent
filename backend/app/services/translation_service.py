"""
Translation Service for multi-language support.
Uses OpenAI for language detection and translation.
Includes caching for performance.
"""
import os
import hashlib
from typing import Optional, Tuple
from functools import lru_cache
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Supported languages with display names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "中文 (Chinese)",
    "ms": "Bahasa Melayu (Malay)",
    "ja": "日本語 (Japanese)",
    "ko": "한국어 (Korean)",
    "th": "ไทย (Thai)",
    "vi": "Tiếng Việt (Vietnamese)",
    "id": "Bahasa Indonesia",
    "ar": "العربية (Arabic)",
    "hi": "हिन्दी (Hindi)",
    "fr": "Français (French)",
    "de": "Deutsch (German)",
    "es": "Español (Spanish)",
    "ru": "Русский (Russian)",
}

# Language names for prompts
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Chinese",
    "ms": "Malay",
    "ja": "Japanese",
    "ko": "Korean",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ar": "Arabic",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
}

# Simple in-memory cache for translations
_translation_cache: dict = {}
MAX_CACHE_SIZE = 1000


def _get_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """Generate cache key for translation."""
    content = f"{source_lang}:{target_lang}:{text}"
    return hashlib.md5(content.encode()).hexdigest()


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


def detect_language(text: str) -> str:
    """
    Detect the language of input text using OpenAI.
    Returns ISO 639-1 language code (e.g., 'en', 'zh', 'ms').
    Falls back to 'en' if detection fails.
    """
    if not text or len(text.strip()) < 3:
        return "en"
    
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a language detection system. 
Analyze the text and respond with ONLY the ISO 639-1 language code (2 letters).
Supported codes: en, zh, ms, ja, ko, th, vi, id, ar, hi, fr, de, es, ru.
If uncertain, respond with 'en'."""
                },
                {
                    "role": "user",
                    "content": f"Detect the language of this text:\n\n{text[:500]}"
                }
            ],
            temperature=0,
            max_tokens=5
        )
        
        detected = response.choices[0].message.content.strip().lower()
        
        # Validate detected language
        if detected in SUPPORTED_LANGUAGES:
            return detected
        
        # Handle common variations
        if detected.startswith("zh"):
            return "zh"
        if detected in ["my", "mal"]:
            return "ms"
        
        return "en"
        
    except Exception as e:
        print(f"Language detection error: {e}")
        return "en"


def translate_text(
    text: str,
    target_lang: str,
    source_lang: Optional[str] = None
) -> str:
    """
    Translate text to target language using OpenAI.
    Uses cache to avoid repeated translations.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'zh', 'ms')
        source_lang: Source language code (auto-detected if not provided)
    
    Returns:
        Translated text, or original if translation fails/unnecessary
    """
    if not text or not text.strip():
        return text
    
    # Detect source language if not provided
    if not source_lang:
        source_lang = detect_language(text)
    
    # Skip translation if same language
    if source_lang == target_lang:
        return text
    
    # Skip translation if target is English and text is already English
    if target_lang == "en" and source_lang == "en":
        return text
    
    # Check cache
    cache_key = _get_cache_key(text, source_lang, target_lang)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        client = get_openai_client()
        
        target_name = LANGUAGE_NAMES.get(target_lang, "English")
        source_name = LANGUAGE_NAMES.get(source_lang, "English")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a professional translator specializing in hospitality and tourism.
Translate the following text from {source_name} to {target_name}.
Maintain the original formatting, including markdown if present.
Keep proper nouns, brand names, and technical terms as-is when appropriate.
Provide only the translation, no explanations."""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        translated = response.choices[0].message.content.strip()
        
        # Update cache (with size limit)
        if len(_translation_cache) >= MAX_CACHE_SIZE:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(_translation_cache.keys())[:100]
            for key in keys_to_remove:
                del _translation_cache[key]
        
        _translation_cache[cache_key] = translated
        return translated
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def translate_to_english(text: str) -> Tuple[str, str]:
    """
    Translate user query to English for RAG processing.
    Returns tuple of (translated_text, detected_language).
    """
    detected_lang = detect_language(text)
    
    if detected_lang == "en":
        return text, "en"
    
    translated = translate_text(text, "en", detected_lang)
    return translated, detected_lang


def translate_response(response: str, target_lang: str) -> str:
    """
    Translate AI response to user's preferred language.
    Skips translation if target is English.
    """
    if target_lang == "en":
        return response
    
    return translate_text(response, target_lang, "en")


def get_supported_languages() -> dict:
    """Get dictionary of supported languages for UI."""
    return SUPPORTED_LANGUAGES.copy()


# Test function
if __name__ == "__main__":
    # Test language detection
    test_texts = [
        ("Hello, how are you?", "en"),
        ("你好，请问餐厅在哪里？", "zh"),
        ("Bolehkah saya tempah bilik?", "ms"),
        ("プールは何時まで開いていますか？", "ja"),
    ]
    
    print("Testing language detection:")
    for text, expected in test_texts:
        detected = detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} '{text[:30]}...' → {detected} (expected: {expected})")
    
    # Test translation
    print("\nTesting translation:")
    english_text = "The restaurant is open from 7am to 10pm."
    
    for lang in ["zh", "ms", "ja"]:
        translated = translate_text(english_text, lang, "en")
        print(f"  → {lang}: {translated}")
