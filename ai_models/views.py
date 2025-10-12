from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
import markdown
from .models import AIModel, ModelArticle
from django.utils import timezone
from xml.sax.saxutils import escape
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

def model_article_detail(request, slug):
    """
    Display a detailed article about an AI model
    """
    article = get_object_or_404(
        ModelArticle._default_manager.select_related('ai_model'), 
        slug=slug, 
        is_published=True
    )
    
    # Process markdown content
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'pymdownx.superfences',
        'pymdownx.highlight'
    ])
    
    article.content_html = md.convert(article.content)
    
    # Get related models (if any)
    related_articles = ModelArticle._default_manager.filter(
        is_published=True
    ).exclude(
        id=article.id
    ).select_related('ai_model')[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    
    return render(request, 'ai_models/article_detail.html', context)

def model_articles_list(request):
    """
    Display a list of all published model articles
    """
    articles = ModelArticle._default_manager.filter(
        is_published=True
    ).select_related('ai_model').order_by('-created_at')
    
    context = {
        'articles': articles,
    }
    
    return render(request, 'ai_models/articles_list.html', context)

def articles_sitemap(request):
    """
    Generate and serve the articles sitemap dynamically
    """
    # Get all published articles
    articles = ModelArticle._default_manager.filter(is_published=True).order_by('-updated_at')
    
    # Start building the sitemap XML with proper formatting
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''
    
    # Add articles to sitemap
    for article in articles:
        # Format last modified date in W3C format
        lastmod = article.updated_at.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        
        # Build the URL using Django's get_absolute_url method for accuracy
        full_url = f'https://mobixai.ir{article.get_absolute_url()}'
        
        sitemap_content += f'''  <url>
    <loc>{escape(full_url)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
'''
        
        # Add image information if available
        if article.image:
            # Ensure we have the correct absolute URL for the image
            image_url = f'https://mobixai.ir{article.image.url}'
            sitemap_content += f'''    <image:image>
      <image:loc>{escape(image_url)}</image:loc>
      <image:title>{escape(article.title)}</image:title>
      <image:caption>{escape(article.excerpt if article.excerpt else article.title)}</image:caption>
    </image:image>
'''
        
        sitemap_content += '  </url>\n'
    
    # Close the sitemap
    sitemap_content += '</urlset>\n'
    
    return HttpResponse(sitemap_content.encode('utf-8'), content_type='application/xml')

class StaticPagesSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        # Return a list of named URLs for static pages
        return [
            'home',
            'register', 
            'login',
            'model_articles_list',
            'terms_and_conditions',
            'dashboard',
            'financial_transactions'
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return current date for static pages
        return timezone.now()
        
    def changefreq(self, obj):
        # Define specific change frequencies for different pages
        changefreq_map = {
            'home': 'daily',
            'dashboard': 'daily',
            'model_articles_list': 'weekly',
            'financial_transactions': 'weekly',
            'terms_and_conditions': 'yearly',
            'register': 'monthly',
            'login': 'monthly'
        }
        return changefreq_map.get(obj, 'monthly')
        
    def priority(self, obj):
        # Define specific priorities for different pages
        priority_map = {
            'home': 1.0,
            'dashboard': 0.8,
            'model_articles_list': 0.8,
            'financial_transactions': 0.6,
            'terms_and_conditions': 0.5,
            'register': 0.9,
            'login': 0.9
        }
        return priority_map.get(obj, 0.5)

def static_sitemap(request):
    """
    Generate and serve the static pages sitemap dynamically
    """
    # Create sitemap instance
    sitemap = StaticPagesSitemap()
    
    # Start building the sitemap XML with proper formatting
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''
    
    # Get all items
    items = sitemap.items()
    
    # Add static pages to sitemap
    for item in items:
        # Get the URL
        url = sitemap.location(item)
        full_url = f'https://mobixai.ir{url}'
        
        # Get lastmod (current date)
        lastmod = timezone.now().strftime('%Y-%m-%d')
        
        # Get changefreq and priority
        changefreq = sitemap.changefreq(item)
        priority = sitemap.priority(item)
        
        sitemap_content += f'''  <url>
    <loc>{escape(full_url)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
'''
        
        # Add specific image information for certain pages
        if item == 'register':
            sitemap_content += '''    <image:image>
      <image:loc>https://mobixai.ir/static/images/registration-illustration.jpg</image:loc>
      <image:title>ثبت نام در MobixAI</image:title>
      <image:caption>ثبت نام رایگان در پلتفرم هوش مصنوعی پیشرفته فارسی</image:caption>
    </image:image>
'''
        elif item == 'login':
            sitemap_content += '''    <image:image>
      <image:loc>https://mobixai.ir/static/images/login-illustration.jpg</image:loc>
      <image:title>ورود به MobixAI</image:title>
      <image:caption>ورود به پلتفرم هوش مصنوعی پیشرفته فارسی</image:caption>
    </image:image>
'''
        elif item == 'model_articles_list':
            sitemap_content += '''    <image:image>
      <image:loc>https://mobixai.ir/static/images/articles-hero.jpg</image:loc>
      <image:title>مقالات مدل‌های هوش مصنوعی</image:title>
      <image:caption>اطلاعات جامع درباره مدل‌های هوش مصنوعی مختلف و کاربردهای آنها</image:caption>
    </image:image>
'''
        
        sitemap_content += '  </url>\n'
    
    # Close the sitemap
    sitemap_content += '</urlset>\n'
    
    return HttpResponse(sitemap_content.encode('utf-8'), content_type='application/xml')