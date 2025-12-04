# SaaS Roadmap: Resort Genius

## Current State Summary

The system has partial multi-tenant SaaS infrastructure in place:

| Component | Status | Details |
|-----------|--------|---------|
| Multi-tenant Models | ✅ Ready | `org_id` on all tables, `Organization` model with plans |
| User Authentication | ✅ Ready | JWT with org context, bcrypt password hashing |
| Database Abstraction | ✅ Ready | PostgreSQL + SQLite support, RLS prepared |
| API Endpoints | ⚠️ Partial | Chat/Dashboard working, no auth enforcement |
| Frontend | ⚠️ Partial | Working UI, hardcoded backend URLs |
| Deployment | ⚠️ Partial | Docker/Cloud Run ready, no CI/CD |

---

## Gap Analysis: Current vs Target SaaS

### 1. Authentication & Authorization
**Current**: Auth service exists but NOT enforced on API endpoints
**Gap**:
- [ ] Add `get_current_user` dependency to protected routes
- [ ] Add `get_current_org` middleware for tenant context
- [ ] Add role-based access control (admin/agent/viewer)
- [ ] Add org-aware WebSocket auth for real-time features

### 2. API Security
**Current**: Open endpoints, no rate limiting
**Gap**:
- [ ] Add API authentication middleware
- [ ] Implement per-tenant rate limiting
- [ ] Add request validation/sanitization
- [ ] Add CORS restrictions (currently `allow_origins=["*"]`)

### 3. Multi-Tenancy Enforcement
**Current**: Models support org_id, not enforced in queries
**Gap**:
- [ ] Add tenant filter to all database queries
- [ ] Enable PostgreSQL Row-Level Security (RLS)
- [ ] Add tenant context middleware
- [ ] Isolated KB embeddings per organization

### 4. Frontend Integration
**Current**: Hardcoded cloud backend URL
**Gap**:
- [ ] Use environment variable for API URL
- [ ] Add login/signup pages
- [ ] Add organization onboarding flow
- [ ] Add user session management

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

### Phase 1: Security Foundation (Week 1-2)
1. Add auth middleware to all API endpoints
2. Implement tenant context middleware
3. Add rate limiting (per-IP, per-tenant)
4. Fix CORS to restrict origins

### Phase 2: Frontend Auth (Week 2-3)
1. Add login/signup pages
2. Environment-based API URLs
3. Session management
4. Organization switcher

### Phase 3: Multi-Tenancy Enforcement (Week 3-4)
1. Tenant-scoped database queries
2. Enable PostgreSQL RLS
3. Isolated vector stores per org
4. Tenant-aware file storage

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

1. **Add auth to Dashboard API** - AuthService exists, just wire it
2. **Fix CORS** - Update `allow_origins` in main.py
3. **Add JWT validation decorator** - Use existing `decode_token`
4. **Environment API URL** - Use `NEXT_PUBLIC_API_URL` in frontend

---

## Files to Modify

| Priority | File | Changes Needed |
|----------|------|----------------|
| P0 | `backend/app/main.py` | Add auth middleware, fix CORS |
| P0 | `backend/app/api/chat.py` | Add `get_current_user` dependency |
| P0 | `backend/app/api/dashboard.py` | Add auth + tenant filter |
| P1 | `frontend/components/ChatInterface.tsx` | Use env var for API URL |
| P1 | `frontend/app/login/page.tsx` | [NEW] Login page |
| P2 | `backend/app/middleware/tenant.py` | [NEW] Tenant context middleware |
| P2 | `backend/app/middleware/ratelimit.py` | [NEW] Rate limiter |

---

*Document Location: Stored in repository at `docs/SAAS_ROADMAP.md` for cross-machine access.*
*Last Updated: 2025-12-04*
