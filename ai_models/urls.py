from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.model_articles_list, name='model_articles_list'),
    path('articles/<slug:slug>/', views.model_article_detail, name='model_article_detail'),
]