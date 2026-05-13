from celery import Celery

from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery("cardai_crm", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.services"])

