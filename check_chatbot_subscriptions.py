import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
import django
django.setup()

from chatbot.models import Chatbot

def check_chatbot_subscriptions():
    print('Chatbot subscription requirements:')
    chatbots = Chatbot.objects.all()
    for chatbot in chatbots:
        subscriptions = chatbot.subscription_types.all()
        subscription_names = [sub.name for sub in subscriptions]
        print(f'- {chatbot.name}: {subscription_names}')

if __name__ == "__main__":
    check_chatbot_subscriptions()