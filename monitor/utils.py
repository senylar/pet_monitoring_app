from datetime import timedelta
from django.utils import timezone
from django.apps import apps
from django.conf import settings
import requests
import logging
import traceback
import re
from monitor.models import Metric

def check_metric(server, metric_type, current_value, threshold, duration, Incident):
    if current_value > threshold:
        active_incident = Incident.objects.filter(
            server=server,
            metric_type=metric_type,
            resolved=False
        ).first()

        if not active_incident:
            Incident.objects.create(
                server=server,
                metric_type=metric_type,
                start_time=timezone.now()
            )
        else:
            active_incident.count += 1
            active_incident.save()
    else:
        active_incident = Incident.objects.filter(
            server=server,
            metric_type=metric_type,
            resolved=False
        ).first()

        if active_incident:
            active_incident.end_time = timezone.now()
            active_incident.resolved = True
            active_incident.save()

def process_metrics(server, data, Incident):
    data['mem'] = mem = re.sub(r'%', '', data['mem'])
    data['disk'] = disk = re.sub(r'%', '', data['disk'])
    print(mem, disk)

    Metric.objects.create(
        server=server,
        cpu=data['cpu'],
        mem=mem,
        disk=disk,
        uptime=data['uptime']
    )

    for metric_type, (threshold, duration) in settings.METRICS.items():
        value = data[metric_type]

        current_value = int(value)
        check_metric(server, metric_type, current_value, threshold, duration, Incident)


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
                process_metrics(server, data, Incident)

        except requests.exceptions.Timeout:
            logging.error(f"Timeout while polling {server.endpoint}")
        except Exception as e:
            logging.error(f"Error polling {server.endpoint}: {str(e)}")

def fetch_metrics_for_test(metrics, val):
    Server = apps.get_model('monitor', 'Server')
    Metric = apps.get_model('monitor', 'Metric')
    Incident = apps.get_model('monitor', 'Incident')

    servers = Server.objects.all()
    for server in servers:
        try:
            response = requests.get(server.endpoint + f'/met/{metrics}/{val}', timeout=10)

            if response.ok:
                data = response.json()
                process_metrics(server, data, Incident)

        except Exception as e:
            logging.error(f"Ошибка опроса {server.endpoint}: {str(e)}")
            logging.error(traceback.format_exc())