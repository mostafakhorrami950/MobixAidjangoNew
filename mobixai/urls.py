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
from django.conf import settings
from django.conf.urls.static import static
from reports.admin import reports_admin_site
import os
from django.http import HttpResponse
from ai_models.views import static_sitemap, articles_sitemap

# Custom view for sitemap index
def sitemap_index(request):
    # Simple sitemap index XML
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://mobixai.ir/sitemap-static.xml</loc>
        <lastmod>2025-10-12T00:00:00+00:00</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://mobixai.ir/sitemap-articles.xml</loc>
        <lastmod>2025-10-12T00:00:00+00:00</lastmod>
    </sitemap>
</sitemapindex>'''
    return HttpResponse(content.encode('utf-8'), content_type='application/xml')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', reports_admin_site.urls),  # Custom reports admin
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chatbot.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('ai-models/', include('ai_models.urls')),
    path('', include('core.urls')),  # Include core app URLs
    
    # Sitemap URLs
    path('sitemap.xml', sitemap_index, name='sitemap-index'),
    path('sitemap-static.xml', static_sitemap, name='sitemap-static'),
    path('sitemap-articles.xml', articles_sitemap, name='sitemap-articles'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)