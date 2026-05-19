# AstraNotes — Deployment Plan

> **Status: DRAFT — Week 10 (CI/CD & Deployment) not yet covered. Render deployment URL and actual CI results will be added after Week 10 class (~2026-06-01).**

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

## Deployment Steps (Manual)

1. Push code to GitHub (ensure `app/`, `AstraNotes_v1/`, `requirements.txt` are committed)
2. Create new **Web Service** on render.com
3. Connect GitHub repository
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable: `JWT_SECRET` = (generate with `openssl rand -hex 32`)
7. Click **Deploy**
8. Wait for deployment (2-3 minutes on free tier)
9. Verify at `https://<app-name>.onrender.com/health`

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
