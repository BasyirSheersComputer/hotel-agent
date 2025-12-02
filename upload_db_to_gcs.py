"""
Upload local vector database to Google Cloud Storage.
Run this script after populating the database locally.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gcs_utils import upload_vector_db_to_gcs

if __name__ == "__main__":
    print("=" * 80)
    print("UPLOAD VECTOR DB TO GOOGLE CLOUD STORAGE")
    print("=" * 80)
    
    # Path to local vector DB
    local_db_path = os.path.join(os.path.dirname(__file__), "backend", "chroma_db_v2")
    
    if not os.path.exists(local_db_path):
        print(f"\n✗ ERROR: Vector database not found at {local_db_path}")
        print("Please run 'python backend/populate_db.py' first to create the database.")
        sys.exit(1)
    
    print(f"\nLocal DB path: {local_db_path}")
    print(f"GCS Bucket: {os.getenv('GCS_BUCKET_NAME', 'hotel-agent-vectordb')}")
    print("\nStarting upload...")
    
    success = upload_vector_db_to_gcs(local_db_path)
    
    if success:
        print("\n" + "=" * 80)
        print("✓ UPLOAD COMPLETE")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ UPLOAD FAILED")
        print("=" * 80)
        sys.exit(1)
