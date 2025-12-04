"""
Script to populate ChromaDB v2 with comprehensive knowledge base.
"""
import os
import sys
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.env_utils import load_env_robustly

# Load environment variables
load_env_robustly()

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db_v2")

def load_knowledge_file(filename):
    """Load text from a file and return as a string."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filename} not found at {filepath}")
        return ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def main():
    print("=" * 80)
    print("POPULATING CHROMA_DB_V2")
    print("=" * 80)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables!")
        print("Please set your API key in backend/.env file")
        sys.exit(1)
    
    # Load knowledge files
    print("\n1. Loading knowledge files...")
    comprehensive_knowledge = load_knowledge_file("comprehensive_knowledge.txt")
    questions = load_knowledge_file("questions.txt")
    
    if not comprehensive_knowledge and not questions:
        print("ERROR: No knowledge files found!")
        sys.exit(1)
    
    # Combine all knowledge
    all_text = comprehensive_knowledge
    if questions:
        all_text += "\n\n" + questions
    
    print(f"   Loaded {len(all_text)} characters of knowledge")
    
    # Split into chunks
    print("\n2. Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Create documents
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": "comprehensive_knowledge.txt"}
        )
        for chunk in text_splitter.split_text(all_text)
    ]
    
    print(f"   Created {len(documents)} document chunks")
    
    # Clear existing database
    print("\n3. Clearing existing database...")
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
        print("   Old database removed")
    
    # Create embeddings and populate database
    print("\n4. Creating embeddings and populating database...")
    print("   This may take a few minutes...")
    
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=CHROMA_PATH
    )
    
    print(f"   Database populated with {len(documents)} chunks")
    
    # Test the database
    print("\n5. Testing database...")
    test_query = "What are the restaurant operating hours?"
    results = db.similarity_search(test_query, k=3)
    print(f"   Test query: '{test_query}'")
    print(f"   Found {len(results)} relevant results")
    if results:
        print(f"   Sample result: {results[0].page_content[:100]}...")
    
    print("\n" + "=" * 80)
    print("DATABASE POPULATION COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
