# Resort Genius - AI Agent Assist for Hospitality

**Version**: 1.0.0 (Stable) | 2.0.0 (In Development - SaaS)  
**Status**: Production Ready (Single-Tenant)

---

## 🎯 Overview

Resort Genius is an AI-powered agent assist platform that delivers instant, accurate answers to guest inquiries in <3 seconds. It combines internal knowledge bases with real-time external data to help hotel call center agents provide exceptional service.

### Key Features

- **Hybrid Intelligence Engine**: Combines RAG (Retrieval-Augmented Generation) with Google Maps API
- **Smart Query Routing**: 100% accuracy in detecting internal vs external queries
- **CFO-Grade Analytics**: Real-time financial & operational metrics (ROI, Efficiency, Accuracy, CSAT)
- **Automated Reporting**: "Club Med" style PDF/CSV executive summaries
- **Multi-Language Support**: Real-time auto-translation for 50+ languages
- **Cloud-Native**: Deployable to Google Cloud Run or any container platform

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Google Maps API Key

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/resort-genius.git
cd resort-genius

# Backend setup
cd backend
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your-key" > .env
echo "GOOGLE_MAPS_API_KEY=your-key" >> .env

# Frontend setup
cd ../frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Running Locally

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Access the application:
- **Chat Interface**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard
- **API Docs**: http://localhost:8000/docs

---

## 📚 Documentation

### Version 1.0 (Current Stable)
- [Complete System Specification](SYSTEM_SPEC_V1.0.md)
- [Product Requirements](prd.md)
- [Testing & Validation](dashboard_verification_report.md)

### Version 2.0 (In Development)
- [SaaS Architecture Review](saas_architecture_review.md)
- [Phase 3 Implementation Plan](phase3_implementation_plan.md)

---

## 🏗️ Architecture

**v1.0 (Single-Tenant)**:
```
Frontend (Next.js) → Backend API (FastAPI) → RAG / Google Maps
                                           → SQLite (Metrics)
                                           → ChromaDB (Vectors)
```

**v2.0 (Multi-Tenant SaaS)** - In Development:
```
Frontend → Backend (Multi-tenant) → PostgreSQL + RLS
                                  → Redis (Sessions)
                                  → pgvector (Embeddings)
                                  → Cloud Storage
```

---

## 📊 Features by Version

### v1.0 - Stable (Current Branch: `main`)

| Feature | Status |
|---------|--------|
| RAG Knowledge Retrieval | ✅ |
| Google Maps Integration | ✅ |
| Smart Query Routing | ✅ |
| ROI/Financial Dashboard | ✅ |
| PDF/CSV Reporting | ✅ |
| Multi-Language Support | ✅ |
| Persistent Chat History | ✅ |
| User Authentication | ❌ |

### v2.0 - SaaS (Development Branch: `feature/v2-saas` & `feature/auth-dashboard-fixes`)

| Feature | Status |
|---------|--------|
| All v1.0 Features | ✅ |
| User Authentication (JWT) | ✅ Done |
| Multi-Tenant Isolation | ✅ Done |
| Custom Dashboards | ✅ Done |
| Knowledge Base Management | ✅ Done |
| PostgreSQL + pgvector | ✅ Done |
| Persistent Chat History | 📅 Planned |
| Multi-Language Support | 📅 Planned |
| Redis Sessions | 📅 Planned |
| Cloud Storage Integration | 📅 Planned |

---

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Location routing accuracy test
python test_location_routing.py

# Dashboard verification
python test_dashboard.py
```

### Test Results (v1.0)
- **Location Routing Accuracy**: 100% (57/57 queries)
- **Dashboard Integration**: ✅ All metrics verified
- **Response Time**: Average 1.5-3 seconds

---

## 🚢 Deployment

### Local Development
See [Quick Start](#quick-start) above.

### Google Cloud Run

```bash
# Deploy backend
gcloud run deploy resort-genius-backend \
  --source backend \
  --region us-central1

# Deploy frontend
gcloud run deploy resort-genius-frontend \
  --source frontend \
  --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_URL=https://your-backend-url
```

---

## 📈 Performance Metrics

- **Response Time**: < 3 seconds (avg 1.5s)
- **Accuracy**: 95%+ overall, 100% routing accuracy
- **Uptime**: 99.9%
- **Concurrent Users**: Tested up to 50

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
ENABLE_METRICS=true
DATABASE_URL=sqlite:///./analytics.db  # v1.0
# DATABASE_URL=postgresql://...  # v2.0
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📝 API Documentation

### Endpoints (v1.0)

- `POST /api/chat` - Submit query (supports multi-language)
- `GET /api/metrics/summary` - Get dashboard ROI summary
- `GET /api/reports/export` - Export financial CSV reports
- `GET /api/reports/export-pdf` - Export Executive PDF Summary
- `GET /api/metrics/categories` - Get question category breakdown
- `GET /api/metrics/trends` - Get hourly trends
- `GET /api/metrics/agents` - Get agent performance

Interactive API docs: http://localhost:8000/docs

---

## 🛠️ Development

### Project Structure

```
resort-genius/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic
│   │   └── main.py   # App entry point
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/          # Pages and routes
│   ├── components/   # React components
│   └── package.json
└── docs/             # Documentation
```

### Git Workflow

**Branches**:
- `main` - Stable v1.0 (single-tenant)
- `feature/v2-saas` - Development v2.0 (multi-tenant SaaS)

**Versioning**:
- v1.x.x - Single-tenant stable releases
- v2.x.x - Multi-tenant SaaS releases

---

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main` (for v1.x fixes) or `feature/v2-saas` (for v2.x features)
2. Make changes and test locally
3. Submit pull request with description
4. Code review and merge

---

## 📄 License

Copyright © 2025 Sheers Software Sdn. Bhd.  
All Rights Reserved.

---

## 🆘 Support

For issues or questions:
- Check documentation in `/docs`
- Review [System Specification](SYSTEM_SPEC_V1.0.md)
- Contact: support@resortgenius.com

---

## 📌 Version History

### v1.0.0 (2025-12-04) - Current Stable
- ✅ Core RAG pipeline
- ✅ Google Maps integration
- ✅ Smart query routing (100% accuracy)
- ✅ Performance dashboard
- ✅ Real-time metrics tracking
- ✅ Chat-dashboard integration
- 📦 Single-tenant deployment ready

### v2.0.0 (In Development)
- 🚧 Multi-tenant SaaS architecture
- 🚧 User authentication (JWT)
- 📅 Persistent chat history
- 📅 Admin dashboard for KB management
- 📅 Multi-language support
- 📅 PostgreSQL + Redis + Cloud Storage

---

**Built with ❤️ for the hospitality industry**
