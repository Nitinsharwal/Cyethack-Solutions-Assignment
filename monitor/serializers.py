from rest_framework import serializers
from .models import Host, Snapshot, Process, SystemInfo

class SystemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemInfo
        fields = "__all__"

class ProcessInSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    ppid = serializers.IntegerField()
    name = serializers.CharField()
    cpu_percent = serializers.FloatField(required=False, allow_null=True)
    mem_rss = serializers.IntegerField(required=False, allow_null=True)
    cmdline = serializers.CharField(required=False, allow_blank=True)

class IngestSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    system_info = serializers.DictField(required=False)
    processes = ProcessInSerializer(many=True)

class ProcessOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["pid", "ppid", "name", "cpu_percent", "mem_rss", "cmdline"]

class SnapshotOutSerializer(serializers.ModelSerializer):
    host = serializers.CharField(source="host.hostname")
    processes = ProcessOutSerializer(many=True)

    class Meta:
        model = Snapshot
        fields = ["host", "captured_at", "processes"]
