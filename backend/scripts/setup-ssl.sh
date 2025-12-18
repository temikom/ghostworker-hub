#!/bin/bash
# SSL Certificate Setup Script using Certbot

set -e

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
    echo "Usage: ./setup-ssl.sh yourdomain.com"
    exit 1
fi

echo "Setting up SSL for $DOMAIN..."

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx || true

# Get certificate
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --non-interactive \
    --agree-tos \
    --email admin@$DOMAIN

# Create ssl directory and copy certificates
mkdir -p ssl
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/

# Set permissions
chmod 644 ssl/*.pem

echo "✓ SSL certificates installed"
echo ""
echo "Now update nginx.conf to enable HTTPS:"
echo "1. Uncomment the HTTPS server block"
echo "2. Update server_name to $DOMAIN"
echo "3. Restart nginx"

# Setup auto-renewal cron job
(crontab -l 2>/dev/null; echo "0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/*.pem $(pwd)/ssl/ && docker-compose -f docker-compose.prod.yml restart nginx") | crontab -

echo "✓ Auto-renewal cron job added"
