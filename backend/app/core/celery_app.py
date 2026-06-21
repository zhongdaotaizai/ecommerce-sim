import os
from app.core.config import settings

USE_CELERY = settings.USE_CELERY and settings.CELERY_BROKER_URL is not None
celery_app = None

if USE_CELERY:
    from celery import Celery
    celery_app = Celery("ecommerce_sim", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
    celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="Asia/Shanghai", enable_utc=True, task_track_started=True, task_acks_late=True, worker_prefetch_multiplier=1, broker_connection_retry_on_startup=True)
else:
    class DummyTask:
        def __call__(self, *args, **kwargs):
            return self
        def delay(self, *args, **kwargs):
            if hasattr(self, "_func"):
                return self._func(*args, **kwargs)
            return None
    class DummyCelery:
        def task(self, *args, **kwargs):
            def decorator(f):
                t = DummyTask()
                t._func = f
                return t
            return decorator
    celery_app = DummyCelery()
    print("[Celery] Running in synchronous mode")
