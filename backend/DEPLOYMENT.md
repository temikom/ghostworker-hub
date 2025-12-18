# GhostWorker Deployment Guide

This guide walks you through deploying GhostWorker on your VPS.

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ VPS
- Minimum 2GB RAM, 2 vCPU, 40GB SSD
- Docker and Docker Compose installed
- Domain name pointed to your VPS IP

## Quick Start

### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/ghostworker.git
cd ghostworker/backend
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required settings to configure:**

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Generate with `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | Strong database password |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SMTP_*` | Email server settings |
| `STRIPE_*` | Stripe API keys (if using payments) |

### 4. Deploy

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy
./scripts/deploy.sh deploy
```

### 5. Setup SSL (Optional but Recommended)

```bash
chmod +x scripts/setup-ssl.sh
sudo ./scripts/setup-ssl.sh yourdomain.com
```

Then update `nginx.conf` to enable HTTPS.

## Frontend Configuration

The frontend connects to your backend via the `VITE_API_URL` environment variable.

### Option A: Build Frontend Separately

Build on your local machine:

```bash
# In the project root (not backend/)
cd ..

# Set your API URL
export VITE_API_URL=https://yourdomain.com

# Build
npm run build

# The dist/ folder contains your production build
```

Upload `dist/` contents to your web server or CDN.

### Option B: Use Docker (Included)

The `docker-compose.prod.yml` includes frontend container:

```bash
# In backend/
VITE_API_URL=https://yourdomain.com docker-compose -f docker-compose.prod.yml up -d
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        NGINX (Port 80/443)                   │
│                    (Reverse Proxy & SSL)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │    FastAPI      │
│   (React App)   │     │   (Port 8000)   │
│    Port 80      │     │                 │
└─────────────────┘     └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
     │  PostgreSQL │    │    Redis    │    │   Celery    │
     │  (Port 5432)│    │ (Port 6379) │    │   Workers   │
     └─────────────┘    └─────────────┘    └─────────────┘
```

## Commands Reference

```bash
# View all services status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs          # All services
./scripts/deploy.sh logs api      # API only
./scripts/deploy.sh logs worker   # Workers only

# Restart services
./scripts/deploy.sh restart

# Update after code changes
./scripts/deploy.sh update

# Create database backup
mkdir -p backups
./scripts/deploy.sh backup

# Restore from backup
./scripts/deploy.sh restore backups/backup_20240101_120000.sql

# Open shell in container
./scripts/deploy.sh shell api
./scripts/deploy.sh shell db

# Stop all services
./scripts/deploy.sh stop

# Clean unused Docker resources
./scripts/deploy.sh clean
```

## Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Monitoring

### Flower (Celery Monitoring)

Access at `http://yourdomain.com:5555` with credentials from `.env`.

### Health Checks

- API: `http://yourdomain.com/health`
- Frontend: `http://yourdomain.com/`

### View Resource Usage

```bash
docker stats
```

## Scaling

### Horizontal Scaling Workers

Edit `docker-compose.prod.yml`:

```yaml
worker:
  deploy:
    replicas: 4  # Increase workers
```

Then restart:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale worker=4
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose -f docker-compose.prod.yml ps db

# View database logs
docker-compose -f docker-compose.prod.yml logs db

# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U ghostworker -d ghostworker
```

### API Not Responding

```bash
# Check API logs
docker-compose -f docker-compose.prod.yml logs api

# Restart API
docker-compose -f docker-compose.prod.yml restart api
```

### Worker Tasks Stuck

```bash
# Check worker logs
docker-compose -f docker-compose.prod.yml logs worker

# Purge task queue (use with caution)
docker-compose -f docker-compose.prod.yml exec worker celery -A app.core.celery_app purge
```

## Security Recommendations

1. **Change default passwords** in `.env`
2. **Enable SSL** with Let's Encrypt
3. **Keep Docker updated**: `sudo apt update && sudo apt upgrade docker-ce`
4. **Regular backups**: Set up daily backup cron job
5. **Monitor logs** for suspicious activity
6. **Restrict Flower access** to admin IPs only

## Frontend API Integration

The frontend is already configured to connect to your backend. Just set the `VITE_API_URL`:

```bash
# During build
VITE_API_URL=https://api.yourdomain.com npm run build

# Or in .env file at project root
VITE_API_URL=https://api.yourdomain.com
```

All API calls go through `src/lib/api.ts` which reads this URL.
