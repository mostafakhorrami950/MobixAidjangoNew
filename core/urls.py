from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('financial-transactions/', views.financial_transactions, name='financial_transactions'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('sidebar-menu-items/', views.get_sidebar_menu_items, name='get_sidebar_menu_items'),
    path('random-advertising-banner/', views.get_random_advertising_banner, name='get_random_advertising_banner'),
]
