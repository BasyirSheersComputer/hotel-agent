
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

try:
    from app.services.retrieval import query_rag
    print("Attempting to query RAG...")
    result = query_rag("What are the restaurant operating hours?")
    print("Result:", result)
except Exception as e:
    print("Error occurred:")
    import traceback
    traceback.print_exc()
