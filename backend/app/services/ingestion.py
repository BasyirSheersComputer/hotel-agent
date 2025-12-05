import os
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Define persistence directory
CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_v2")


def get_collection_name(org_id: Optional[str] = None) -> str:
    """
    Get the Chroma collection name for an organization.
    Mirrors the logic in retrieval.py for consistency.
    """
    if org_id is None:
        return "kb_demo"
    
    # Sanitize org_id for collection name
    safe_org_id = str(org_id).replace("-", "")[:32]
    return f"kb_{safe_org_id}"


def ingest_documents(pdf_directory: str, org_id: Optional[str] = None):
    """
    Ingest all PDFs from the directory, split them, and store embeddings in ChromaDB.
    
    Args:
        pdf_directory: Path to directory containing PDF/TXT files
        org_id: Organization ID for tenant-scoped storage (optional, defaults to demo)
    """
    if not os.path.exists(pdf_directory):
        print(f"Directory {pdf_directory} does not exist.")
        return

    documents = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_directory, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith(".txt"):
            from langchain_community.document_loaders import TextLoader
            file_path = os.path.join(pdf_directory, filename)
            loader = TextLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print("No documents found to ingest.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Initialize Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Get org-specific collection name
    collection_name = get_collection_name(org_id)
    print(f"Ingesting to collection: {collection_name}")

    # Create/Update Vector DB with org-specific collection
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=collection_name
    )
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH} (collection: {collection_name}).")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector store")
    parser.add_argument("--data-dir", type=str, help="Directory containing documents")
    parser.add_argument("--org-id", type=str, default=None, help="Organization ID for scoped storage")
    args = parser.parse_args()
    
    if args.data_dir:
        data_dir = args.data_dir
    else:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    
    ingest_documents(data_dir, org_id=args.org_id)

