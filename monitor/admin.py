from django.contrib import admin
from .models import Server, Metric, Incident

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint')

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