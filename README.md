# Resort Genius - AI Agent Assist

**Copyright (c) 2025 Sheers Software Sdn. Bhd. All Rights Reserved.**

## Overview
Resort Genius is an AI-powered agent assist platform designed for the hospitality industry. It combines internal knowledge base retrieval (RAG) with real-time external location data (Google Maps) to provide instant, accurate answers to guest inquiries.

## Features
- **Hybrid Intelligence**: Intelligently routes queries between internal knowledge and external APIs.
- **Smart Filtering**: Distinguishes between on-property facilities and external amenities.
- **RAG Pipeline**: Semantic search over property documentation.
- **Location Services**: Real-time distance and status for nearby places.
- **Markdown Formatting**: Structured, easy-to-read responses for agents.

## Setup

1.  Clone the repository.
2.  Navigate to the `backend` directory.
3.  Copy `.env.example` to `.env` and fill in your API keys:
    ```bash
    cp .env.example .env
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Important:** You must rebuild the vector database if it's missing (it is not tracked in git).
    - Run the database population script (if available) or ensure `backend/chroma_db_v2` is present.
6.  Run the server:
    ```bash
    python -m uvicorn app.main:app --reload
    ```

## Usage
This software is proprietary and confidential. Unauthorized copying, transfer, or use is strictly prohibited.

## Contact
**Sheers Software Sdn. Bhd.**
Ahmad Basyir Azahari
[Contact Information]

## License
See the [LICENSE](LICENSE) file for details.
