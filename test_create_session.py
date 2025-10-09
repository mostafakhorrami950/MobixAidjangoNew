import requests
import json

# First, get available chatbots
chatbots_url = "http://127.0.0.1:8000/api/chatbot/chatbots/available/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Token d9ac178d27def178d82ca8ac9364920c8f3ce6d0"
}

try:
    response = requests.get(chatbots_url, headers=headers)
    print(f"Chatbots Status Code: {response.status_code}")
    chatbots = response.json()
    print(f"Available chatbots: {chatbots}")
    
    if chatbots and len(chatbots) > 0:
        # Create a chat session with the first chatbot
        session_url = "http://127.0.0.1:8000/api/chatbot/sessions/"
        session_data = {
            "chatbot": chatbots[0]['id'],
            "title": "Test Session"
        }
        
        session_response = requests.post(session_url, headers=headers, data=json.dumps(session_data))
        print(f"Session Creation Status Code: {session_response.status_code}")
        print(f"Session Creation Response: {session_response.text}")
        
        # Now get the sessions
        sessions_response = requests.get(session_url, headers=headers)
        print(f"Sessions Status Code: {sessions_response.status_code}")
        print(f"Sessions Response: {sessions_response.text}")
        
except Exception as e:
    print(f"Error: {e}")