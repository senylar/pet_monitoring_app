from datetime import timedelta
from django.utils import timezone
from django.apps import apps
from monitor.models import Metric
import requests
import logging

import traceback

def check_metric(server, metric_type, current_value, threshold, duration, Incident):
    # Получаем последние метрики ��а указанный период
    time_threshold = timezone.now() - duration
    metrics = Metric.objects.filter(
        server=server,
        timestamp__gte=time_threshold
    ).order_by('timestamp')

    # Проверяем, превышает ли значение порога в течение всего периода
    if all(int(getattr(metric, metric_type)) > threshold for metric in metrics):
        # Проверяем, есть ли уже активный инцидент
        active_incident = Incident.objects.filter(
            server=server,
            metric_type=metric_type,
            resolved=False
        ).first()

        if not active_incident:
            # Создаём новый инцидент
            Incident.objects.create(
                server=server,
                metric_type=metric_type,
                start_time=timezone.now()
            )
    else:
        # Если значение вернулось в норму, закрываем инцидент
        active_incident = Incident.objects.filter(
            server=server,
            metric_type=metric_type,
            resolved=False
        ).first()

        if active_incident:
            active_incident.end_time = timezone.now()
            active_incident.resolved = True
            active_incident.save()

import re

def fetch_metrics():
    Server = apps.get_model('monitor', 'Server')
    Metric = apps.get_model('monitor', 'Metric')
    Incident = apps.get_model('monitor', 'Incident')

    servers = Server.objects.all()
    for server in servers:
        try:
            response = requests.get(server.endpoint, timeout=10)

            if response.ok:
                data = response.json()

                mem = re.sub(r'%', '', data['mem'])
                disk = re.sub(r'%', '', data['disk'])
                print(mem, disk)
                # Сохраняем метрику
                metric = Metric.objects.create(
                    server=server,
                    cpu=data['cpu'],
                    mem=mem,
                    disk=disk,
                    uptime=data['uptime']
                )

                # Проверяем условия для CPU
                check_metric(server, 'cpu', int(data['cpu']), 85, timedelta(minutes=30), Incident)

                # Проверяем условия для Memory
                check_metric(server, 'mem', int(mem), 90, timedelta(minutes=30), Incident)

                # Проверяем условия для Disk
                check_metric(server, 'disk', int(disk), 95, timedelta(hours=2), Incident)

        except Exception as e:
            logging.error(f"Ошибка опроса {server.endpoint}: {str(e)}")
            logging.error(traceback.format_exc())