#!/bin/bash
# GhostWorker Deployment Script

set -e

echo "🚀 GhostWorker Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-"deploy"}

case $COMMAND in
    "deploy")
        echo -e "${GREEN}Deploying GhostWorker...${NC}"
        
        # Pull latest images
        docker-compose -f docker-compose.prod.yml pull
        
        # Build custom images
        docker-compose -f docker-compose.prod.yml build --no-cache
        
        # Start services
        docker-compose -f docker-compose.prod.yml up -d
        
        # Wait for services to be healthy
        echo "Waiting for services to start..."
        sleep 10
        
        # Run database migrations
        echo "Running database migrations..."
        docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || true
        
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        ;;
    
    "update")
        echo -e "${YELLOW}Updating GhostWorker...${NC}"
        
        # Pull latest changes (if using git)
        # git pull origin main
        
        # Rebuild and restart
        docker-compose -f docker-compose.prod.yml build --no-cache api worker frontend
        docker-compose -f docker-compose.prod.yml up -d --force-recreate api worker frontend
        
        # Run migrations
        docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || true
        
        echo -e "${GREEN}✓ Update complete!${NC}"
        ;;
    
    "stop")
        echo -e "${YELLOW}Stopping GhostWorker...${NC}"
        docker-compose -f docker-compose.prod.yml down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    
    "restart")
        echo -e "${YELLOW}Restarting GhostWorker...${NC}"
        docker-compose -f docker-compose.prod.yml restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    
    "logs")
        SERVICE=${2:-""}
        if [ -z "$SERVICE" ]; then
            docker-compose -f docker-compose.prod.yml logs -f --tail=100
        else
            docker-compose -f docker-compose.prod.yml logs -f --tail=100 $SERVICE
        fi
        ;;
    
    "status")
        echo -e "${GREEN}Service Status:${NC}"
        docker-compose -f docker-compose.prod.yml ps
        ;;
    
    "backup")
        echo -e "${YELLOW}Creating database backup...${NC}"
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ghostworker ghostworker > "./backups/$BACKUP_FILE"
        echo -e "${GREEN}✓ Backup saved to backups/$BACKUP_FILE${NC}"
        ;;
    
    "restore")
        BACKUP_FILE=$2
        if [ -z "$BACKUP_FILE" ]; then
            echo -e "${RED}Error: Please specify backup file${NC}"
            echo "Usage: ./deploy.sh restore backups/backup_file.sql"
            exit 1
        fi
        echo -e "${YELLOW}Restoring from $BACKUP_FILE...${NC}"
        docker-compose -f docker-compose.prod.yml exec -T db psql -U ghostworker ghostworker < "$BACKUP_FILE"
        echo -e "${GREEN}✓ Restore complete${NC}"
        ;;
    
    "shell")
        SERVICE=${2:-"api"}
        docker-compose -f docker-compose.prod.yml exec $SERVICE /bin/sh
        ;;
    
    "clean")
        echo -e "${YELLOW}Cleaning up unused Docker resources...${NC}"
        docker system prune -f
        docker volume prune -f
        echo -e "${GREEN}✓ Cleanup complete${NC}"
        ;;
    
    *)
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  update   - Update services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (optionally specify service)"
        echo "  status   - Show service status"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore database from backup"
        echo "  shell    - Open shell in container"
        echo "  clean    - Clean unused Docker resources"
        ;;
esac
