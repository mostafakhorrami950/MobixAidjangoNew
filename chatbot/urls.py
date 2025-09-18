from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('session/<int:session_id>/', views.chat_session, name='chat_session'),
    path('sessions/', views.get_user_sessions, name='get_user_sessions'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    path('session/<int:session_id>/send/', views.send_message, name='send_message'),
    path('session/<int:session_id>/send-image/', views.send_image_message, name='send_image_message'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('generate-title/', views.generate_chat_title, name='generate_chat_title'),
    path('chatbot/<int:chatbot_id>/models/', views.get_available_models_for_chatbot, name='get_available_models_for_chatbot'),
]