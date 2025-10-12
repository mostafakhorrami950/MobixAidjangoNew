from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone
from ai_models.models import ModelArticle
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate dynamic sitemap for articles'

    def handle(self, *args, **options):
        # Get all published articles
        articles = ModelArticle.objects.filter(is_published=True).order_by('-updated_at')
        
        # Start building the sitemap XML
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''
        
        # Add articles to sitemap
        for article in articles:
            # Format last modified date
            lastmod = article.updated_at.strftime('%Y-%m-%d')
            
            # Build the URL
            url = reverse('model_article_detail', kwargs={'slug': article.slug})
            full_url = f'https://mobixai.ir{url}'
            
            sitemap_content += f'''  <url>
    <loc>{full_url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
'''
            
            # Add image information if available
            if article.image:
                image_url = f'https://mobixai.ir{article.image.url}'
                sitemap_content += f'''    <image:image>
      <image:loc>{image_url}</image:loc>
      <image:title>{article.title}</image:title>
      <image:caption>{article.excerpt or article.title}</image:caption>
    </image:image>
'''
            
            sitemap_content += '  </url>\n'
        
        # Close the sitemap
        sitemap_content += '</urlset>'
        
        # Write to file
        sitemap_path = os.path.join(settings.BASE_DIR, 'templates', 'sitemap-articles.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sitemap with {len(articles)} articles at {sitemap_path}'
            )
        )