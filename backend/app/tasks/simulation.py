import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.celery_app import USE_CELERY, celery_app

if USE_CELERY:
    from app.core.simulation_runner import _initialize_system_data as _init_data
    from app.core.simulation_runner import _run_simulation_day as _run_day

    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def initialize_system_data(self):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            result = _init_data(db)
            return result
        except Exception as e:
            db.rollback()
            raise self.retry(exc=e)
        finally:
            db.close()

    @celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
    def run_simulation_day(self):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            result = _run_day(db)
            return result
        except Exception as e:
            raise self.retry(exc=e)
        finally:
            db.close()

else:
    from app.core.simulation_runner import _initialize_system_data as initialize_system_data
    from app.core.simulation_runner import _run_simulation_day as run_simulation_day
