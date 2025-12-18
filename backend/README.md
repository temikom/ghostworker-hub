# GhostWorker Backend

A production-ready FastAPI backend for GhostWorker - an AI-powered business communication automation platform.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Update `.env` with your credentials

3. Start with Docker:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

5. Access the API:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── teams.py
│   │   │   ├── inbox.py
│   │   │   ├── conversations.py
│   │   │   ├── messages.py
│   │   │   ├── customers.py
│   │   │   ├── orders.py
│   │   │   ├── tags.py
│   │   │   ├── templates.py
│   │   │   ├── analytics.py
│   │   │   ├── integrations.py
│   │   │   ├── webhooks.py
│   │   │   ├── n8n.py
│   │   │   └── ai.py
│   │   └── deps.py          # Dependencies
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # JWT & auth
│   │   └── celery_app.py    # Celery config
│   ├── db/
│   │   ├── base.py          # Base model
│   │   ├── session.py       # DB session
│   │   └── init_db.py       # DB initialization
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── workers/             # Celery tasks
├── alembic/                 # Migrations
├── tests/                   # Test suite
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.worker
└── requirements.txt
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password
- `GET /auth/me` - Get current user

### Users & Teams
- `GET /users` - List users
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `GET /teams` - List teams
- `POST /teams` - Create team
- `PUT /teams/{id}` - Update team

### Inbox & Messaging
- `GET /inbox` - Get unified inbox
- `GET /conversations` - List conversations
- `GET /conversations/{id}` - Get conversation
- `POST /conversations/{id}/tags` - Add tags
- `GET /messages/{conversation_id}` - Get messages
- `POST /messages/send` - Send message

### Customers
- `GET /customers` - List customers
- `POST /customers` - Create customer
- `GET /customers/{id}` - Get customer
- `PUT /customers/{id}` - Update customer
- `GET /customers/{id}/activity` - Get activity

### Orders
- `GET /orders` - List orders
- `POST /orders` - Create order
- `GET /orders/{id}` - Get order
- `PUT /orders/{id}/status` - Update status

### Tags & Templates
- `GET /tags` - List tags
- `POST /tags` - Create tag
- `PUT /tags/{id}` - Update tag
- `DELETE /tags/{id}` - Delete tag
- `GET /templates` - List templates
- `POST /templates` - Create template
- `PUT /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template

### Analytics
- `GET /analytics/messages` - Message analytics
- `GET /analytics/response-time` - Response time metrics
- `GET /analytics/channels` - Channel distribution
- `GET /analytics/customers` - Top customers
- `GET /analytics/orders` - Orders summary

### Integrations
- `GET /integrations` - List integrations
- `POST /integrations/connect` - Connect integration
- `POST /integrations/disconnect` - Disconnect
- `POST /webhooks/whatsapp` - WhatsApp webhook
- `POST /webhooks/instagram` - Instagram webhook
- `POST /webhooks/tiktok` - TikTok webhook

### AI
- `POST /ai/reply` - Generate AI reply
- `POST /ai/suggest` - Suggest actions
- `POST /ai/summarize` - Summarize conversation
- `POST /ai/extract-order` - Extract order intent
- `POST /ai/categorize` - Categorize message

### N8N
- `POST /n8n/trigger` - Trigger workflow
- `GET /n8n/workflows` - List workflows
- `POST /n8n/webhook` - Receive N8N callback

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Access database
docker-compose exec db psql -U ghostworker -d ghostworker

# Restart worker
docker-compose restart worker

# Stop all services
docker-compose down
```

## 🔐 Security

- JWT tokens with access/refresh flow
- Password hashing with bcrypt
- Rate limiting on sensitive endpoints
- CORS configuration
- SQL injection protection via SQLAlchemy
- Input validation via Pydantic

## 📊 Background Tasks

Celery handles:
- AI reply generation
- Message sending to platforms
- Order processing
- Webhook fan-out to N8N
- Analytics aggregation
- Search indexing

## 🧪 Testing

```bash
# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app

# Run specific test
docker-compose exec api pytest tests/test_auth.py
```

## 📝 License

Proprietary - GhostWorker
