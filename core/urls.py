from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('financial-transactions/', views.financial_transactions, name='financial_transactions'),
]