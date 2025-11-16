# 🐳 BuckBounty Docker Deployment Guide

Complete guide for running BuckBounty with Docker.

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your API keys (use your favorite editor)
notepad .env  # Windows
nano .env     # Linux/Mac

# 3. Start all services
docker-compose up --build
```

That's it! Access BuckBounty at http://localhost:3000

---

## 📋 Prerequisites

- Docker 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ (included with Docker Desktop)
- API Keys (see `.env.example`)

---

## 🔧 Environment Setup

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Required API Keys

Edit `.env` and add these **required** keys:

```env
# Google Gemini (Free tier available)
GEMINI_API_KEY=your_gemini_api_key_here

# Plaid Sandbox (Free)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_sandbox_secret

# Stripe Test Mode (Free)
STRIPE_API_KEY=sk_test_your_stripe_test_key
```

### 3. Optional API Keys

```env
# ElevenLabs (Optional - for better voice quality)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Gmail API (Optional - for email coupon extraction)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_secret
```

---

## 🏃 Running with Docker Compose

### Start All Services

```bash
# Build and start (first time)
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d
```

### Check Service Status

```bash
# View running containers
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis
```

### Stop Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes data!)
docker-compose down -v
```

---

## 🌐 Service URLs

Once running, access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main BuckBounty UI |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Redis** | localhost:6379 | Cache (internal only) |

---

## 🔍 Troubleshooting

### Issue: "Connection refused" on backend

**Solution:** Backend might still be starting. Check logs:
```bash
docker-compose logs backend
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Issue: "Cannot find module" in frontend

**Solution:** Rebuild frontend with --no-cache:
```bash
docker-compose build --no-cache frontend
docker-compose up frontend
```

### Issue: Redis connection errors

**Solution:** Ensure Redis is healthy:
```bash
docker-compose ps redis

# Should show "healthy" status
# If not, restart Redis:
docker-compose restart redis
```

### Issue: API keys not working

**Solution:**
1. Check `.env` file is in project root
2. Restart containers after updating `.env`:
```bash
docker-compose down
docker-compose up -d
```

### Issue: Port already in use (3000 or 8000)

**Solution:** Change ports in `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "3001:3000"  # Change external port

backend:
  ports:
    - "8001:8000"  # Change external port
```

---

## 🏗️ Manual Docker Build

If you prefer to build and run containers individually:

### Backend

```bash
cd backend

# Build
docker build -t buckbounty-backend .

# Run
docker run -d \
  --name buckbounty-backend \
  -p 8000:8000 \
  --env-file ../.env \
  buckbounty-backend
```

### Frontend

```bash
# Build (from project root)
docker build -t buckbounty-frontend .

# Run
docker run -d \
  --name buckbounty-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  buckbounty-frontend
```

### Redis

```bash
docker run -d \
  --name buckbounty-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes
```

---

## 🚀 Production Deployment

### AWS ECS/Fargate

1. **Push images to ECR:**
```bash
# Tag images
docker tag buckbounty-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/buckbounty-frontend:latest
docker tag buckbounty-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/buckbounty-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/buckbounty-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/buckbounty-backend:latest
```

2. **Set up ElastiCache (Redis):**
   - Create Redis cluster
   - Note endpoint URL
   - Update `REDIS_URL` in environment

3. **Create ECS Task Definitions** using the pushed images

4. **Set up Load Balancer** (ALB) for HTTPS

### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/buckbounty-frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/buckbounty-backend ./backend

# Deploy
gcloud run deploy buckbounty-frontend \
  --image gcr.io/PROJECT-ID/buckbounty-frontend \
  --platform managed \
  --allow-unauthenticated

gcloud run deploy buckbounty-backend \
  --image gcr.io/PROJECT-ID/buckbounty-backend \
  --platform managed \
  --allow-unauthenticated
```

### Heroku

```bash
# Login to Heroku Container Registry
heroku container:login

# Push backend
cd backend
heroku container:push web -a buckbounty-backend
heroku container:release web -a buckbounty-backend

# Push frontend
cd ..
heroku container:push web -a buckbounty-frontend
heroku container:release web -a buckbounty-frontend

# Add Redis addon
heroku addons:create heroku-redis:mini -a buckbounty-backend
```

---

## 🔒 Production Security Checklist

- [ ] Use production API keys (not sandbox/test)
- [ ] Enable HTTPS (use nginx or cloud load balancer)
- [ ] Set `DEBUG=false` in backend
- [ ] Use managed Redis (AWS ElastiCache, Redis Cloud)
- [ ] Configure CORS properly in `backend/main.py`
- [ ] Set up monitoring (CloudWatch, Datadog, etc.)
- [ ] Enable container health checks
- [ ] Use secrets manager for API keys (not .env in production)
- [ ] Set up automated backups for Redis
- [ ] Configure rate limiting on API endpoints

---

## 📊 Resource Requirements

### Minimum (Development)
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB

### Recommended (Production)
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB (for vector DB growth)

---

## 🧪 Health Checks

Both containers include health checks:

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "healthy"}`

### Frontend Health Check
```bash
curl http://localhost:3000
```

Expected: 200 OK response

### Redis Health Check
```bash
docker exec buckbounty-redis redis-cli ping
```

Expected response: `PONG`

---

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `PLAID_CLIENT_ID` | Yes | - | Plaid client ID |
| `PLAID_SECRET` | Yes | - | Plaid API secret |
| `STRIPE_API_KEY` | Yes | - | Stripe API key |
| `ELEVENLABS_API_KEY` | No | - | ElevenLabs API key |
| `PORT` | No | 8000 | Backend port |
| `DEBUG` | No | false | Debug mode |
| `NEXT_PUBLIC_API_URL` | No | http://localhost:8000 | Backend URL |
| `REDIS_URL` | No | redis://redis:6379 | Redis connection URL |

---

## 🔄 Updating the Application

### Pull Latest Changes
```bash
git pull origin main
```

### Rebuild and Restart
```bash
docker-compose down
docker-compose up --build -d
```

### Update Specific Service
```bash
# Update only backend
docker-compose up --build -d backend

# Update only frontend
docker-compose up --build -d frontend
```

---

## 💾 Data Persistence

Data is persisted in Docker volumes:

### View Volumes
```bash
docker volume ls
```

### Backup Data
```bash
# Backup Redis
docker exec buckbounty-redis redis-cli BGSAVE

# Copy Redis dump
docker cp buckbounty-redis:/data/dump.rdb ./backup/

# Backup backend data
docker cp buckbounty-backend:/app/data ./backup/backend_data
```

### Restore Data
```bash
# Restore Redis
docker cp ./backup/dump.rdb buckbounty-redis:/data/
docker-compose restart redis

# Restore backend data
docker cp ./backup/backend_data buckbounty-backend:/app/data
docker-compose restart backend
```

---

## 🎯 Performance Optimization

### Multi-stage Build Caching
Already configured in Dockerfiles. To maximize:

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build
```

### Limit Resource Usage
Edit `docker-compose.yml` to add resource limits:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify environment: `docker-compose config`
3. Test individual services: `docker-compose ps`
4. Consult main [README.md](README.md)
5. Open an issue on GitHub

---

**Happy Deploying!** 🚀
