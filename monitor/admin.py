from django.contrib import admin
from .models import Server, Metric, Incident
from django.db.models import Q

# @admin.register(Server)
# class ServerAdmin(admin.ModelAdmin):
#     list_display = ('name', 'endpoint')

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('server', 'cpu_with_percentage', 'mem_with_percentage', 'disk_with_percentage', 'uptime', 'timestamp')
    list_filter = ('server',)

    def cpu_with_percentage(self, obj):
        return f"{obj.cpu}%"
    cpu_with_percentage.short_description = 'CPU'

    def mem_with_percentage(self, obj):
        return f"{obj.mem}%"
    mem_with_percentage.short_description = 'Memory'

    def disk_with_percentage(self, obj):
        return f"{obj.disk}%"
    disk_with_percentage.short_description = 'Disk'

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('server', 'metric_type', 'start_time', 'end_time', 'resolved')
    list_filter = ('metric_type', 'resolved')
    search_fields = ('server__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            Q(metric_type='cpu', count__gte=2) |
            Q(metric_type='mem', count__gte=2) |
            Q(metric_type='disk', count__gte=8))

from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import admin, messages
from django import forms
from .models import Server
import csv
from io import TextIOWrapper

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV файл')

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint', 'created_at')
    change_list_template = 'change_list.html'  # Кастомный шаблон

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
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
                return redirect('..')  # Возвращаемся на страницу списка
        else:
            form = CSVImportForm()

        context = {
            'form': form,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'upload_csv.html', context)