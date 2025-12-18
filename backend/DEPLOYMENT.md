# GhostWorker Complete Deployment Guide
## By Temi Kom

This comprehensive guide walks you through deploying GhostWorker on your VPS with both frontend and backend.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Docker Installation](#docker-installation)
4. [Clone & Configure](#clone--configure)
5. [Deploy Backend](#deploy-backend)
6. [Deploy Frontend](#deploy-frontend)
7. [SSL Setup](#ssl-setup)
8. [Verify Deployment](#verify-deployment)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- Ubuntu 20.04+ or Debian 11+
- Minimum 2 vCPU, 4GB RAM, 40GB SSD
- Domain name pointed to your VPS IP (A record)
- SSH access with root or sudo privileges

### Services You'll Need
- **Email**: Gmail App Password or SMTP service (SendGrid, Mailgun)
- **AI**: OpenAI API key (optional for AI features)
- **Payments**: Stripe account (optional for payments)
- **Messaging**: Twilio, WhatsApp Business, or Meta Developer account

---

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git nginx ufw
```

### 2. Configure Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 5555/tcp  # Flower (optional)
sudo ufw enable
sudo ufw status
```

### 3. Create App User (Optional but Recommended)
```bash
sudo adduser ghostworker
sudo usermod -aG sudo ghostworker
sudo usermod -aG docker ghostworker
su - ghostworker
```

---

## Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

## Clone & Configure

### 1. Clone Repository
```bash
cd /home/ghostworker  # or your preferred directory
git clone https://github.com/yourusername/ghostworker.git
cd ghostworker
```

### 2. Configure Backend Environment
```bash
cd backend
cp .env.example .env
nano .env  # or vim .env
```

**Required Environment Variables:**

```env
# SECURITY - Generate these!
SECRET_KEY=<run: openssl rand -hex 32>
ENCRYPTION_KEY=<run: openssl rand -hex 32>
JWT_SECRET_KEY=<run: openssl rand -hex 32>

# DATABASE
POSTGRES_USER=ghostworker
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=ghostworker
DATABASE_URL=postgresql://ghostworker:<password>@db:5432/ghostworker

# REDIS
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# YOUR DOMAIN
FRONTEND_URL=https://yourdomain.com
VITE_API_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# EMAIL (Gmail Example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Gmail App Password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# OPTIONAL: AI
OPENAI_API_KEY=sk-...

# OPTIONAL: PAYMENTS
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OPTIONAL: MESSAGING
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
META_APP_ID=...
META_APP_SECRET=...

# MONITORING
FLOWER_USER=admin
FLOWER_PASSWORD=<strong-password>
```

### 3. Create Backup Directory
```bash
mkdir -p backups
chmod +x scripts/deploy.sh scripts/setup-ssl.sh
```

---

## Deploy Backend

### 1. Start Services
```bash
cd /home/ghostworker/ghostworker/backend

# First deployment
./scripts/deploy.sh deploy

# Watch logs
./scripts/deploy.sh logs
```

### 2. Verify Backend is Running
```bash
# Check containers
docker compose -f docker-compose.prod.yml ps

# Expected output:
# ghostworker-api      running
# ghostworker-worker   running
# ghostworker-beat     running
# ghostworker-db       running
# ghostworker-redis    running
# ghostworker-nginx    running
# ghostworker-frontend running
# ghostworker-flower   running

# Test API health
curl http://localhost:8000/health
```

---

## Deploy Frontend

The frontend is automatically included in `docker-compose.prod.yml`. It builds with the `VITE_API_URL` set to your domain.

### Option A: Docker (Automatic - Recommended)
Already done if you ran `./scripts/deploy.sh deploy`.

### Option B: Separate Build (Manual)
If you want to deploy frontend separately:

```bash
# On your local machine or server
cd /home/ghostworker/ghostworker

# Set API URL
export VITE_API_URL=https://yourdomain.com

# Build
npm install
npm run build

# The dist/ folder contains production files
# Deploy to any static host or nginx
```

---

## SSL Setup

### Option A: Using Certbot (Recommended)
```bash
cd /home/ghostworker/ghostworker/backend

# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily
docker compose -f docker-compose.prod.yml stop nginx

# Get certificate
sudo certbot certonly --standalone \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --non-interactive \
    --agree-tos \
    --email your@email.com

# Copy certificates
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chmod 644 ssl/*.pem
```

### Update Nginx Config for SSL
Edit `nginx.conf` and uncomment the HTTPS server block:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

Restart nginx:
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### Auto-Renewal Cron Job
```bash
(crontab -l 2>/dev/null; echo "0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /home/ghostworker/ghostworker/backend/ssl/ && docker compose -f /home/ghostworker/ghostworker/backend/docker-compose.prod.yml restart nginx") | crontab -
```

---

## Verify Deployment

### 1. Check All Services
```bash
./scripts/deploy.sh status
```

### 2. Test Endpoints
```bash
# Health check
curl https://yourdomain.com/health

# API test
curl https://yourdomain.com/api/v1/health

# Frontend should load in browser
open https://yourdomain.com
```

### 3. Monitor Logs
```bash
# All services
./scripts/deploy.sh logs

# Specific service
./scripts/deploy.sh logs api
./scripts/deploy.sh logs worker
./scripts/deploy.sh logs frontend
```

### 4. Access Flower (Celery Monitoring)
Open `https://yourdomain.com:5555` with the username/password from your `.env` file.

---

## Maintenance

### Daily Operations

```bash
# View status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Restart services
./scripts/deploy.sh restart

# Update after code changes
git pull
./scripts/deploy.sh update
```

### Backups

```bash
# Create backup
./scripts/deploy.sh backup

# Restore backup
./scripts/deploy.sh restore backups/backup_20240101_120000.sql

# Automated daily backups (add to crontab)
0 2 * * * /home/ghostworker/ghostworker/backend/scripts/deploy.sh backup
```

### Updates

```bash
# Pull latest code
cd /home/ghostworker/ghostworker
git pull origin main

# Rebuild and restart
cd backend
./scripts/deploy.sh update
```

### Scaling Workers

Edit `docker-compose.prod.yml`:
```yaml
worker:
  deploy:
    replicas: 4  # Increase workers
```

Apply:
```bash
docker compose -f docker-compose.prod.yml up -d --scale worker=4
```

---

## Troubleshooting

### Container Not Starting

```bash
# View logs
docker compose -f docker-compose.prod.yml logs api

# Check container status
docker compose -f docker-compose.prod.yml ps

# Restart specific service
docker compose -f docker-compose.prod.yml restart api
```

### Database Issues

```bash
# Connect to database
docker compose -f docker-compose.prod.yml exec db psql -U ghostworker -d ghostworker

# View database logs
docker compose -f docker-compose.prod.yml logs db
```

### Worker Tasks Not Running

```bash
# Check worker logs
docker compose -f docker-compose.prod.yml logs worker

# Check beat scheduler
docker compose -f docker-compose.prod.yml logs beat

# Purge queue (if stuck)
docker compose -f docker-compose.prod.yml exec worker celery -A app.core.celery_app purge
```

### Frontend Not Loading

```bash
# Check frontend logs
docker compose -f docker-compose.prod.yml logs frontend

# Rebuild frontend
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### API Returns 502

```bash
# Check if API is running
docker compose -f docker-compose.prod.yml ps api

# Check API logs
docker compose -f docker-compose.prod.yml logs api

# Restart API
docker compose -f docker-compose.prod.yml restart api
```

### Clear Everything & Start Fresh

```bash
# Stop all services
./scripts/deploy.sh stop

# Remove all containers, networks, volumes
docker compose -f docker-compose.prod.yml down -v

# Rebuild everything
./scripts/deploy.sh deploy
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    YOUR VPS (yourdomain.com)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    NGINX (Port 80/443)                     │  │
│  │               SSL Termination + Reverse Proxy              │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
│                            │                                     │
│            ┌───────────────┼───────────────┐                     │
│            │               │               │                     │
│            ▼               ▼               ▼                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Frontend   │  │   FastAPI    │  │   Flower     │           │
│  │   (React)    │  │    (API)     │  │  (Monitor)   │           │
│  │   Port 80    │  │  Port 8000   │  │  Port 5555   │           │
│  └──────────────┘  └──────┬───────┘  └──────────────┘           │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                    │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  PostgreSQL  │  │    Redis     │  │   Celery     │           │
│  │  (Database)  │  │   (Cache)    │  │  (Workers)   │           │
│  │  Port 5432   │  │  Port 6379   │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `./scripts/deploy.sh deploy` | Full deployment |
| `./scripts/deploy.sh update` | Update after code changes |
| `./scripts/deploy.sh stop` | Stop all services |
| `./scripts/deploy.sh restart` | Restart all services |
| `./scripts/deploy.sh logs` | View all logs |
| `./scripts/deploy.sh logs api` | View API logs |
| `./scripts/deploy.sh status` | Show service status |
| `./scripts/deploy.sh backup` | Create database backup |
| `./scripts/deploy.sh restore <file>` | Restore from backup |
| `./scripts/deploy.sh shell api` | Open shell in API container |
| `./scripts/deploy.sh clean` | Clean unused Docker resources |

---

## Integrations Setup

### WhatsApp Business API

1. Create a Meta Developer account at https://developers.facebook.com
2. Create a new app with WhatsApp product
3. Get your Phone Number ID and Access Token
4. Add to `.env`:
   ```env
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   WHATSAPP_ACCESS_TOKEN=your_access_token
   WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_random_verify_token
   ```
5. Configure webhook URL: `https://yourdomain.com/api/v1/webhooks/whatsapp`

### Twilio (SMS/WhatsApp)

1. Create account at https://twilio.com
2. Get Account SID and Auth Token from console
3. Add to `.env`:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Stripe Payments

1. Create account at https://stripe.com
2. Get API keys from Dashboard > Developers
3. Add to `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
4. Configure webhook URL: `https://yourdomain.com/api/v1/webhooks/stripe`

### OpenAI (AI Features)

1. Create account at https://platform.openai.com
2. Generate API key
3. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```

---

## Security Checklist

- [ ] Changed all default passwords in `.env`
- [ ] Generated strong SECRET_KEY, ENCRYPTION_KEY, JWT_SECRET_KEY
- [ ] Enabled SSL with Let's Encrypt
- [ ] Configured firewall (UFW)
- [ ] Set up automated backups
- [ ] Restricted Flower access (port 5555) to admin IPs
- [ ] Enabled 2FA for admin accounts
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## Support

- **Author**: Temi Kom
- **Project**: GhostWorker
- **Documentation**: See README.md

---

## License

Copyright © 2024 Temi Kom. All rights reserved.
