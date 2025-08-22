from django.contrib import admin
from .models import Host, SystemInfo, Snapshot, Process

# Register your models here
@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('hostname',)

@admin.register(SystemInfo)
class SystemInfoAdmin(admin.ModelAdmin):
    list_display = ('host', 'os', 'os_version', 'release', 'machine', 'processor', 'cpu_count', 'ram_total_gb', 'disk_total_gb', 'disk_used_gb')

@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('host', 'captured_at')
    list_filter = ('captured_at',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('snapshot', 'pid', 'ppid', 'name', 'cpu_percent', 'mem_rss')
    search_fields = ('name', 'cmdline')
