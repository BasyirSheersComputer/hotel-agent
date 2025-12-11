"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .location import search_nearby_places, format_nearby_results, get_place_type
from app.env_utils import load_env_robustly

# Ensure env is loaded
load_env_robustly()

# Only import GCS utilities in cloud environment
try:
    from .gcs_utils import download_vector_db_from_gcs
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("GCS utilities not available (running in local mode)")

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_v2")

# Download vector DB from GCS if in cloud environment
if GCS_AVAILABLE and (os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("K_SERVICE")):
    print("Cloud environment detected. Attempting to download vector DB from GCS...")
    download_vector_db_from_gcs()


PROMPT_TEMPLATE = """
You are a helpful Club Med Cherating resort assistant. Answer the question based only on the following context.

Context:
{context}

---

Question: {question}

Instructions for your response:
1. Structure your answer with clear hierarchy:
   - Start with a direct, concise answer
   - Use ### for main section headings when multiple topics are covered
   - Use **bold** for restaurant names, times, prices, and important terms
   - Use bullet points (-) for main items
   - Use sub-bullets (  -) with 2-space indentation for details under main items

2. Formatting guidelines:
   - Each main point should be on its own line
   - Sub-points should be clearly indented under their parent
   - Add blank lines between major sections
   - Keep bullet points concise (1-2 lines max)

3. Example structure:
   **Main Topic:**
   - Main point 1
     - Sub-detail A
     - Sub-detail B
   - Main point 2
     - Sub-detail C

Answer:
"""

def detect_location_query(query_text: str) -> bool:
    """
    Detect if the query is asking about nearby locations/amenities.
    """
    query_lower = query_text.lower()
    
    # Expanded location keywords
    location_keywords = [
        "nearest", "nearby", "closest", "close to", "near the hotel", "near me",
        "around here", "in the area", "within", "how far",
        "where is", "where's", "where can i find", "where can i get",
        "where do i find", "where to find", "how do i get to",
        "find a", "find me", "find the", "show me", "direct me to",
        "looking for", "search for", "any", "are there", "i need",
        "local", "in town", "around", "available", "urgently",
        "fill up", "buy", "get", "visit"
    ]
    
    if any(keyword in query_lower for keyword in location_keywords):
        return True
    
    question_words = ["where", "find", "show", "any", "is there", "are there"]
    if any(qword in query_lower for qword in question_words):
        from .location import PLACE_TYPE_MAPPINGS
        for place_keyword in PLACE_TYPE_MAPPINGS.keys():
            if place_keyword in query_lower:
                return True
    
    return False

def is_resort_facility(query_text: str) -> bool:
    """
    Check if the query is asking about a facility that exists ON the resort property.
    """
    query_lower = query_text.lower()
    
    resort_context_phrases = [
        "at the resort", "at the hotel", "on property", "in the resort",
        "the resort", "the hotel", "resort's", "hotel's",
        "the restaurant hours", "restaurant hours", "restaurant operating",
        "the pool", "the gym", "the lobby", "the beach at",
        "mutiara", "rembulan", "enak", "pinang"
    ]
    
    if any(phrase in query_lower for phrase in resort_context_phrases):
        return True
    
    external_indicators = [
        "local", "nearby", "nearest", "closest", "in town", "in the area",
        "around here", "off-site", "outside", "external", "where can i find",
        "find me", "any", "are there", "where can i buy", "where can i get"
    ]
    
    if "show me" in query_lower:
        resort_show_patterns = [
            "show me the restaurant", "show me the pool", "show me the gym",
            "show me the beach", "show me the lobby", "show me the bar"
        ]
        if any(pattern in query_lower for pattern in resort_show_patterns):
            return True
        external_indicators.append("show me")
    
    if any(indicator in query_lower for indicator in external_indicators):
        return False
    
    resort_facilities = [
        "pool", "pools", "swimming pool", "zen pool",
        "trapeze", "flying trapeze", "archery", "kayak", "kayaking",
        "sailing", "hobie cat", "tennis court", "gym", "fitness center",
        "yoga class", "spa treatment", "kids club", "mini club",
        "room service", "suite", "my room", "our room",
        "lobby", "reception", "front desk", "boutique", "parking lot"
    ]
    
    for facility in resort_facilities:
        if facility in query_lower:
            return True
    
    return False

def get_collection_name(org_id: str = None) -> str:
    from app.config.settings import DEMO_MODE, DEMO_ORG_ID
    if DEMO_MODE or org_id is None:
        return "kb_demo"
    if org_id == DEMO_ORG_ID:
        return "kb_demo"
    safe_org_id = str(org_id).replace("-", "")[:32]
    return f"kb_{safe_org_id}"

