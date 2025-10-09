from rest_framework import serializers
from accounts.models import User
from chatbot.models import ChatSession, ChatMessage, Chatbot, AIModel, ChatSessionUsage
from subscriptions.models import SubscriptionType, UserSubscription
from ai_models.models import AIModel as AIModelOriginal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'is_verified', 'date_joined']


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'


class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_type = SubscriptionTypeSerializer(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = ['id', 'subscription_type', 'is_active', 'start_date', 'end_date']


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelOriginal
        fields = ['id', 'name', 'model_id', 'description', 'model_type', 'is_active', 'is_free', 'token_cost_multiplier']


class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbot
        fields = ['id', 'name', 'description', 'image', 'is_active', 'system_prompt', 'chatbot_type']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message_id', 'message_type', 'content', 'tokens_count', 'image_url', 'created_at', 'edited_at', 'disabled']


class ChatSessionSerializer(serializers.ModelSerializer):
    chatbot = ChatbotSerializer(read_only=True)
    ai_model = AIModelSerializer(read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'chatbot', 'ai_model', 'title', 'auto_generate_title', 'created_at', 'updated_at', 'is_active']


class ChatSessionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSessionUsage
        fields = ['id', 'tokens_count', 'free_model_tokens_count', 'is_free_model', 'created_at', 'updated_at']