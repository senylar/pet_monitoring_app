import os

from django.contrib import admin
from .models import Server, Metric, Incident
from django.db.models import Q
from django.conf import settings

from .utils import fetch_metrics
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import admin, messages
from django import forms
import csv
from io import TextIOWrapper

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    """
    Admin interface for the Metric model.
    """
    list_display = ('server', 'cpu_with_percentage', 'mem_with_percentage', 'disk_with_percentage', 'uptime', 'timestamp')
    list_filter = ('server',)
    change_list_template = os.path.join(settings.BASE_DIR, 'monitor/templates/metrics/change_list.html')

    def cpu_with_percentage(self, obj):
        """
        Display CPU usage with percentage sign.
        """
        return f"{obj.cpu}%"
    cpu_with_percentage.short_description = 'CPU'

    def mem_with_percentage(self, obj):
        """
        Display memory usage with percentage sign.
        """
        return f"{obj.mem}%"
    mem_with_percentage.short_description = 'Memory'

    def disk_with_percentage(self, obj):
        """
        Display disk usage with percentage sign.
        """
        return f"{obj.disk}%"
    disk_with_percentage.short_description = 'Disk'

    def get_urls(self):
        """
        Add custom URL for fetching metrics.
        """
        urls = super().get_urls()
        custom_urls = [
            path('fetch-metrics/', self.admin_site.admin_view(self.fetch_metrics_view), name='fetch_metrics'),
        ]
        return custom_urls + urls

    def fetch_metrics_view(self, request):
        """
        View to fetch metrics and display a success message.
        """
        from .utils import fetch_metrics  # Import function here to avoid circular import
        fetch_metrics()
        self.message_user(request, "Metrics fetched successfully")
        return redirect('..')  # Return to the list page

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """
    Admin interface for the Incident model.
    """
    list_display = ('server', 'metric_type', 'start_time', 'end_time', 'resolved')
    list_filter = ('metric_type', 'resolved')
    search_fields = ('server__name',)

    def get_queryset(self, request):
        """
        Customize the queryset to filter incidents based on metric type and count.
        """
        qs = super().get_queryset(request)
        return qs.filter(
            Q(metric_type='cpu', count__gte=2) |
            Q(metric_type='mem', count__gte=2) |
            Q(metric_type='disk', count__gte=8))

@admin.action(description='Fetch Metrics')
def fetch_metrics_action(modeladmin, request, queryset):
    """
    Admin action to fetch metrics and display a success message.
    """
    fetch_metrics()
    modeladmin.message_user(request, "Metrics fetched successfully")

class CSVImportForm(forms.Form):
    """
    Form for uploading CSV files.
    """
    csv_file = forms.FileField(label='CSV файл')

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    """
    Admin interface for the Server model.
    """
    list_display = ('name', 'endpoint', 'created_at')
    change_list_template = os.path.join(settings.BASE_DIR, 'monitor/templates/servers/change_list.html')

    def get_urls(self):
        """
        Add custom URL for uploading CSV files.
        """
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        """
        View to handle CSV file upload and process the data.
        """
        if request.method == 'POST':
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.DictReader(csv_file)

                for row in reader:
                    Server.objects.create(
                        name=row['name'],
                        endpoint=row['endpoint']
                    )

                self.message_user(request, 'CSV файл успешно загружен и обработан!')
                return redirect('..')  # Return to the list page
        else:
            form = CSVImportForm()

        context = {
            'form': form,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'servers/upload_csv.html', context)