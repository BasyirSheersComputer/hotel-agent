# Product Requirements Document (PRD)
## Resort Genius - AI Agent Assist for Hospitality

**Version**: 2.1 (Enhanced)  
**Status**: Production Ready  
**Date**: December 10 2025  
**Product Owner**: Ahmad Basyir Bin Azahari

---

## 1. Product Overview

**Product Name**: Resort Genius  
**Tagline**: Turn every agent into your best agent.  
**Problem**: Hotel call center agents spend 40% of their time searching for information across scattered sources (PDFs, manuals, websites), leading to long hold times (8+ mins), inconsistent answers, and high training costs.  
**Solution**: An AI-powered agent assist dashboard that delivers instant, accurate answers to any guest inquiry in <3 seconds by combining internal knowledge with real-time external data.

### Key Metrics (Success Criteria)
- **Response Time**: <3 seconds per query
- **Accuracy**: >95% with source attribution
- **Adoption**: >90% of agents using daily
- **Efficiency**: 30% reduction in Average Handle Time (AHT)

---

## 2. User Personas

### Primary: The Call Center Agent (Sarah)
- **Role**: Handles 50+ calls/day, multitasking heavily.
- **Pain Points**: Can't find info quickly, hates putting guests on hold, stressed by complex questions.
- **Needs**: Instant answers, "type & forget" UI, trust in the data.

### Secondary: The Operations Manager (David)
- **Role**: Oversees agent performance and training.
- **Pain Points**: High turnover, long training times, inconsistent brand voice.
- **Needs**: Easy onboarding, consistent answers, analytics on query trends.

---

## 3. Core Features & Functional Requirements

### 3.1 Hybrid Intelligence Engine
*The brain of the system.*
- **FR-01**: System must answer questions based on internal documents (PDFs, text).
- **FR-02**: System must answer location-based questions using Google Maps API.
- **FR-03**: System must intelligently route queries between Internal vs. External sources.
  - *Logic*: "Pool" = Internal; "Hospital" = External.
- **FR-04**: System must provide source attribution for every answer.

### 3.2 Smart Knowledge Retrieval (RAG)
*Handling property-specific data.*
- **FR-05**: Ingest and index unstructured text data (Chunk size: 500 chars).
- **FR-06**: Semantic search using vector embeddings (OpenAI text-embedding-3-small).
- **FR-07**: Retrieve top 3-5 relevant chunks for context.
- **FR-08**: Generate natural language response using GPT-4o.

### 3.3 Location Services Integration
*Handling external world data.*
- **FR-09**: Detect location intent keywords ("nearest", "nearby", "distance").
- **FR-10**: Identify place types (hospital, pharmacy, ATM, mall).
- **FR-11**: Calculate real-time Haversine distance from hotel coordinates.
- **FR-12**: Display results with Name, Distance, Rating, and Status (Open/Closed).

### 3.4 User Interface (Agent Dashboard)
*The interaction layer.*
- **FR-13**: Simple chat interface with "Type & Send" functionality.
- **FR-14**: Markdown rendering for structured responses (Bold, Bullets, Headings).
- **FR-15**: Mobile-responsive design for tablet usage.
- **FR-16**: Clear visual distinction between User and AI messages.

### 3.5 Advanced Analytics & Reporting
*Deep insights for management.*
- **FR-17**: Dual-axis trending charts (Volume vs Response Time) with dynamic granularity (Hourly/Daily).
- **FR-18**: Robust data filling ("Zero-Fill") to ensure continuous timelines even with sparse data.
- **FR-19**: Comprehensive date filtering (Today, 48h, 7d, 30d, Custom Range).

---

## 4. Technical Architecture

### 4.1 Tech Stack
- **Frontend**: Next.js (React), Tailwind CSS, TypeScript.
- **Backend**: FastAPI (Python), Uvicorn.
- **AI/ML**: LangChain, OpenAI API (GPT-4o, Embeddings).
- **Database**: ChromaDB (Vector Store), In-memory (for MVP).
- **External APIs**: Google Maps Places API.

### 4.2 Data Flow
1. **User Input** → Frontend → API Request (`/api/chat`).
2. **Backend Routing**:
   - If `is_resort_facility()` → **RAG Pipeline**.
   - If `detect_location_query()` → **Google Maps Service**.
   - Else → **RAG Pipeline**.
3. **Processing**:
   - **RAG**: Query Embeddings → Vector Search → Context Assembly → LLM Generation.
   - **Maps**: Place Search → Distance Calc → Formatting.
4. **Response** → Frontend → Markdown Renderer → **User Display**.

### 4.3 Security & Performance
- **Latency**: API response timeout set to 30s (target <3s).
- **Auth**: API Key validation for external services.
- **Data Privacy**: No PII stored in vector DB; ephemeral chat history.

---

## 5. User Flows

### Flow A: The "Resort Facility" Query
1. **Agent** types: "What time does the pool close?"
2. **System** detects "pool" as resort facility.
3. **System** searches Knowledge Base.
4. **System** returns: "**Main Pool** closes at **8:00 PM**." (Source: `facilities.txt`)

### Flow B: The "External Amenity" Query
1. **Agent** types: "Where is the nearest pharmacy?"
2. **System** detects "nearest" + "pharmacy".
3. **System** calls Google Maps API.
4. **System** returns: "1. **Health Lane Pharmacy** (2.5km) - Open Now."

### Flow C: The "Complex" Query
1. **Agent** types: "Is breakfast included and where is it?"
2. **System** retrieves context on "breakfast" and "restaurants".
3. **System** synthesizes: "Yes, breakfast is included in the All-Inclusive package. It is served at **Mutiara Restaurant** from 7:15 AM."

---

## 6. Implementation Roadmap

### Phase 1: MVP (Completed)
- [x] Core RAG pipeline.
- [x] Basic UI.
- [x] Knowledge base ingestion (23 initial questions).

### Phase 2: Enhanced Intelligence (Completed)
- [x] Google Maps integration.
- [x] Smart routing logic.
- [x] Markdown formatting.
- [x] Expanded knowledge base (100+ questions).

### Phase 3: CFO Analytics & Global Reach (Completed)
- [x] ROI & Financial Metrics Dashboard.
- [x] Executive Reporting (PDF/CSV).
- [x] Multi-language support (50+ languages).
- [x] Persistent Chat History (Session-based).
- [x] **Enhanced Visualizations** (Dual-Axis, Zero-Fill, Dynamic Aggregation).

### Phase 4: SaaS Scale-Up (Next)
- [ ] User Authentication (SSO).
- [ ] Admin Dashboard for KB updates.
- [ ] Multi-tenant Data Isolation.
- [ ] Billing & Subscription Management.

---

## 7. Assumptions & Constraints
- **Internet**: Agents must have stable internet connection.
- **Language**: MVP supports English only.
- **Data**: Hotel provides accurate, up-to-date documentation.
- **API Costs**: Client covers OpenAI and Google Maps usage fees.

---

## 8. Sign-off
**Approved By**:
_________________________ (Product)  
_________________________ (Engineering)  
_________________________ (Operations)
