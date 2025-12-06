# SaaS Roadmap: Resort Genius

## Current State Summary

The system has robust multi-tenant SaaS infrastructure in place:

| Component | Status | Details |
|-----------|--------|---------|
| Multi-tenant Models | ✅ Ready | `org_id` on all tables, `Organization` model with plans |
| User Authentication | ✅ Ready | JWT with org context, bcrypt password hashing, AuthContext in Frontend |
| Database Abstraction | ✅ Ready | PostgreSQL + SQLite support, RLS prepared |
| API Endpoints | ✅ Ready | Chat/Dashboard secured with Auth & Rate Limiting |
| Frontend | ✅ Ready | Login page, Auth protection, Environment-based URLs, TypeScript type safety |
| Deployment | ✅ Ready | Docker/Cloud Run ready, Deployment Docs created, DB Migrated |
| Local Development | ✅ Ready | LOCAL_DEV mode bypasses GCP secrets, init_database.py for demo user |

---

## Gap Analysis: Current vs Target SaaS

### 1. Authentication & Authorization
**Current**: Auth enforced on all key endpoints, JWT signing/validation unified
**Gap**:
- [x] Add `get_current_user` dependency to protected routes
- [x] Add `get_current_org` middleware for tenant context
- [x] Fix JWT_SECRET_KEY consistency between auth_service.py and settings.py (Dec 2024)
- [x] Add role-based access control (admin/agent/viewer) - *Implemented in require_role middleware*
- [ ] Add org-aware WebSocket auth for real-time features

### 2. API Security
**Current**: Secured with JWT, Rate Limiting, and CORS
**Gap**:
- [x] Add API authentication middleware
- [x] Implement per-tenant rate limiting
- [x] Add request validation/sanitization
- [x] Add CORS restrictions (configurable via settings)

### 3. Multi-Tenancy Enforcement
**Current**: Application-level tenant filtering implemented, DB Migrated to PG
**Gap**:
- [x] Add tenant filter to all database queries (Metrics Service)
- [x] Migrate to Production Database (PostgreSQL)
- [ ] Enable PostgreSQL Row-Level Security (RLS)
- [x] Add tenant context middleware
- [ ] Isolated KB embeddings per organization

### 4. Frontend Integration
**Current**: Full auth flow with login and session management, TypeScript type safety
**Gap**:
- [x] Use environment variable for API URL
- [x] Add login/signup pages
- [x] Fix TypeScript `any` types in Dashboard, ChatInterface, AuthContext (Dec 2024)
- [x] Fix register() function signature in LoginForm (Dec 2024)
- [ ] Add organization onboarding flow (Registration API exists, UI pending)
- [x] Add user session management
- [x] UI Refinements (History Drawer, Mobile responsiveness)

### 5. Scalability
**Current**: Single instance deployment, Stateless Compute
**Gap**:
- [ ] Stateless session handling (Redis/Memcached) - *Priority for Phase 4*
- [x] Database connection pooling (Application-side Configured) / *PgBouncer recommended for High Scale*
- [x] Implement Caching for RAG (Redis) - *Completed Phase 4*
- [ ] Async task queue for KB ingestion (Celery/RQ)
- [ ] Stateless session handling (Redis/Memcached)
- [ ] CDN for frontend assets

### 6. Observability
**Current**: Basic print logging
**Gap**:
- [ ] Structured logging (JSON)
- [ ] Application metrics (Prometheus)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Error tracking (Sentry)
- [ ] Alerting on anomalies

### 7. Billing & Subscription
**Current**: Plan field exists on Organization
**Gap**:
- [ ] Stripe/Payment integration
- [ ] Usage tracking per tenant
- [ ] Plan enforcement (query limits, KB limits)
- [ ] Billing dashboard

---

## Priority Implementation Order

### Phase 1: Security Foundation (COMPLETED)
1. [x] Add auth middleware to all API endpoints
2. [x] Implement tenant context middleware
3. [x] Add rate limiting (per-IP, per-tenant)
4. [x] Fix CORS to restrict origins

### Phase 2: Frontend Auth & UI (COMPLETED)
1. [x] Add login/signup pages
2. [x] Environment-based API URLs
3. [x] Session management
4. [x] Chat History Drawer & Mobile UI
5. [x] TypeScript type safety fixes (10+ `any` types → properly typed)
6. [ ] Organization switcher

### Phase 3: Database & Multi-Tenancy (COMPLETED)
1. [x] Tenant-scoped database queries (Metrics)
2. [x] Migrate SQLite to PostgreSQL
3. [x] Database Deployment Documentation
4. [ ] Enable PostgreSQL RLS (Future Hardening)
5. [ ] Isolated vector stores per org

### Phase 4: Scalability & Optimization (IN PROGRESS)
**Strategy**: Focus on reducing latency and cost while ensuring high concurrency handling.
1. [x] **Implement RAG Caching** (Redis): Reduce LLM calls for repeated queries (23% speedup verified).
2. [ ] **Async Task Queue**: Offload analytics writes and KB processing (Celery/RQ).
3. [ ] **Stateless Session Store**: Robust session handling for auto-scaling.

### Phase 5: Billing & Observability (Future)
1. Stripe integration
2. Usage metering
3. Structured logging
4. Monitoring dashboards

---

## Quick Wins Available Now

These can be implemented immediately with existing code:

1. **Add auth to Dashboard API** - [x] DONE
2. **Fix CORS** - [x] DONE
3. **Add JWT validation decorator** - [x] DONE
4. **Environment API URL** - [x] DONE
5. **Implement RAG Caching** - [x] DONE
6. **JWT Secret Key Consistency** - [x] DONE (Dec 2024)
7. **TypeScript Type Safety** - [x] DONE (Dec 2024)

---

## Files to Modify

| Priority | File | Changes Needed |
|----------|------|----------------|
| P0 | `backend/app/main.py` | [x] Add auth middleware, fix CORS |
| P0 | `backend/app/api/chat.py` | [x] Add `get_current_user` dependency |
| P0 | `backend/app/api/dashboard.py` | [x] Add auth + tenant filter |
| P1 | `frontend/components/ChatInterface.tsx` | [x] Use env var for API URL |
| P1 | `frontend/app/login/page.tsx` | [x] Login page |
| P2 | `backend/app/middleware/tenant.py` | [x] Tenant context middleware |
| P2 | `backend/app/middleware/ratelimit.py` | [x] Rate limiter |

---

## Recent Updates (December 2024)

### Integration Test Results ✅
- Login API: Working (returns JWT token)
- Chat API: Working (AI responds to queries)
- Browser E2E: Login → Chat flow verified

### Bug Fixes Applied
| Issue | Fix | File |
|-------|-----|------|
| JWT token validation failed | Unified JWT_SECRET_KEY import from settings.py | `auth_service.py` |
| TypeScript `any` types | Added proper interfaces | `Dashboard.tsx`, `ChatInterface.tsx` |
| register() signature mismatch | Fixed function call arguments | `LoginForm.tsx` |
| .env overriding shell vars | Conditional env loading | `env_utils.py` |

### Local Development Setup
```powershell
# Backend (with LOCAL_DEV to skip GCP secrets)
$env:LOCAL_DEV='true'; python -m uvicorn app.main:app --port 8000

# Frontend
npm run dev
```
**Demo Credentials:** `admin@demo-hotel.com` / `admin123` / `demo-hotel`

---

*Document Location: Stored in repository at `docs/SAAS_ROADMAP.md` for cross-machine access.*
*Last Updated: 2024-12-06*
