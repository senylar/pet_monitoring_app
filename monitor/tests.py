
import os
import django

# Указываем путь к настройкам Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amo_test_monitoring_app.settings")
django.setup()

import os
import django
from django.test import TestCase
import requests
import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from monitor.models import Metric, Incident, Server
from monitor.utils import check_metric, process_metrics, fetch_metrics, fetch_metrics_for_test

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'amo_test_monitoring_app.settings'

# Initialize Django
django.setup()

class TestMonitor(unittest.TestCase):
    def setUp(self):
        # Настройка тестовых данных
        self.server = Server(endpoint="http://127.0.0.1:5000")
        self.server.save()

        self.incident = Incident(
            server=self.server,
            metric_type='cpu',
            start_time=timezone.now(),
            resolved=False,
            count=0
        )
        self.incident.save()

        # Настройка settings.METRICS
        settings.METRICS = {
            'cpu': (80, timedelta(minutes=5)),
            'mem': (90, timedelta(minutes=10)),
            'disk': (95, timedelta(minutes=15))
        }

    def tearDown(self):
        # Очистка тестовых данных
        Incident.objects.all().delete()
        Metric.objects.all().delete()
        Server.objects.all().delete()

    def test_check_metric_create_incident(self):
        """Тест создания инцидента при превышении порога."""
        print(self.incident.count)
        check_metric(self.server, 'cpu', 85, 80, timedelta(minutes=30), Incident)
        incident = Incident.objects.filter(server=self.server, metric_type='cpu').first()
        self.assertIsNotNone(incident)
        self.assertEqual(incident.count, 1)

    def test_check_metric_increment_count(self):
        """Тест увеличения счетчика инцидента при повторном превышении."""
        check_metric(self.server, 'cpu', 85, 80, timedelta(minutes=5), Incident)
        check_metric(self.server, 'cpu', 85, 80, timedelta(minutes=5), Incident)
        incident = Incident.objects.filter(server=self.server, metric_type='cpu').first()
        self.assertEqual(incident.count, 2)

    def test_check_metric_resolve_incident(self):
        """Тест разрешения инцидента при снижении ниже порога."""
        check_metric(self.server, 'cpu', 85, 80, timedelta(minutes=5), Incident)
        check_metric(self.server, 'cpu', 75, 80, timedelta(minutes=5), Incident)
        incident = Incident.objects.filter(server=self.server, metric_type='cpu').first()
        self.assertTrue(incident.resolved)

    def test_process_metrics_with_valid_data(self):
        """Тест обработки корректных данных."""
        data = {'cpu': '70', 'mem': '80%', 'disk': '90%', 'uptime': '100'}
        process_metrics(self.server, data, Incident)
        metric = Metric.objects.filter(server=self.server).first()
        self.assertEqual(metric.cpu, 70)
        self.assertEqual(metric.mem, 80)
        self.assertEqual(metric.disk, 90)

    def test_process_metrics_with_invalid_mem(self):
        """Тест обработки некорректного значения mem."""
        data = {'cpu': '70', 'mem': 'N/A', 'disk': '90%', 'uptime': '100'}
        with self.assertRaises(ValueError):
            process_metrics(self.server, data, Incident)

    def test_process_metrics_with_missing_key(self):
        """Тест обработки данных с отсутствующим ключом."""
        data = {'cpu': '70', 'disk': '90%', 'uptime': '100'}
        with self.assertRaises(KeyError):
            process_metrics(self.server, data, Incident)

    @patch('requests.get')
    def test_fetch_metrics_success(self, mock_get):
        """Тест успешного опроса сервера."""
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {'cpu': '70', 'mem': '80%', 'disk': '90%', 'uptime': '100'}
        fetch_metrics()
        metric = Metric.objects.filter(server=self.server).first()
        self.assertIsNotNone(metric)

    @patch('requests.get')
    def test_fetch_metrics_timeout(self, mock_get):
        """Тест обработки таймаута при опросе сервера."""
        mock_get.side_effect = requests.Timeout
        with self.assertLogs(level='ERROR') as log:
            fetch_metrics()
            # Проверяем, что ошибка залогирована
            self.assertTrue(any("Timeout" in message for message in log.output))

    @patch('requests.get')
    def test_fetch_metrics_for_test_success(self, mock_get):
        """Тест успешного опроса сервера для тестового эндпоинта."""
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {'cpu': '70', 'mem': '80%', 'disk': '90%', 'uptime': '100'}
        fetch_metrics_for_test('cpu', 70)
        metric = Metric.objects.filter(server=self.server).first()
        self.assertIsNotNone(metric)

    def get_logs(self):
        """Вспомогательная функция для получения логов."""
        import logging
        from io import StringIO
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logging.getLogger().addHandler(handler)
        return log_stream.getvalue()


if __name__ == '__main__':
    unittest.main()