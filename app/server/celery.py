"""Celery configuration."""

from celery import Celery
from kombu import Queue

from core.config import settings

# Create Celery instance
celery_app = Celery(
    "sunog",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.lyrics_tasks",
        "workers.audio_tasks", 
        "workers.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "workers.lyrics_tasks.*": {"queue": "lyrics"},
        "workers.audio_tasks.*": {"queue": "audio"},
        "workers.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("lyrics", routing_key="lyrics"),
        Queue("audio", routing_key="audio"),
        Queue("notifications", routing_key="notifications"),
    ),
    
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Almaty",
    enable_utc=True,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Result backend
    result_expires=3600,       # 1 hour
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule
    beat_schedule={
        "cleanup-expired-assets": {
            "task": "workers.cleanup_tasks.cleanup_expired_assets",
            "schedule": 86400.0,  # Daily
        },
    },
)

# Optional configuration for production
if not settings.debug:
    celery_app.conf.update(
        worker_hijack_root_logger=False,
        worker_log_color=False,
    )

