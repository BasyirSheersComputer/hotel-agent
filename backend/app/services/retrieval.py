"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.
"""
import os

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
# (GCS credentials are automatically available in Cloud Run)
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
    
    # Expanded location keywords to catch more natural language patterns
    location_keywords = [
        # Proximity-based
        "nearest", "nearby", "closest", "close to", "near the hotel", "near me",
        "around here", "in the area", "within", "how far",
        
        # Location-seeking phrases
        "where is", "where's", "where can i find", "where can i get",
        "where do i find", "where to find", "how do i get to",
        
        # Search/Find phrases
        "find a", "find me", "find the", "show me", "direct me to",
        "looking for", "search for", "any", "are there", "i need",
        
        # Local/Area modifiers
        "local", "in town", "around", "available", "urgently",
       
        # Action phrases that imply external location
        "fill up", "buy", "get", "visit"
    ]
    
    # Check for location keywords
    if any(keyword in query_lower for keyword in location_keywords):
        return True
    
    # Additional check: if query contains a recognizable place type from location.py
    # and uses question words, it's likely a location query
    question_words = ["where", "find", "show", "any", "is there", "are there"]
    if any(qword in query_lower for qword in question_words):
        # Import here to avoid circular dependency at module level
        from .location import PLACE_TYPE_MAPPINGS
        
        # Check if any place type keyword is in the query
        for place_keyword in PLACE_TYPE_MAPPINGS.keys():
            if place_keyword in query_lower:
                return True
    
    return False

def is_resort_facility(query_text: str) -> bool:
    """
    Check if the query is asking about a facility that exists ON the resort property.
    These should be answered from the knowledge base, not Google Maps.
    """
    query_lower = query_text.lower()
    
    # FIRST: Check for explicit resort context phrases that should ALWAYS use KB
    # These take priority over external indicators
    resort_context_phrases = [
        "at the resort", "at the hotel", "on property", "in the resort",
        "the resort", "the hotel", "resort's", "hotel's",
        "the restaurant hours", "restaurant hours", "restaurant operating",
        "the pool", "the gym", "the lobby", "the beach at",
        "mutiara", "rembulan", "enak", "pinang"  # Specific restaurant names
    ]
    
    if any(phrase in query_lower for phrase in resort_context_phrases):
        return True
    
    # Explicit indicators that user is asking about EXTERNAL locations (not resort)
    external_indicators = [
        "local", "nearby", "nearest", "closest", "in town", "in the area",
        "around here", "off-site", "outside", "external", "where can i find",
        "find me", "any", "are there", "where can i buy", "where can i get"
    ]
    
    # Special handling for "show me" - depends on context
    # "show me the X" for resort facilities should use KB
    # "show me cafes" should use Maps
    if "show me" in query_lower:
        # Check if it's "show me the [facility]" or "show me [specific resort name]"
        resort_show_patterns = [
            "show me the restaurant", "show me the pool", "show me the gym",
            "show me the beach", "show me the lobby", "show me the bar"
        ]
        if any(pattern in query_lower for pattern in resort_show_patterns):
            return True
        # Otherwise, "show me" is an external indicator
        external_indicators.append("show me")
    
    # If query has external indicators, it's NOT about resort facilities
    # UNLESS it explicitly mentions resort/hotel context (already checked above)
    if any(indicator in query_lower for indicator in external_indicators):
        return False
    
    # Specific resort facilities (only if no external indicators)
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
    """
    Get the Chroma collection name for an organization.
    
    Returns:
        - 'kb_demo' for demo mode or no org_id
        - 'kb_{org_id}' for normal orgs
        - 'default' as fallback for backward compatibility
    """
    from app.config.settings import DEMO_MODE, DEMO_ORG_ID
    
    if DEMO_MODE or org_id is None:
        return "kb_demo"
    
    if org_id == DEMO_ORG_ID:
        return "kb_demo"
    
    # Sanitize org_id for collection name (Chroma has restrictions)
    safe_org_id = str(org_id).replace("-", "")[:32]
    return f"kb_{safe_org_id}"


def query_rag(query_text: str, org_id: str = None):
    """
    Query the RAG system and return the answer and sources.
    If the query is about nearby locations, use Google Maps API instead.
    
    Args:
        query_text: The user's query
        org_id: Organization ID for tenant-scoped retrieval (optional)
    """
    # Check if this is a location-based query
    if detect_location_query(query_text):
        # IMPORTANT: Check if it's asking about a resort facility first
        if is_resort_facility(query_text):
            # This is about an on-property facility - use RAG, not Maps
            pass  # Fall through to RAG query below
        else:
            # This is about an external amenity - check if we can find it on Maps
            place_type = get_place_type(query_text)
            
            if place_type:
                # Use Google Maps to find nearby places
                places = search_nearby_places(place_type, radius=10000, max_results=5)
                answer = format_nearby_results(places, place_type)
                
                return {
                    "answer": answer,
                    "sources": ["Google Maps Places API"]
                }
    
    # Fallback to standard RAG for non-location queries or resort facility queries
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY missing in retrieval.py")
        
        embedding_function = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )
        
        if not os.path.exists(CHROMA_PATH):
            return {
                "answer": "I apologize, but I cannot access my knowledge base at the moment. The system administrator needs to rebuild the vector database.",
                "sources": ["System Error: Vector DB missing"]
            }
        
        # Get org-specific collection name
        collection_name = get_collection_name(org_id)
        
        # Try to load org-specific collection first
        try:
            db = Chroma(
                persist_directory=CHROMA_PATH, 
                embedding_function=embedding_function,
                collection_name=collection_name
            )
            # Check if collection has documents
            if db._collection.count() == 0:
                # Fall back to default collection for backward compatibility
                db = Chroma(
                    persist_directory=CHROMA_PATH, 
                    embedding_function=embedding_function
                )
        except:
            # Fall back to default collection
            db = Chroma(
                persist_directory=CHROMA_PATH, 
                embedding_function=embedding_function
            )

        # Search the DB
        results = db.similarity_search_with_score(query_text, k=3)

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        model = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key
        )
        response_text = model.invoke(prompt)

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        
        return {
            "answer": response_text.content,
            "sources": sources
        }
    except Exception as e:
        print(f"RAG Error: {str(e)}")
        return {
            "answer": "I'm having trouble connecting to my knowledge base. Please check your API keys and network connection.",
            "sources": [f"System Error: {str(e)}"]
        }
