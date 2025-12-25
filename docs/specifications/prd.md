# Product Requirements Document (PRD)
## Resort Genius - AI Agent Assist for Hospitality

**Version**: 3.0 (SaaS Platform Expansion)  
**Status**: In Development  
**Date**: December 25 2025  
**Product Owner**: Ahmad Basyir Bin Azahari

---

## 1. Product Overview

**Product Name**: Resort Genius  
**Tagline**: Turn every agent into your best agent.  
**Problem**: Hotel call center agents spend 40% of their time searching for information while hoteliers struggle with high training costs and inconsistent service quality.  
**Solution**: An AI-powered agent assist dashboard that delivers instant, accurate answers combined with a comprehensive SaaS platform for multi-property management, automated billing, and detailed analytics.

### Key Metrics (Success Criteria)
- **Response Time**: <3 seconds per query
- **Accuracy**: >95% with source attribution
- **Adoption**: >90% of agents using daily
- **Efficiency**: 30% reduction in Average Handle Time (AHT)
- **SaaS Viability**: Fully automated onboarding and billing flow via Stripe.

---

## 2. User Personas & RBAC

### 2.1 Roles & Responsibilities

| Role | Access Level | Description | Example |
| :--- | :--- | :--- | :--- |
| **Super Admin** | System-Wide | Management of all tenants, billing oversight, system health monitoring. | **SaaS Provider (Us)** |
| **Tenant Admin** | Organization | Full control over the Organization (Tenant), subscription, and all properties. | **Club Med HQ** |
| **Property Manager** | Property | Management of a specific hotel's KB, agents, and analytics. | **Manager @ Cherating** |
| **Agent** | Property | Read-only access to Chat and basic personal history. | **Front Desk Staff** |
| **Viewer** | Property | Read-only access to Analytics (e.g., for investors/analysts). | **External Auditor** |

---

## 3. Core Features & Functional Requirements

### 3.1 Hybrid Intelligence Engine (Existing)
*The brain of the system.*
- **FR-01**: RAG-based answer generation from internal KBs.
- **FR-02**: Google Maps integration for external queries.
- **FR-03**: Intelligent routing and source attribution.

### 3.2 SaaS Controller (Super Admin)
*System-wide oversight.*
- **FR-20**: **Tenant Overview**: List all tenants with status (Active/Trial/Churned), plan, and usage metrics.
- **FR-21**: **Global Analytics**: Aggregate query volume, token usage, and error rates across the platform.
- **FR-22**: **System Health**: Monitor API latency and service up-time.

### 3.3 Multi-Property Management
*One Tenant, Many Hotels.*
- **FR-23**: **Hierarchy**: `Tenant (Club Med)` -> `Property (Cherating)` -> `Property (Borneo)`.
- **FR-24**: **Scoped Data**: KB documents and Analytics must be isolatable by Property while accessible to Tenant Admin.

### 3.4 Onboarding & Billing (Stripe)
*Automated revenue engine.*
- **FR-25**: **Self-Serve Signup**: frictionless registration page.
- **FR-26**: **Stripe Integration**:
    - Subscription Plans (Free, Pro, Enterprise).
    - Automated Invoicing & Payment Failure handling.
    - Usage-based billing (optional) for efficient token consumption.
- **FR-27**: **Billing Portal**: Customer portal for upgrading/downgrading/cancelling.

### 3.5 ROI Comparison Engine
*Sales enablement tool.*
- **FR-28**: **"Before vs After" Simulator**: Input current costs (Agent hourly rate, AHT) vs. System Performance to visualize savings.
- **FR-29**: **Investment Feasibility Report**: PDF export of projected ROI for potential investors.

---

## 4. Technical Architecture

### 4.1 Tech Stack
- **Frontend**: Next.js (React), Tailwind CSS.
- **Backend**: FastAPI (Python), Uvicorn.
- **Database**: 
    - **Relational**: PostgreSQL (Users, Orgs, Properties, Billing).
    - **Vector**: ChromaDB (Embeddings, scoped by `org_id` + `property_id`).
- **Billing**: Stripe API.

### 4.2 Data Model Changes
- **Organization**: The paying entity (Tenant).
- **Property**: The physical location (Hotel).
- **User**: Links to Organization (and optionally specific Property).
- **KBDocument**: Scoped to Organization OR Property.

---

## 5. Implementation Roadmap

### Phase 1-3: Completed
- Core RAG, Maps, Dashboard, Analytics.

### Phase 4: SaaS Platform Core (In Progress)
- [x] **User Authentication (SSO/JWT)**
- [x] **Multi-tenant Data Isolation** (Base `org_id`)
- [x] **Multi-Property Architecture** (`property_id` layer, Backend Models Ready)
- [x] **RBAC Implementation** (Roles & Permissions middleware)
- [x] **Onboarding Flow** (Signup & Stripe Checkout APIs)

### Phase 5: Advanced Enterprise Features (New)
- [/] **SaaS Controller Service** (Super Admin Dashboard, Backend API Ready)
- [/] **Stripe Deep Integration** (Webhooks, Checkout, Usage Metering)
- [ ] **ROI Comparison Engine**
- [ ] **Custom Dashboards** (Role-based views)
- [ ] **Production Readiness** (Disable Demo Mode, Full Security Audit)

---

## 6. Assumptions & Constraints
- **Stripe**: Requires Test Mode API keys for development.
- **Postgres**: Development will continue on SQLite with robust schema mirroring production Postgres.
