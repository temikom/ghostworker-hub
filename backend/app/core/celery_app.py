from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ghostworker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.ai_tasks",
        "app.workers.tasks.message_tasks",
        "app.workers.tasks.order_tasks",
        "app.workers.tasks.webhook_tasks",
        "app.workers.tasks.analytics_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    
    # Rate limiting
    task_default_rate_limit="100/m",
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "aggregate-analytics-hourly": {
            "task": "app.workers.tasks.analytics_tasks.aggregate_analytics",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-old-webhooks-daily": {
            "task": "app.workers.tasks.webhook_tasks.cleanup_old_webhooks",
            "schedule": 86400.0,  # Every day
        },
        "update-search-index": {
            "task": "app.workers.tasks.analytics_tasks.update_search_index",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)
