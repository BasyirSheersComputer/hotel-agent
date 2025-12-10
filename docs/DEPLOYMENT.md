# Deployment Guide

This guide covers deployment for both **Google Cloud** (Scalable/Serverless) and **On-Premise** (Docker/VM).

## 1. Google Cloud Deployment

### Architecture
- **Frontend**: Google Cloud Run (Containerized Next.js).
- **Backend**: Google Cloud Run (Containerized FastAPI).
- **Database**: Cloud SQL (PostgreSQL 15+) with `pgvector` extension.
- **Vector Store**: ChromaDB (Hydrated from GCS) OR Migrate to PGVector (Recommended for persistent scale).
- **Storage**: Google Cloud Storage (for PDFs/Images).

### Prerequisites
- Google Cloud Project with Billing enabled.
- Cloud SDK (`gcloud`) installed.

### Steps

#### A. Database (Cloud SQL)
1.  **Create Instance**:
    ```bash
    gcloud sql instances create hotel-agent-db --database-version=POSTGRES_15 --cpu=2 --memory=8GB --region=us-central1
    ```
2.  **Create Database & User**:
    ```bash
    gcloud sql databases create hotel_agent --instance=hotel-agent-db
    gcloud sql users create hotel_admin --instance=hotel-agent-db --password=[SECURE_PASSWORD]
    ```
3.  **Enable Extensions**:
    Connect to the DB and run:
    ```sql
    CREATE EXTENSION vector;
    ```

#### B. Backend (Cloud Run)
1.  **Build Container**:
    ```bash
    cd backend
    gcloud builds submit --tag gcr.io/[PROJECT_ID]/hotel-backend
    ```
2.  **Deploy**:
    ```bash
    gcloud run deploy hotel-backend \
      --image gcr.io/[PROJECT_ID]/hotel-backend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars DATABASE_URL="postgresql://hotel_admin:[PASSWORD]@[DB_IP]:5432/hotel_agent" \
      --set-env-vars DB_POOL_ENABLED="false" \
      --set-env-vars OPENAI_API_KEY=[KEY]
    ```
    *Note: Use Cloud SQL Auth Proxy or VPC Connector for secure DB connection.*

#### C. Frontend (Cloud Run)
1.  **Build Container**:
    ```bash
    cd frontend
    gcloud builds submit --tag gcr.io/[PROJECT_ID]/hotel-frontend
    ```
2.  **Deploy**:
    ```bash
    gcloud run deploy hotel-frontend \
      --image gcr.io/[PROJECT_ID]/hotel-frontend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars NEXT_PUBLIC_API_URL=[BACKEND_URL]
    ```

---

## 2. On-Premise Deployment

### Architecture
- **Docker Compose**: Orchestrates setup on a single VM/Server.

### Hardware Requirements (Optimal Performance)
- **CPU**: 4 vCPUs (2 for App, 2 for DB).
- **RAM**: 8 GB RAM (4GB min).
- **Disk**: 50 GB SSD.

### Steps
1.  **Clone Repository**:
    ```bash
    git clone https://github.com/your-repo/hotel-agent.git
    cd hotel-agent
    ```
2.  **Configure Environment**:
    - Update `backend/.env` with production keys.
    - Ensure `DATABASE_URL` matches the internal docker service name (e.g. `postgres`).
3.  **Run with Docker Compose**:
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --build
    ```
    *(Note: Create `docker-compose.prod.yml` combining backend, frontend, and db services).*

---

## 3. Local Development (Quickstart)

### One-Click Startup (Recommended)
We provide a robust startup script that handles port conflicts, dependency checks, and launches both Backend and Frontend automatically.

1.  **Windows**:
    ```cmd
    start_system.bat
    ```
    *This wraps `start_system.ps1` which gracefully cleans up ports 3000/8000 before starting.*

2.  **Manual Start**:
    If you prefer manual control:
    *   **Backend**:
        ```bash
        cd backend
        python -m uvicorn app.main:app --reload --port 8000
        ```
    *   **Frontend**:
        ```bash
        cd frontend
        npm run dev
        ```

---

## 4. Compute Sizing (Recommendation)

| Component | Google Cloud (optimal) | On-Prem / VM (Minimum) |
|-----------|------------------------|------------------------|
| **Backend** | Cloud Run: 2 vCPU, 2GB RAM (Auto-scaling) | 2 vCPU, 2GB RAM |
| **Frontend**| Cloud Run: 1 vCPU, 512MB RAM | 1 vCPU, 1GB RAM |
| **Database**| Cloud SQL: db-custom-2-3840 (2 vCPU, 3.75GB) | 2 vCPU, 4GB RAM |

**Note**: For high concurrency (100+ concurrent users), ensure Database `flux` (IOPS) is sufficient (SSD).
