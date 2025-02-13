from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=100)
    endpoint = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpu = models.PositiveSmallIntegerField()  # 0-100%
    mem = models.CharField(max_length=10)     # "30%"
    disk = models.CharField(max_length=10)    # "43%"
    uptime = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class Incident(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=10, choices=[('cpu', 'CPU'), ('mem', 'Memory'), ('disk', 'Disk')])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.server.name} - {self.metric_type} ({'Resolved' if self.resolved else 'Active'})"