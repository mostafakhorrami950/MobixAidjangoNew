from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ChatbotViewSet,
    AIModelViewSet,
    ChatSessionViewSet,
    ChatSessionUsageViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'chatbots', ChatbotViewSet, basename='chatbot')
router.register(r'ai-models', AIModelViewSet, basename='ai-model')
router.register(r'chat-sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'chat-session-usages', ChatSessionUsageViewSet, basename='chat-session-usage')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]