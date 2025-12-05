"""
Knowledge Base Service for document management.
Handles document upload, deletion, and vector DB operations.
"""
import os
import uuid
import hashlib
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import KBDocument, Organization
from app.config.settings import DEMO_MODE, DEMO_ORG_ID


# Local storage path (for development / demo mode)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_v2")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_collection_name(org_id: str = None) -> str:
    """Get Chroma collection name for an organization."""
    if DEMO_MODE or org_id is None:
        return "kb_demo"
    safe_org_id = str(org_id).replace("-", "")[:32]
    return f"kb_{safe_org_id}"


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash for deduplication."""
    return hashlib.sha256(content).hexdigest()


class KBService:
    """Knowledge Base document management service."""
    
    @staticmethod
    def list_documents(db: Session, org_id: str, include_processing: bool = True) -> List[KBDocument]:
        """
        List all documents for an organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            include_processing: Whether to include docs still being processed
        """
        query = db.query(KBDocument).filter(KBDocument.org_id == org_id)
        
        if not include_processing:
            query = query.filter(KBDocument.status == "active")
        
        return query.order_by(KBDocument.uploaded_at.desc()).all()
    
    @staticmethod
    def get_document(db: Session, doc_id: str, org_id: str) -> Optional[KBDocument]:
        """Get a single document by ID (org-scoped)."""
        return db.query(KBDocument).filter(
            KBDocument.doc_id == doc_id,
            KBDocument.org_id == org_id
        ).first()
    
    @staticmethod
    async def upload_document(
        db: Session,
        org_id: str,
        user_id: str,
        filename: str,
        content: bytes,
        auto_ingest: bool = True
    ) -> KBDocument:
        """
        Upload a document and optionally trigger ingestion.
        
        Args:
            db: Database session
            org_id: Organization ID
            user_id: Uploading user's ID
            filename: Original filename
            content: File content as bytes
            auto_ingest: Whether to automatically ingest to vector DB
        
        Returns:
            Created KBDocument record
        """
        # Compute hash for deduplication
        content_hash = compute_file_hash(content)
        
        # Check for duplicate
        existing = db.query(KBDocument).filter(
            KBDocument.org_id == org_id,
            KBDocument.content_hash == content_hash
        ).first()
        
        if existing:
            raise ValueError(f"Document with same content already exists: {existing.filename}")
        
        # Generate unique filename
        doc_id = uuid.uuid4()
        ext = os.path.splitext(filename)[1].lower()
        stored_filename = f"{org_id}/{doc_id}{ext}"
        
        # Store file locally (for demo/dev mode)
        # TODO: Add GCS/S3 integration for production
        org_upload_dir = os.path.join(UPLOAD_DIR, str(org_id))
        os.makedirs(org_upload_dir, exist_ok=True)
        
        local_path = os.path.join(org_upload_dir, f"{doc_id}{ext}")
        with open(local_path, "wb") as f:
            f.write(content)
        
        # Create database record
        doc = KBDocument(
            doc_id=doc_id,
            org_id=org_id,
            filename=filename,
            file_url=local_path,  # Local path for now, cloud URL in production
            content_hash=content_hash,
            uploaded_by=user_id,
            status="processing" if auto_ingest else "uploaded"
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Trigger async ingestion
        if auto_ingest:
            try:
                await KBService.ingest_document(db, doc, org_id)
                doc.status = "active"
                db.commit()
            except Exception as e:
                doc.status = "failed"
                db.commit()
                raise e
        
        return doc
    
    @staticmethod
    async def ingest_document(db: Session, doc: KBDocument, org_id: str):
        """
        Ingest a document into the vector database.
        
        Args:
            db: Database session
            doc: KBDocument to ingest
            org_id: Organization ID for collection scoping
        """
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        
        # Load document based on file type
        file_path = doc.file_url
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata["source"] = doc.filename
            chunk.metadata["doc_id"] = str(doc.doc_id)
            chunk.metadata["org_id"] = str(org_id)
        
        # Get embeddings and store
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        collection_name = get_collection_name(org_id)
        
        # Add to existing collection or create new
        vectordb = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        vectordb.add_documents(chunks)
        print(f"Ingested {len(chunks)} chunks from {doc.filename} to collection {collection_name}")
    
    @staticmethod
    def delete_document(db: Session, doc_id: str, org_id: str) -> bool:
        """
        Delete a document and remove from vector DB.
        
        Args:
            db: Database session
            doc_id: Document ID to delete
            org_id: Organization ID (for scoping)
        
        Returns:
            True if deleted, False if not found
        """
        doc = db.query(KBDocument).filter(
            KBDocument.doc_id == doc_id,
            KBDocument.org_id == org_id
        ).first()
        
        if not doc:
            return False
        
        # Delete from vector DB
        try:
            KBService._remove_from_vector_db(str(doc_id), org_id)
        except Exception as e:
            print(f"Warning: Failed to remove from vector DB: {e}")
        
        # Delete local file
        try:
            if os.path.exists(doc.file_url):
                os.remove(doc.file_url)
        except Exception as e:
            print(f"Warning: Failed to delete file: {e}")
        
        # Delete database record
        db.delete(doc)
        db.commit()
        
        return True
    
    @staticmethod
    def _remove_from_vector_db(doc_id: str, org_id: str):
        """Remove document chunks from vector database."""
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        collection_name = get_collection_name(org_id)
        
        vectordb = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        # Delete by metadata filter
        vectordb._collection.delete(where={"doc_id": doc_id})
        print(f"Removed chunks for doc {doc_id} from collection {collection_name}")
    
    @staticmethod
    async def reindex_all(db: Session, org_id: str) -> dict:
        """
        Rebuild vector DB for an organization from all active documents.
        
        Args:
            db: Database session
            org_id: Organization ID
        
        Returns:
            Dict with reindex results
        """
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        import chromadb
        
        # Get all active documents
        docs = db.query(KBDocument).filter(
            KBDocument.org_id == org_id,
            KBDocument.status == "active"
        ).all()
        
        if not docs:
            return {"status": "no_documents", "count": 0}
        
        # Clear existing collection
        collection_name = get_collection_name(org_id)
        try:
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            try:
                client.delete_collection(collection_name)
            except:
                pass  # Collection might not exist
        except Exception as e:
            print(f"Warning: Could not clear collection: {e}")
        
        # Re-ingest all documents
        success_count = 0
        failed_docs = []
        
        for doc in docs:
            try:
                await KBService.ingest_document(db, doc, org_id)
                success_count += 1
            except Exception as e:
                failed_docs.append({"filename": doc.filename, "error": str(e)})
                doc.status = "failed"
        
        db.commit()
        
        return {
            "status": "completed",
            "total": len(docs),
            "success": success_count,
            "failed": failed_docs
        }
