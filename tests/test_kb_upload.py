
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import Base
from app.models import Organization, User, KBDocument
from app.services.kb_service import KBService

# Setup DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestKBUpload(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()
        
        # Create Org and User
        self.org = Organization(name="Test Org", slug="test-org")
        self.db.add(self.org)
        self.db.commit()
        self.db.refresh(self.org)
        
        self.user = User(
            org_id=self.org.org_id,
            email="test@test.com",
            password_hash="pw",
            name="Test User"
        )
        self.db.add(self.user)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    @patch('app.services.kb_service.KBService.ingest_document')
    async def test_upload_flow(self, mock_ingest):
        """Test file upload to DB + Call to Ingest"""
        
        # Mock Ingest to just return True (avoid actual vector logic for this unit)
        mock_ingest.return_value = None
        
        content = b"This is a test document content about pool hours."
        filename = "pool_info.txt"
        
        print("Uploading document...")
        doc = await KBService.upload_document(
            db=self.db,
            org_id=self.org.org_id,
            user_id=self.user.user_id,
            filename=filename,
            content=content,
            auto_ingest=True
        )
        
        print(f"Document created: {doc.doc_id} Status: {doc.status}")
        
        # Verify DB integrity
        assert doc.filename == filename
        assert doc.org_id == self.org.org_id
        assert doc.status == "active"  # Should be active if ingest succeeds (mocked)
        
        # Verify Ingest was called
        mock_ingest.assert_called_once()
        print("PASS: Ingestion triggered.")

    @patch('langchain_community.document_loaders.TextLoader')
    @patch('langchain_text_splitters.RecursiveCharacterTextSplitter')
    @patch('langchain_openai.OpenAIEmbeddings')
    @patch('langchain_chroma.Chroma')
    async def test_ingestion_logic(self, mock_chroma, mock_embeddings, mock_splitter, mock_loader):
        """Test the actual Ingestion logic (Chunking -> Embedding) with mocks"""
        
        # Setup Mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [MagicMock(page_content="Test Content")]
        mock_loader.return_value = mock_loader_instance
        
        mock_splitter_instance = MagicMock()
        mock_chunk = MagicMock(page_content="Test Content", metadata={})
        mock_splitter_instance.split_documents.return_value = [mock_chunk]
        mock_splitter.return_value = mock_splitter_instance
        
        mock_vectordb = MagicMock()
        mock_chroma.return_value = mock_vectordb
        
        # Crate Doc Record
        doc = KBDocument(
            doc_id=uuid.uuid4(),
            org_id=self.org.org_id,
            filename="test.txt",
            file_url="test.txt", # won't be read by loader due to mock
            status="processing"
        )
        
        print("Simulating Ingestion...")
        await KBService.ingest_document(self.db, doc, self.org.org_id)
        
        # Verify Steps
        mock_loader.assert_called()
        print("PASS: Loader initialized.")
        
        mock_splitter.assert_called()
        print("PASS: Text Splitter initialized.")
        
        mock_chroma.assert_called()
        print("PASS: Vector DB initialized.")
        
        mock_vectordb.add_documents.assert_called()
        print(f"PASS: add_documents called with {mock_vectordb.add_documents.call_args}")
        
        # Verify Metadata usage
        # chunk metadata should now have source/doc_id/org_id
        args, _ = mock_vectordb.add_documents.call_args
        chunks = args[0]
        assert chunks[0].metadata["doc_id"] == str(doc.doc_id)
        assert chunks[0].metadata["org_id"] == str(self.org.org_id)
        print("PASS: Metadata correctly assigned.")

if __name__ == "__main__":
    unittest.main()
