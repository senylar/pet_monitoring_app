import os
import django
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from django.conf import settings
from monitor.models import Metric, Incident, Server
from monitor.utils import check_metric, process_metrics

# Указываем путь к настройкам Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amo_test_monitoring_app.settings")
django.setup()


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class TestMonitor(TestCase):
    def setUp(self):
        # Настройка тестовых данных
        call_command('migrate')

        # Создаем тестовый сервер
        self.server = Server.objects.create(
            name="Test Server",
            endpoint="http://example.com"
        )

        # Настройка settings.METRICS
        settings.METRICS = {
            'cpu': 80,  # Порог и длительность
            'mem': 90,
            'disk': 95
        }

    def tearDown(self):
        # Очистка тестовых данных
        Incident.objects.all().delete()
        Metric.objects.all().delete()
        Server.objects.all().delete()

    def test_check_metric_create_incident(self):
        """Тест создания инцидента при превышении порога."""
        check_metric(self.server, 'cpu', 85, 80, Incident)
        incident = Incident.objects.filter(server=self.server, metric_type='cpu').first()
        self.assertIsNotNone(incident)
        self.assertEqual(incident.count, 1)

    def test_check_metric_increment_count(self):
        """Тест увеличения счетчика инцидента при повторном превышении."""
        check_metric(self.server, 'cpu', 85, 80, Incident)
        check_metric(self.server, 'cpu', 85, 80, Incident)
        incident = Incident.objects.filter(server=self.server, metric_type='cpu').first()
        self.assertEqual(incident.count, 2)

    def test_check_metric_resolve_incident(self):
        """Тест разрешения инцидента при снижении ниже порога."""
        check_metric(self.server, 'cpu', 85, 80, Incident)
        check_metric(self.server, 'cpu', 75, 80, Incident)
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

    def test_process_metrics_with_invalid_disk(self):
        """Тест обработки некорректного значения disk."""
        data = {'cpu': '70', 'mem': '80%', 'disk': 'N/A', 'uptime': '100'}
        with self.assertRaises(ValueError):
            process_metrics(self.server, data, Incident)

    def test_process_metrics_with_missing_uptime(self):
        """Тест обработки данных с отсутствующим ключом uptime."""
        data = {'cpu': '70', 'mem': '80%', 'disk': '90%'}
        with self.assertRaises(KeyError):
            process_metrics(self.server, data, Incident)

    def test_process_metrics_with_invalid_cpu(self):
        """Тест обработки некорректного значения cpu."""
        data = {'cpu': 'N/A', 'mem': '80%', 'disk': '90%', 'uptime': '100'}
        with self.assertRaises(ValueError):
            process_metrics(self.server, data, Incident)

    def test_process_metrics_with_missing_cpu(self):
        """Тест обработки данных с отсутствующим ключом cpu."""
        data = {'mem': '80%', 'disk': '90%', 'uptime': '100'}
        with self.assertRaises(KeyError):
            process_metrics(self.server, data, Incident)


if __name__ == '__main__':
    import unittest
    unittest.main()