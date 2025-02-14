import logging
import os
from datetime import datetime

from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'
    scheduler = None

    def ready(self):
        # Проверяем, что это основной процесс (не автоперезагрузчик)
        if os.environ.get('RUN_MAIN') != 'true':
            return

        logging.warning(self.scheduler)
        if not self.is_running_test() and not self.scheduler:
            self.start_scheduler()

    def start_scheduler(self):
        if not self.scheduler:
            from .utils import fetch_metrics
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(
                fetch_metrics,
                'interval',
                minutes=15,
                next_run_time=datetime.now(),
                id='fetch_metrics_job'
            )
            self.scheduler.start()
            logging.info("Scheduler started with job 'fetch_metrics_job'.")
        else:
            logging.warning("Scheduler is already running.")

    def is_running_test(self):
        import sys
        return 'test' in sys.argv