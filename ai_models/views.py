from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import markdown
from .models import AIModel, ModelArticle

def model_article_detail(request, slug):
    """
    Display a detailed article about an AI model
    """
    article = get_object_or_404(
        ModelArticle.objects.select_related('ai_model'), 
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
    related_articles = ModelArticle.objects.filter(
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
    articles = ModelArticle.objects.filter(
        is_published=True
    ).select_related('ai_model').order_by('-created_at')
    
    context = {
        'articles': articles,
    }
    
    return render(request, 'ai_models/articles_list.html', context)