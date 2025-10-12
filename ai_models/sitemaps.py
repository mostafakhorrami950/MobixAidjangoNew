from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import ModelArticle

class ArticlesSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return ModelArticle._default_manager.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse('model_article_detail', kwargs={'slug': item.slug})
        
    def changefreq(self, obj):
        return 'weekly'
        
    def priority(self, obj):
        return 0.8

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