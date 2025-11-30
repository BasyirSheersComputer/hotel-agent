import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Define persistence directory
CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_v2")

def ingest_documents(pdf_directory: str):
    """
    Ingest all PDFs from the directory, split them, and store embeddings in ChromaDB.
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
    # Note: This requires OPENAI_API_KEY to be set in environment
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Create/Update Vector DB
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    # Test run
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    ingest_documents(data_dir)
