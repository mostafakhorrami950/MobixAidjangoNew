from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('session/<int:session_id>/', views.chat_session, name='chat_session'),
    path('sessions/', views.get_user_sessions, name='get_user_sessions'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/create-default/', views.create_default_session, name='create_default_session'),
    path('session/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    path('session/<int:session_id>/send/', views.send_message, name='send_message'),
    path('session/<int:session_id>/send_full/', views.send_message_and_get_full_response, name='send_message_full'),
    # Removed send-image endpoint as it's only used for image functionality
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('generate-title/', views.generate_chat_title, name='generate_chat_title'),
    path('chatbot/<int:chatbot_id>/models/', views.get_available_models_for_chatbot, name='get_available_models_for_chatbot'),
    path('session/<int:session_id>/update-title/', views.update_session_title, name='update_session_title'),
    path('session/<int:session_id>/web-search-access/', views.check_web_search_access, name='check_web_search_access'),
    path('web-search-access/', views.check_web_search_access_no_session, name='check_web_search_access_no_session'),
    path('session/<int:session_id>/image-generation-access/', views.check_image_generation_access, name='check_image_generation_access'),
    path('session/<int:session_id>/update-model/', views.update_session_model, name='update_session_model'),
    path('models/', views.get_available_models_for_user, name='get_available_models_for_user'),
    path('sidebar-menu-items/', views.get_sidebar_menu_items, name='get_sidebar_menu_items'),
    path('session/<int:session_id>/message/<uuid:message_id>/edit/', views.edit_message, name='edit_message'),
    path('api/global-settings/', views.get_global_settings, name='get_global_settings'),
]
