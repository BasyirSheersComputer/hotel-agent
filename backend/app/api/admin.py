"""
Admin API endpoints for KB management.
All endpoints require admin role.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.middleware.auth import get_current_user, CurrentUser, require_admin
from app.services.kb_service import KBService
from app.config.settings import DEMO_MODE

# Router with admin-only access
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin - KB Management"],
    dependencies=[Depends(require_admin())]
)

# Pydantic models for responses
class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    uploaded_at: datetime
    uploaded_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    message: str

class DeleteResponse(BaseModel):
    success: bool
    message: str

class ReindexResponse(BaseModel):
    status: str
    total: int
    success: int
    failed: List[dict]


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all documents in the organization's knowledge base.
    """
    org_id = current_user.org_id
    
    # Demo mode: return sample documents
    if DEMO_MODE:
        sample_docs = [
            DocumentResponse(
                doc_id="demo-doc-1",
                filename="resort_facilities.pdf",
                status="active",
                uploaded_at=datetime.now(),
                uploaded_by="demo-user"
            ),
            DocumentResponse(
                doc_id="demo-doc-2",
                filename="dining_guide.pdf",
                status="active",
                uploaded_at=datetime.now(),
                uploaded_by="demo-user"
            ),
            DocumentResponse(
                doc_id="demo-doc-3",
                filename="activities_schedule.txt",
                status="active",
                uploaded_at=datetime.now(),
                uploaded_by="demo-user"
            )
        ]
        return DocumentListResponse(documents=sample_docs, total=len(sample_docs))
    
    docs = KBService.list_documents(db, org_id)
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                doc_id=str(doc.doc_id),
                filename=doc.filename,
                status=doc.status,
                uploaded_at=doc.uploaded_at,
                uploaded_by=str(doc.uploaded_by) if doc.uploaded_by else None
            )
            for doc in docs
        ],
        total=len(docs)
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document to the knowledge base.
    Supports PDF and TXT files.
    """
    # Demo mode: simulate upload
    if DEMO_MODE:
        return UploadResponse(
            doc_id="demo-upload-" + str(uuid.uuid4())[:8],
            filename=file.filename,
            status="simulated",
            message="Upload simulated in demo mode. No actual changes made."
        )
    
    org_id = current_user.org_id
    user_id = current_user.user_id
    
    # Validate file type
    allowed_extensions = [".pdf", ".txt", ".md"]
    filename = file.filename or "document.txt"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 50MB"
        )
    
    try:
        doc = await KBService.upload_document(
            db=db,
            org_id=org_id,
            user_id=user_id,
            filename=filename,
            content=content,
            auto_ingest=True
        )
        
        return UploadResponse(
            doc_id=str(doc.doc_id),
            filename=doc.filename,
            status=doc.status,
            message="Document uploaded and indexed successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/document/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document from the knowledge base.
    Also removes from vector database.
    """
    # Demo mode: simulate delete
    if DEMO_MODE:
        return DeleteResponse(
            success=True,
            message="Delete simulated in demo mode. No actual changes made."
        )
    
    org_id = current_user.org_id
    
    success = KBService.delete_document(db, doc_id, org_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DeleteResponse(
        success=True,
        message="Document deleted successfully"
    )


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_knowledge_base(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rebuild the vector database from all active documents.
    Use this after making changes or if the vector DB is corrupted.
    """
    # Demo mode: simulate reindex
    if DEMO_MODE:
        return ReindexResponse(
            status="simulated",
            total=3,
            success=3,
            failed=[]
        )
    
    org_id = current_user.org_id
    
    try:
        result = await KBService.reindex_all(db, org_id)
        
        return ReindexResponse(
            status=result.get("status", "completed"),
            total=result.get("total", 0),
            success=result.get("success", 0),
            failed=result.get("failed", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex failed: {str(e)}")