async def run_sync_in_executor(func, *args, **kwargs):
    """Run a sync function in a thread pool executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

async def query_rag(query_text: str, org_id: str = None):
    """
    Async implementation of query_rag with Redis Caching.
    """
    # 1. Check Cache
    from .cache import cache_service
    # Ensure org_id is string for cache key
    cache_org_id = str(org_id) if org_id else "demo"
    
    cached = cache_service.get_cached_response(cache_org_id, query_text)
    if cached:
        # Optional: Indicate cached source?
        # cached["sources"].append("Cache") 
        return cached

    # Check if this is a location-based query
    if detect_location_query(query_text):
        if is_resort_facility(query_text):
            pass  # Fall through to RAG
        else:
            place_type = get_place_type(query_text)
            if place_type:
                # Check for API Key first
                maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
                
                if not maps_api_key or maps_api_key == "todo":
                     # Mock Fallback for Demo/Missing Key (Proactive)
                    answer = f"**Nearby {place_type.title()} (Demo Data):**\n\n*   **Kuantan General Hospital:** 30 mins away (Emergency)\n*   **Klinik Kesihatan Cherating:** 5 mins away (General)\n*   **Nearest Pharmacy:** 10 mins drive" if "hospital" in str(place_type) or "pharmacy" in str(place_type) else f"**Nearby {place_type.title()} (Demo):**\n\n*   **Local Option 1:** Highly rated.\n*   **Local Option 2:** Popular with guests."
                    source = "Demo Data (Maps Unavailable)"
                else:
                    # Run Map Search in ThreadPool (Blocking I/O)
                    try:
                        places = await run_sync_in_executor(search_nearby_places, place_type, radius=10000, max_results=5)
                        answer = format_nearby_results(places, place_type)
                        source = "Google Maps Places API"
                    except Exception as e:
                        # Fallback if search fails even with key
                        print(f"Maps API Error: {e}, using mock.")
                        answer = f"**Nearby {place_type.title()} (Demo Data):**\n\n*   **Local Clinic:** 5 mins away.\n*   **Hospital:** 30 mins drive."
                        source = "Demo Data (Error Fallback)"

                result = {
                    "answer": answer,
                    "sources": [source]
                }
                # Cache Map Results
                cache_service.set_cached_response(cache_org_id, query_text, result)
                return result
    
    # Fallback to standard RAG
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY missing in retrieval.py")
        
        embedding_function = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )
        
        if not os.path.exists(CHROMA_PATH):
            print("Vector DB missing. Attempting to auto-initialize...")
            try:
                # Run population script
                import subprocess
                # Get absolute path to populate_db.py (sibling of this file's parent's parent...)
                # Current file: backend/app/services/retrieval.py
                # Target: backend/populate_db.py
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                script_path = os.path.join(backend_dir, "populate_db.py")
                
                # Check if script exists
                if os.path.exists(script_path):
                    # Blocking call wrapped in executor
                    def run_population():
                        subprocess.run([sys.executable, script_path], check=True)
                        
                    await run_sync_in_executor(run_population)
                    print("Vector DB initialized successfully.")
                else:
                    return {
                        "answer": f"System Error: Vector DB missing and population script not found at {script_path}.",
                        "sources": ["System Error"]
                    }
            except Exception as e:
                print(f"Failed to auto-initialize Vector DB: {e}")
                return {
                    "answer": "System Error: Vector DB missing and auto-initialization failed.",
                    "sources": ["System Error"]
                }
        
        collection_name = get_collection_name(org_id)
        
        # Initialize DB (Sync Op, usually fast enough, or could wrap)
        # Chroma initialization checks directory existence.
        try:
            db = Chroma(
                persist_directory=CHROMA_PATH, 
                embedding_function=embedding_function,
                collection_name=collection_name
            )
            if db._collection.count() == 0:
                db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        except:
            db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

        # ASYNC Search
        # await db.asimilarity_search_with_score(query_text, k=3)
        # Note: some older langchain versions might not support asimilarity_search_with_score on Chroma.
        # If it fails, we fall back to run_in_executor.
        try:
            results = await db.asimilarity_search_with_score(query_text, k=3)
        except AttributeError:
             # Fallback if method missing
             results = await run_sync_in_executor(db.similarity_search_with_score, query_text, k=3)

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
        # ASYNC Invoke
        response_text = await model.ainvoke(prompt)

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        
        result = {
            "answer": response_text.content,
            "sources": sources
        }
        # Cache RAG Results
        cache_service.set_cached_response(cache_org_id, query_text, result)
        return result

    except Exception as e:
        print(f"RAG Error: {str(e)}")
        error_msg = str(e).lower()
        
        # Graceful handling for invalid API key (common in demo/test envs)
        if "401" in error_msg or "api key" in error_msg or "authentication" in error_msg:
             return {
                "answer": "I apologize, but I am currently running in a demo environment without a live connection to the AI processing unit. I can assist you with standard information about Check-in, Facilities, Dining, and Activities using the Quick Assist buttons.",
                "sources": ["System Message"]
            }

        # Do NOT cache errors
        return {
            "answer": "System Error: " + str(e),
            "sources": ["System Error"]
        }
