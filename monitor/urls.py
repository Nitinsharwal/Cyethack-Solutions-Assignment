from django.urls import path
from .views import IngestView, LatestForHostView, LatestAcrossHostsView, HostsView, SystemDetailsView, system
from django.views.generic import TemplateView

urlpatterns = [
    path("ingest/", IngestView.as_view()),
    path("latest/<str:hostname>/", LatestForHostView.as_view(), name="latest"),
    path("latest/", LatestAcrossHostsView.as_view(), name="latest_across"),
    path("hosts/", HostsView.as_view(), name="hosts"),
    path("system/<str:hostname>/", SystemDetailsView.as_view(), name="system_api"),  
    path("system/", system, name="system"), 
    path("", TemplateView.as_view(template_name="index.html")),
]
