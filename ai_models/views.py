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

def static_sitemap(request):
    """
    Generate and serve the static pages sitemap dynamically
    """
    # Define static pages with their correct URL names and metadata
    static_pages = [
        {
            'name': 'home',
            'changefreq': 'daily',
            'priority': 1.0,
            'image': None
        },
        {
            'name': 'register',
            'changefreq': 'monthly',
            'priority': 0.9,
            'image': None  # Removed non-existent image
        },
        {
            'name': 'login',
            'changefreq': 'monthly',
            'priority': 0.9,
            'image': None  # Removed non-existent image
        },
        {
            'name': 'model_articles_list',
            'changefreq': 'weekly',
            'priority': 0.8,
            'image': None  # Removed non-existent image
        },
        {
            'name': 'terms_and_conditions',
            'changefreq': 'yearly',
            'priority': 0.5,
            'image': None
        },
        {
            'name': 'dashboard',
            'changefreq': 'daily',
            'priority': 0.8,
            'image': None
        },
        {
            'name': 'financial_transactions',
            'changefreq': 'weekly',
            'priority': 0.6,
            'image': None
        }
    ]
    
    # Start building the sitemap XML with proper formatting
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''
    
    # Add static pages to sitemap
    for page in static_pages:
        try:
            # Get the URL
            url = reverse(page['name'])
            full_url = f'https://mobixai.ir{url}'
            
            # Get lastmod (current date)
            lastmod = timezone.now().strftime('%Y-%m-%d')
            
            sitemap_content += f'''  <url>
    <loc>{escape(full_url)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
'''
            
            # Add image information if available
            if page['image']:
                sitemap_content += f'''    <image:image>
      <image:loc>{escape(page['image']['loc'])}</image:loc>
      <image:title>{escape(page['image']['title'])}</image:title>
      <image:caption>{escape(page['image']['caption'])}</image:caption>
    </image:image>
'''
            
            sitemap_content += '  </url>\n'
        except Exception as e:
            # Skip pages that can't be reversed
            continue
    
    # Close the sitemap
    sitemap_content += '</urlset>\n'
    
    return HttpResponse(sitemap_content.encode('utf-8'), content_type='application/xml')