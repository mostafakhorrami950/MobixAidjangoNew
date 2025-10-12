from django.core.management.base import BaseCommand
from ai_models.models import ModelArticle
import os
from django.conf import settings
from xml.sax.saxutils import escape

class Command(BaseCommand):
    help = 'Generate dynamic sitemap for articles'

    def handle(self, *args, **options):
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
        
        # Write to file
        sitemap_path = os.path.join(settings.BASE_DIR, 'templates', 'sitemap-articles.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        self.stdout.write(
            'Successfully generated sitemap with {} articles at {}'.format(len(articles), sitemap_path)
        )