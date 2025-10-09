from django.urls import path
from . import admin

urlpatterns = [
    path('dashboard/', admin.reports_admin_site.reports_dashboard, name='reports_dashboard'),
]