from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status, views
from .models import Host, Snapshot, Process
from .serializers import IngestSerializer, SnapshotOutSerializer
from django.db.models import Max
import psutil
from django.shortcuts import render


def _check_api_key(request):
    key = request.headers.get("X-API-Key")
    return key and key == getattr(settings, "PROC_AGENT_API_KEY", None)

class IngestView(views.APIView):
    authentication_classes = []  # simple header check
    permission_classes = []

    def post(self, request):
        if not _check_api_key(request):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        ser = IngestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        hostname = ser.validated_data["hostname"]
        processes = ser.validated_data["processes"]

        with transaction.atomic():
            host, _ = Host.objects.get_or_create(hostname=hostname)
            snap = Snapshot.objects.create(host=host, captured_at=timezone.now())
            Process.objects.bulk_create([
                Process(
                    snapshot=snap,
                    pid=p["pid"],
                    ppid=p["ppid"],
                    name=p["name"],
                    cpu_percent=p.get("cpu_percent"),
                    mem_rss=p.get("mem_rss"),
                    cmdline=p.get("cmdline", ""),
                )
                for p in processes
            ])

        return Response({"status": "ok", "snapshot_id": snap.id})

class LatestForHostView(views.APIView):
    def get(self, request, hostname):
        try:
            host = Host.objects.get(hostname=hostname)
        except Host.DoesNotExist:
            return Response({"detail": "Host not found"}, status=404)

        snap = host.snapshots.first()
        if not snap:
            return Response({"detail": "No data"}, status=404)
        out = SnapshotOutSerializer(snap).data
        return Response(out)

class LatestAcrossHostsView(views.APIView):
    def get(self, request):
        # Return the latest snapshot for each host
        latest_ids = (Snapshot.objects
                      .values("host_id")
                      .annotate(latest_id=Max("id"))
                      .values_list("latest_id", flat=True))
        snaps = Snapshot.objects.filter(id__in=latest_ids)
        return Response([SnapshotOutSerializer(s).data for s in snaps])

class HostsView(views.APIView):
    def get(self, request):
        data = []
        for h in Host.objects.all():
            latest = h.snapshots.first()
            data.append({
                "hostname": h.hostname,
                "latest_captured_at": latest.captured_at if latest else None
            })
        return Response(data)



class SystemDetailsView(views.APIView):
    """
    Return system details (CPU, Memory, Disk) for a host.
    NOTE: This gives details of the machine where Django is running.
    """

    def get(self, request, hostname):
        try:
            # just check host exists in DB
            Host.objects.get(hostname=hostname)
        except Host.DoesNotExist:
            return Response({"detail": "Host not found"}, status=404)

        # collect system stats
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        data = {
            "cpu_percent": cpu_percent,
            "memory_total": mem.total,
            "memory_used": mem.used,
            "memory_available": mem.available,
            "memory_percent": mem.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_free": disk.free,
            "disk_percent": disk.percent,
            "boot_time": timezone.datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
        return Response(data)

def system(request):
    return render(request,'system.html')