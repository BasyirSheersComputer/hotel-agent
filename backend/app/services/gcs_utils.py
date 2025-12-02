"""
Utility module for Google Cloud Storage operations.
Handles downloading and caching the ChromaDB vector database from GCS.
"""
import os
import shutil
from pathlib import Path
from google.cloud import storage

# GCS Configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "hotel-agent-vectordb")
GCS_DB_PATH = "chroma_db_v2"  # Path in bucket
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db_v2")

def download_vector_db_from_gcs():
    """
    Download the vector database from Google Cloud Storage to local filesystem.
    Returns True if successful, False otherwise.
    """
    try:
        # Check if DB already exists locally
        if os.path.exists(LOCAL_DB_PATH) and os.listdir(LOCAL_DB_PATH):
            print(f"Vector DB already exists at {LOCAL_DB_PATH}")
            return True
        
        print(f"Downloading vector DB from GCS bucket: {GCS_BUCKET_NAME}")
        
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        # Create local directory
        os.makedirs(LOCAL_DB_PATH, exist_ok=True)
        
        # List all blobs in the chroma_db_v2 folder
        blobs = bucket.list_blobs(prefix=f"{GCS_DB_PATH}/")
        
        downloaded_count = 0
        for blob in blobs:
            # Skip directory markers
            if blob.name.endswith('/'):
                continue
            
            # Get relative path within chroma_db_v2
            relative_path = blob.name[len(GCS_DB_PATH)+1:]  # Remove prefix
            if not relative_path:
                continue
            
            # Full local path
            local_file_path = os.path.join(LOCAL_DB_PATH, relative_path)
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download the file
            blob.download_to_filename(local_file_path)
            downloaded_count += 1
            print(f"  Downloaded: {relative_path}")
        
        print(f"✓ Successfully downloaded {downloaded_count} files from GCS")
        return True
        
    except Exception as e:
        print(f"✗ Error downloading vector DB from GCS: {e}")
        return False

def upload_vector_db_to_gcs(local_db_path=None):
    """
    Upload the local vector database to Google Cloud Storage.
    
    Args:
        local_db_path: Path to the local chroma_db_v2 directory. 
                      Defaults to LOCAL_DB_PATH.
    
    Returns:
        True if successful, False otherwise.
    """
    if local_db_path is None:
        local_db_path = LOCAL_DB_PATH
    
    try:
        if not os.path.exists(local_db_path):
            print(f"✗ Local vector DB not found at {local_db_path}")
            return False
        
        print(f"Uploading vector DB to GCS bucket: {GCS_BUCKET_NAME}")
        
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        # Walk through all files in the directory
        uploaded_count = 0
        for root, dirs, files in os.walk(local_db_path):
            for file in files:
                local_file = os.path.join(root, file)
                
                # Get relative path from local_db_path
                relative_path = os.path.relpath(local_file, local_db_path)
                
                # GCS blob path
                blob_path = f"{GCS_DB_PATH}/{relative_path.replace(os.sep, '/')}"
                
                # Upload
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(local_file)
                uploaded_count += 1
                print(f"  Uploaded: {relative_path}")
        
        print(f"✓ Successfully uploaded {uploaded_count} files to GCS")
        return True
        
    except Exception as e:
        print(f"✗ Error uploading vector DB to GCS: {e}")
        return False
