from django.contrib import admin
from .models import Server, Metric

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint')

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('server', 'cpu', 'timestamp')
    list_filter = ('server',)