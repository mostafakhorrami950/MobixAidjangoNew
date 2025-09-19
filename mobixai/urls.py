"""
URL configuration for mobixai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chatbot.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('', include('core.urls')),  # Include core app URLs
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# Serve static and media files during development
if settings.DEBUG:
    # Static files (CSS, JS, images)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Media files (uploaded content)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
