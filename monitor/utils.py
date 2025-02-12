from django.apps import apps
import requests

def fetch_metrics():
    Server = apps.get_model('monitor', 'Server')
    Metric = apps.get_model('monitor', 'Metric')

    servers = Server.objects.all()
    for server in servers:
        try:
            response = requests.get(server.endpoint, timeout=10)
            if response.ok:
                data = response.json()
                Metric.objects.create(
                    server=server,
                    cpu=data['cpu'],
                    mem=data['mem'],
                    disk=data['disk'],
                    uptime=data['uptime']
                )
        except Exception as e:
            print(f"Ошибка опроса {server.endpoint}: {str(e)}")