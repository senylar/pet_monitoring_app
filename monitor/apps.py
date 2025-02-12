from datetime import datetime

from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        if not self.is_running_test():
            self.start_scheduler()

    def start_scheduler(self):
        from .utils import fetch_metrics  # Импорт внутри метода
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            fetch_metrics,
            'interval',
            minutes=15,
            next_run_time=datetime.now()
        )
        scheduler.start()

    def is_running_test(self):
        import sys
        return 'test' in sys.argv