from django.urls import path
from . import views

urlpatterns = [
    path('purchase/', views.purchase_subscription, name='purchase_subscription'),
    path('comparison/', views.public_subscription_comparison, name='public_subscription_comparison'),
    path('apply-discount/', views.apply_discount_code, name='apply_discount_code'),
    path('payment/<int:subscription_id>/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('calculate-remaining-value/', views.calculate_remaining_subscription_value, name='calculate_remaining_value'),
    path('test-calculation/', views.test_subscription_calculation, name='test_subscription_calculation'),
    path('intelligent-upgrade/<int:new_subscription_id>/', views.intelligent_subscription_upgrade, name='intelligent_subscription_upgrade'),
    path('complete-upgrade/', views.complete_intelligent_upgrade, name='complete_intelligent_upgrade'),
    path('costs/', views.user_openrouter_costs, name='user_openrouter_costs'),
]