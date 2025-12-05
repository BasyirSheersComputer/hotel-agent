# SaaS Roadmap: Resort Genius

## Current State Summary

The system has robust multi-tenant SaaS infrastructure in place:

| Component | Status | Details |
|-----------|--------|---------|
| Multi-tenant Models | ✅ Ready | `org_id` on all tables, `Organization` model with plans |
| User Authentication | ✅ Ready | JWT with org context, bcrypt password hashing, AuthContext in Frontend |
| Database Abstraction | ✅ Ready | PostgreSQL + SQLite support, RLS prepared |
| API Endpoints | ✅ Ready | Chat/Dashboard secured with Auth & Rate Limiting |
| Frontend | ✅ Ready | Login page, Auth protection, Environment-based URLs |
| Deployment | ⚠️ Partial | Docker/Cloud Run ready, no CI/CD |

---

## Gap Analysis: Current vs Target SaaS

### 1. Authentication & Authorization
**Current**: Auth enforced on all key endpoints
**Gap**:
- [x] Add `get_current_user` dependency to protected routes
- [x] Add `get_current_org` middleware for tenant context
- [ ] Add role-based access control (admin/agent/viewer) - *Partial support in middleware*
- [ ] Add org-aware WebSocket auth for real-time features

### 2. API Security
**Current**: Secured with JWT, Rate Limiting, and CORS
**Gap**:
- [x] Add API authentication middleware
- [x] Implement per-tenant rate limiting
- [x] Add request validation/sanitization
- [x] Add CORS restrictions (configurable via settings)

### 3. Multi-Tenancy Enforcement
**Current**: Application-level tenant filtering implemented
**Gap**:
- [x] Add tenant filter to all database queries (Metrics Service)
- [ ] Enable PostgreSQL Row-Level Security (RLS)
- [x] Add tenant context middleware
- [ ] Isolated KB embeddings per organization

### 4. Frontend Integration
**Current**: Full auth flow with login and session management
**Gap**:
- [x] Use environment variable for API URL
- [x] Add login/signup pages
- [ ] Add organization onboarding flow (Registration API exists, UI pending)
- [x] Add user session management

### 5. Scalability
**Current**: Single instance deployment
**Gap**:
- [ ] Stateless session handling (Redis/Memcached)
- [ ] Database connection pooling (pgBouncer)
- [ ] Async task queue for KB ingestion (Celery/RQ)
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

### Phase 2: Frontend Auth (COMPLETED)
1. [x] Add login/signup pages
2. [x] Environment-based API URLs
3. [x] Session management
4. [ ] Organization switcher

### Phase 3: Multi-Tenancy Enforcement (IN PROGRESS)
1. [x] Tenant-scoped database queries (Metrics)
2. [ ] Enable PostgreSQL RLS
3. [ ] Isolated vector stores per org
4. [ ] Tenant-aware file storage

### Phase 4: Scalability (Week 4-6)
1. Redis for session cache
2. Background job queue
3. Database read replicas
4. CDN setup

### Phase 5: Billing & Observability (Week 6-8)
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

*Document Location: Stored in repository at `docs/SAAS_ROADMAP.md` for cross-machine access.*
*Last Updated: 2025-12-05*
