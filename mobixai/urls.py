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
from django.contrib.sitemaps.views import sitemap, index
from ai_models.sitemaps import ArticlesSitemap, StaticPagesSitemap
from reports.admin import reports_admin_site
from django.views.generic import TemplateView

# Sitemaps configuration
sitemaps = {
    'articles': ArticlesSitemap,
    'static': StaticPagesSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', reports_admin_site.urls),  # Custom reports admin
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chatbot.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('ai-models/', include('ai_models.urls')),
    path('', include('core.urls')),  # Include core app URLs
    path('sitemap.xml', index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)