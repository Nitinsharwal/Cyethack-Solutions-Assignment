from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.hostname

class SystemInfo(models.Model):
    host = models.OneToOneField(Host, on_delete=models.CASCADE, related_name="system_info")
    os = models.CharField(max_length=100)
    os_version = models.TextField()
    release = models.CharField(max_length=100)
    machine = models.CharField(max_length=50)
    processor = models.CharField(max_length=200)
    cpu_count = models.IntegerField()
    ram_total_gb = models.FloatField()
    disk_total_gb = models.FloatField()
    disk_used_gb = models.FloatField()

class Snapshot(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="snapshots")
    captured_at = models.DateTimeField(auto_now_add=True)

class Process(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name="processes")
    pid = models.IntegerField()
    ppid = models.IntegerField()
    name = models.CharField(max_length=300)
    cpu_percent = models.FloatField(null=True, blank=True)
    mem_rss = models.BigIntegerField(null=True, blank=True)
    cmdline = models.TextField(blank=True, default="")
