# Deployment Guide - Cirujano System

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Monitoring & Logs](#monitoring--logs)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)

## Prerequisites

### Required Tools

- Docker & Docker Compose 20.10+
- Git
- Node.js 20.x
- Python 3.11
- PostgreSQL 15
- Redis 7

### Required Credentials

- GitHub token (for registry)
- SSH keys for production servers
- Database credentials
- API keys for third-party services
- Slack webhook for notifications

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cirujano_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development
DEBUG=true

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=password

# Storage
STORAGE_TYPE=local
STORAGE_PATH=./uploads
```

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/cirujano/cirujano-front.git
cd cirujano-front

# Setup environment
cp .env.example .env

# Start services with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database (optional)
docker-compose exec backend python scripts/seed_database.py

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Frontend Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Run tests
npm run test

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run application
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Staging Deployment

### Prerequisites

```bash
# SSH access to staging server
ssh user@staging.cirujano.app

# Set up deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo passwd deploy
```

### Deploy via CI/CD

Push to `develop` branch to trigger automatic staging deployment:

```bash
git checkout develop
git pull origin develop
# Make changes
git commit -m "feat: new feature"
git push origin develop

# GitHub Actions automatically:
# 1. Runs tests
# 2. Builds Docker images
# 3. Pushes to registry
# 4. Deploys to staging
# 5. Runs smoke tests
```

### Manual Staging Deployment

```bash
# SSH into staging server
ssh deploy@staging.cirujano.app

# Navigate to project
cd /var/www/cirujano-staging

# Pull latest code
git pull origin develop

# Update dependencies
npm ci
pip install -r backend/requirements.txt

# Build frontend
npm run build

# Pull latest Docker images
docker-compose -f docker-compose.staging.yml pull

# Start services
docker-compose -f docker-compose.staging.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify deployment
curl https://staging.cirujano.app/api/health
```

### Staging Health Checks

```bash
# Check services
docker-compose -f docker-compose.staging.yml ps

# View logs
docker-compose -f docker-compose.staging.yml logs -f backend

# Check database
docker-compose exec postgres psql -U cirujano -d cirujano_db -c "SELECT COUNT(*) FROM repairs;"

# Monitor metrics
curl https://staging.cirujano.app/api/logs/stats
```

## Production Deployment

### Prerequisites

1. **Infrastructure Setup**
   - Load balancer (nginx/HAProxy)
   - Database backup system
   - Monitoring (Prometheus/Grafana)
   - Log aggregation (ELK/Loki)

2. **Security**
   - SSL/TLS certificates (Let's Encrypt)
   - Firewall rules
   - VPN/SSH key authentication
   - Secrets management (Vault)

3. **Backup & Recovery**
   - Automated database backups (daily)
   - Backup verification (weekly)
   - Recovery testing (monthly)

### Deployment Steps

```bash
# 1. Create deployment checklist
# [ ] Code reviewed and tested
# [ ] Database backups created
# [ ] Current state backed up
# [ ] Rollback plan documented
# [ ] Team notified

# 2. Prepare for deployment
ssh deploy@cirujano.app
cd /var/www/cirujano

# 3. Backup current state
cp -r app app.backup.$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml export > backup.tar

# 4. Database backup
docker-compose exec postgres pg_dump -U cirujano cirujano_db > backup.sql

# 5. Pull latest code
git pull origin main
git log -1 --oneline  # Verify commit

# 6. Update dependencies
npm ci
pip install -r backend/requirements.txt --upgrade

# 7. Build frontend
npm run build

# 8. Run pre-deployment tests
npm run test:smoke  # Verify environment

# 9. Build Docker images
docker-compose build

# 10. Blue-Green Deployment
# Keep old containers running (Blue)
# Start new containers (Green) in parallel

# 11. Start new containers
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# 12. Wait for services to initialize
sleep 30

# 13. Run database migrations
docker-compose exec backend alembic upgrade head

# 14. Health checks on all instances
for i in {1..3}; do
  curl -f https://cirujano.app/api/health || exit 1
done

# 15. Monitor for errors (5 minutes)
watch -n 5 'curl https://cirujano.app/api/logs/stats'

# 16. If all OK, remove old containers
docker system prune -f

# 17. Verify in monitoring
# - Check error rates
# - Check response times
# - Check resource usage
```

## Quick Reference

- **Local Dev**: `docker-compose up -d`
- **Staging Deploy**: Push to `develop`
- **Production Deploy**: Push to `main`
- **View Logs**: `docker-compose logs -f`
- **Database Migration**: `alembic upgrade head`
- **Rollback**: `cp -r app.backup app`
