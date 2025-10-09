from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.utils import timezone
from accounts.models import User
from subscriptions.services import UsageService
from .serializers import (
    UserSerializer, 
    SubscriptionTypeSerializer, 
    UserSubscriptionSerializer,
    AIModelSerializer,
    ChatbotSerializer,
    ChatMessageSerializer,
    ChatSessionSerializer,
    ChatSessionUsageSerializer
)
import logging
import uuid

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user information
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def subscription(self, request):
        """Get user's subscription information"""
        try:
            user_subscription = request.user.get_subscription_info()
            if user_subscription:
                serializer = UserSubscriptionSerializer(user_subscription)
                return Response(serializer.data)
            return Response({'detail': 'No active subscription found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for chatbots
    """
    serializer_class = ChatbotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        user_subscription = self.request.user.get_subscription_type()
        if user_subscription:
            # Get chatbots available for user's subscription
            return Chatbot.objects.filter(
                is_active=True
            ).filter(
                subscription_types=user_subscription
            ) | Chatbot.objects.filter(
                is_active=True,
                subscription_types=None
            )
        else:
            # If no subscription, only show chatbots with no subscription requirement
            return Chatbot.objects.filter(
                is_active=True,
                subscription_types=None
            )


class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for AI models
    """
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        AIModel = apps.get_model('ai_models', 'AIModel')
        user_subscription = self.request.user.get_subscription_type()
        
        if user_subscription:
            # Get models available for user's subscription
            return AIModel.objects.filter(
                is_active=True
            ).filter(
                subscriptions__subscription_types=user_subscription
            ) | AIModel.objects.filter(
                is_active=True,
                is_free=True
            )
        else:
            # If no subscription, only show free models
            return AIModel.objects.filter(
                is_active=True,
                is_free=True
            )


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat sessions
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def create(self, request):
        """Create a new chat session"""
        try:
            Chatbot = apps.get_model('chatbot', 'Chatbot')
            AIModel = apps.get_model('ai_models', 'AIModel')
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            # Get data from request
            chatbot_id = request.data.get('chatbot_id')
            ai_model_id = request.data.get('ai_model_id')
            title = request.data.get('title', 'چت جدید')
            
            if not chatbot_id:
                return Response({'error': 'انتخاب چت‌بات الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the chatbot
            chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
            
            # Check if user has access to this chatbot
            if chatbot.subscription_types.exists():
                user_subscription = request.user.get_subscription_type()
                if not user_subscription or not chatbot.subscription_types.filter(id=user_subscription.id).exists():
                    return Response({'error': 'شما دسترسی لازم برای این چت‌بات را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
            # Check if AI model is provided
            if not ai_model_id:
                return Response({'error': 'انتخاب مدل هوش مصنوعی الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has access to the selected model
            try:
                selected_model = AIModel.objects.get(model_id=ai_model_id, is_active=True)
                if not request.user.has_access_to_model(selected_model):
                    return Response({'error': 'شما دسترسی لازم برای این مدل را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            except AIModel.DoesNotExist:
                return Response({'error': 'مدل انتخابی وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create new chat session
            session = ChatSession.objects.create(
                user=request.user,
                chatbot=chatbot,
                ai_model=selected_model,
                title=title
            )
            
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'خطا در ایجاد جلسه: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific session"""
        ChatMessage = apps.get_model('chatbot', 'ChatMessage')
        session = self.get_object()
        messages = session.messages.filter(disabled=False).all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({'messages': serializer.data})
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a chat session"""
        ChatMessage = apps.get_model('chatbot', 'ChatMessage')
        session = self.get_object()
        
        try:
            # Check user access to AI model
            if not request.user.has_access_to_model(session.ai_model):
                return Response({'error': 'شما دسترسی لازم برای این مدل را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
            user_message_content = request.data.get('message', '')
            
            if not user_message_content:
                return Response({'error': 'محتوای پیام الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check usage limits
            subscription_type = request.user.get_subscription_type()
            
            if subscription_type:
                # Perform comprehensive usage limit checking
                within_limit, message = UsageService.comprehensive_check(
                    request.user, session.ai_model, subscription_type
                )
                if not within_limit:
                    return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
            
            # Calculate tokens for user message
            user_message_tokens = UsageService.calculate_tokens_for_message(user_message_content)
            
            # Create user message
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message_content,
                tokens_count=user_message_tokens
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            # Return user message
            serializer = ChatMessageSerializer(user_message)
            return Response({'user_message': serializer.data}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        """Delete a chat session"""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def update_title(self, request, pk=None):
        """Update session title"""
        session = self.get_object()
        new_title = request.data.get('title', 'چت جدید')
        session.title = new_title
        session.save()
        return Response({'success': True, 'title': new_title})
    
    @action(detail=True, methods=['post'], url_path='messages/(?P<message_id>[^/.]+)/edit')
    def edit_message(self, request, pk=None, message_id=None):
        """Edit a user message and regenerate subsequent assistant messages"""
        try:
            ChatMessage = apps.get_model('chatbot', 'ChatMessage')
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            
            # Get the session and verify ownership
            session = self.get_object()
            
            # Get the message to edit
            message = get_object_or_404(ChatMessage, message_id=message_id, session=session, message_type='user')
            
            # Parse the new content
            new_content = request.data.get('content', '').strip()
            
            if not new_content:
                return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check usage limits before proceeding
            subscription_type = request.user.get_subscription_type()
            ai_model = session.ai_model
            
            if ai_model and subscription_type:
                # Perform comprehensive usage limit checking
                within_limit, message_limit = UsageService.comprehensive_check(
                    request.user, ai_model, subscription_type
                )
                if not within_limit:
                    return Response({'error': message_limit}, status=status.HTTP_403_FORBIDDEN)
            
            # Update the message content
            message.content = new_content
            message.edited_at = timezone.now()
            message.save()
            
            # Mark all subsequent messages (both user and assistant) as disabled
            subsequent_messages = session.messages.filter(
                created_at__gt=message.created_at
            ).order_by('created_at')
            
            disabled_message_ids = []
            for msg in subsequent_messages:
                msg.disabled = True
                msg.save()
                disabled_message_ids.append(str(msg.message_id))
            
            return Response({
                'success': True,
                'disabled_message_ids': disabled_message_ids
            })
            
        except Exception as e:
            logger.error(f"Error editing message: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatSessionUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for chat session usage
    """
    serializer_class = ChatSessionUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
        return ChatSessionUsage.objects.filter(user=self.request.user)