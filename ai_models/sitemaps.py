from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import ModelArticle

class ArticlesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ModelArticle._default_manager.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse('model_article_detail', kwargs={'slug': item.slug})

class StaticPagesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return ['register', 'login', 'model_articles_list', 'terms_and_conditions']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return current date for static pages
        return timezone.now()