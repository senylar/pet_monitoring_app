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

