from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog
import time

from app.core.config import settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.audit import AuditLogMiddleware
from app.api.routes import (
    auth, users, teams, inbox, conversations, messages,
    customers, orders, tags, templates, analytics,
    integrations, webhooks, n8n, ai, oauth
)
from app.api.routes import sessions
from app.db.session import engine
from app.db.base import Base

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting GhostWorker API", version="1.0.0")
    yield
    logger.info("Shutting down GhostWorker API")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered business communication automation platform",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Log Middleware
app.add_middleware(AuditLogMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ghostworker-api", "version": "1.0.0"}


# API v1 Routes with versioned prefix
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(oauth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["OAuth"])
app.include_router(sessions.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Sessions & 2FA"])
app.include_router(users.router, prefix=f"{API_V1_PREFIX}/users", tags=["Users"])
app.include_router(teams.router, prefix=f"{API_V1_PREFIX}/teams", tags=["Teams"])
app.include_router(inbox.router, prefix=f"{API_V1_PREFIX}/inbox", tags=["Inbox"])
app.include_router(conversations.router, prefix=f"{API_V1_PREFIX}/conversations", tags=["Conversations"])
app.include_router(messages.router, prefix=f"{API_V1_PREFIX}/messages", tags=["Messages"])
app.include_router(customers.router, prefix=f"{API_V1_PREFIX}/customers", tags=["Customers"])
app.include_router(orders.router, prefix=f"{API_V1_PREFIX}/orders", tags=["Orders"])
app.include_router(tags.router, prefix=f"{API_V1_PREFIX}/tags", tags=["Tags"])
app.include_router(templates.router, prefix=f"{API_V1_PREFIX}/templates", tags=["Templates"])
app.include_router(analytics.router, prefix=f"{API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(integrations.router, prefix=f"{API_V1_PREFIX}/integrations", tags=["Integrations"])
app.include_router(webhooks.router, prefix=f"{API_V1_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(n8n.router, prefix=f"{API_V1_PREFIX}/n8n", tags=["N8N"])
app.include_router(ai.router, prefix=f"{API_V1_PREFIX}/ai", tags=["AI"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "api_version": "v1",
        "docs": "/api/v1/docs"
    }
