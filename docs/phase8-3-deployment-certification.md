# Phase 8.3 Deployment & Operational Runbook

**GeoVerify India — Deployment Certification Guide**  
**Version:** `8.3.0`  
**Date:** October 2026  

---

## 1. Clean Environment Deployment Steps

### Step 1: Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/maneaditya478-commits/GeoVerify.git
cd GeoVerify

# Python Virtual Environment
python -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

pip install -r backend/requirements.txt
```

### Step 2: Initialize Geographic Data & Dense Indexes
```bash
# Verify catalog and dense vector pre-indexing
python -c "from app.entity_resolution.candidates import candidate_generator; print(f'Loaded: {len(candidate_generator.states)} states, {len(candidate_generator.districts)} districts')"
```

### Step 3: Start Backend Fast-API Application
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Verify Health & Readiness Probes
```bash
# Liveness Probe (Instantaneous 200 OK)
curl http://localhost:8000/health/live

# Readiness Probe (Checks catalog, dense index, OCR availability)
curl http://localhost:8000/health/ready

# Telemetry Overview
curl http://localhost:8000/health/telemetry
```

### Step 5: Start Frontend Dashboard
```bash
cd frontend
npm install
npm run build
npm run preview
```

---

## 2. Production Docker Deployment

GeoVerify includes hardened Dockerfiles for containerized environments:

```bash
# Build backend container
docker build -t geoverify-backend:8.3.0 -f backend/Dockerfile .

# Run with bounded memory and non-root user
docker run -d \
  --name geoverify-api \
  -p 8000:8000 \
  --memory=2g \
  --cpus=2 \
  -e APP_ENV=production \
  -e GEOVERIFY_CONFIG_VERSION=8.3.0 \
  geoverify-backend:8.3.0
```

---

## 3. Rollback Procedure

If deployment issues occur:
1. Revert container image tag to `8.2.0`:
   ```bash
   docker service update --image geoverify-backend:8.2.0 geoverify-service
   ```
2. Invalidate cache layer by rotating `GEOVERIFY_CONFIG_VERSION` in environment variables.
3. Verify `/health/ready` returns `status: "ready"`.
