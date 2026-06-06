# AstraNotes — Deployment Plan

> **Status:** Complete — CI/CD operational; Render deployment configured via `render.yaml` (root of repo).

## Overview

AstraNotes v1.0 is deployed as a single-process FastAPI application on Render's free tier. The SQLite database file persists on the server's ephemeral disk (acceptable for a student project demo; production would require a managed database).

## Target Platform: Render (render.com)

**Service type:** Web Service (free tier)  
**Region:** Oregon (US West)  
**Instance:** 0.1 CPU / 512 MB RAM (free tier)

## Deployment Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `JWT_SECRET` | Secret key for JWT signing | **Yes** | `openssl rand -hex 32` |
| `DATABASE_URL` | SQLAlchemy DB URL | No (defaults to `sqlite:///./notes.db`) | `sqlite:///./notes.db` |

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Deployment via render.yaml (Infrastructure-as-Code)

The `render.yaml` in the repo root defines the full service configuration.
Render reads this file automatically when the repo is connected.

```yaml
services:
  - type: web
    name: astranotes
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET
        generateValue: true      # Render auto-generates a secure random value
      - key: DATABASE_URL
        value: sqlite:///./notes.db
```

`JWT_SECRET` uses `generateValue: true` — Render generates a secure secret automatically; no manual entry needed.

## First-Time Setup (one-time)

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect the GitHub repository (`FranklinZhong/AstraNotes-AIDSE`)
3. Render detects `render.yaml` and pre-fills all settings
4. Click **Deploy** — done in ~2 minutes
5. Verify: `https://<app-name>.onrender.com/health`

All subsequent pushes to `main` auto-deploy via the connected repo.

## Post-Deployment Verification

```bash
# Health check
curl https://<app-name>.onrender.com/health

# Register test user
curl -X POST https://<app-name>.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Access UI
open https://<app-name>.onrender.com/
```

## Limitations (Free Tier)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Spin-down after 15 min inactivity | Cold start (~30s) on first request | Acceptable for demo; prod would use paid tier |
| Ephemeral disk | SQLite data lost on redeploy | Acceptable for demo; prod would use PostgreSQL |
| 512 MB RAM | Limits concurrent users | Sufficient for demo (< 10 concurrent users) |

## Known Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| SQLite data loss on redeploy | Medium | Document this as known limitation; demo accounts pre-created |
| JWT_SECRET exposure | Low | Set via Render environment variables, never in code |
| Render free tier unavailability | Low | Have local demo as backup |

## Rollback Procedure

1. Identify the last working commit hash via Render deploy log
2. In Render dashboard → Manual Deploy → select commit hash
3. Click **Deploy** — rollback completes in ~2 minutes

## Local Development

```bash
# Clone and set up
git clone <repo-url>
cd AstraNotes
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally
JWT_SECRET=dev-secret uvicorn app.main:app --reload

# Run tests
python -m pytest -q
```

## CI/CD Status (Week 10)

**GitHub Actions pipeline** (`ci.yml`) is operational as of Sprint 8:

| Trigger | Python versions | Test command | Status |
|---------|----------------|--------------|--------|
| Push to `main` | 3.11, 3.12 | `pytest -q --tb=short` | ✅ Passing — 84 tests |
| PR to `main` | 3.11, 3.12 | `pytest -q --tb=short` | ✅ Active gate |

Test results are uploaded as JUnit XML artifacts with 14-day retention on every CI run.

**Render deployment notes:**
- Free tier instances sleep after 15 minutes of inactivity
- First request after sleep has approximately 30-second cold start
- Demo video should warm up the application before recording live interactions
- `DATABASE_URL` defaults to `sqlite:///./notes.db` (ephemeral on Render; data lost on redeploy — acceptable for demo)
