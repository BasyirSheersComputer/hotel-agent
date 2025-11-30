"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.
"""
import os

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .location import search_nearby_places, format_nearby_results, get_place_type

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_v2")

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
    location_keywords = [
        "nearest", "nearby", "closest", "close to", "near the hotel",
        "around here", "in the area", "within", "how far"
    ]
    
    return any(keyword in query_text.lower() for keyword in location_keywords)

def is_resort_facility(query_text: str) -> bool:
    """
    Check if the query is asking about a facility that exists ON the resort property.
    These should be answered from the knowledge base, not Google Maps.
    """
    query_lower = query_text.lower()
    
    # Facilities that Club Med Cherating HAS on property
    resort_facilities = [
        # Beach & Water
        "beach", "sea", "ocean", "shore", "coast", "sand", "water", "swimming",
        
        # Pools
        "pool", "pools", "swimming pool",
        
        # Restaurants & Dining (on property)
        "mutiara", "rembulan", "pinang", "restaurant", "buffet", "dining", 
        "breakfast", "lunch", "dinner", "bar", "food",
        
        # Activities & Sports
        "trapeze", "archery", "kayak", "sailing", "tennis", "gym", "fitness",
        "yoga", "spa", "massage", "kids club", "playground",
        
        # Accommodation
        "room", "suite", "accommodation", "deluxe", "garden view",
        
        # Resort Areas
        "lobby", "reception", "boutique", "shop", "parking lot"
    ]
    
    # Check if query asks about any resort facility
    for facility in resort_facilities:
        if facility in query_lower:
            return True
    
    return False

def query_rag(query_text: str):
    """
    Query the RAG system and return the answer and sources.
    If the query is about nearby locations, use Google Maps API instead.
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
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=3)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI(model="gpt-4o")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    
    return {
        "answer": response_text.content,
        "sources": sources
    }
