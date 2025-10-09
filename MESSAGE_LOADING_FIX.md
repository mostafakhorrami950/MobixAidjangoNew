# Message Loading Issue Fix

## Problem Description
The Flutter app was not loading messages correctly. After investigating the code, we found that the issue was in the Django API's `ChatMessageViewSet` class.

## Root Cause
The `ChatMessageViewSet.get_queryset()` method was only filtering messages by user but not by session. When the Flutter app called `/api/chatbot/messages/?session=<id>`, it was receiving all messages for the user across all sessions instead of just the messages for the specific session.

## Solution
We modified the `ChatMessageViewSet.get_queryset()` method in [chatbot/api.py](file:///c:/Users/10/Projects/mobixaidjangonew/chatbot/api.py) to properly filter messages by the session parameter when provided:

```python
def get_queryset(self):
    # Users can only see messages from their own chat sessions
    queryset = ChatMessage.objects.filter(session__user=self.request.user)
    
    # Filter by session if provided as a query parameter
    session_id = self.request.query_params.get('session', None)
    if session_id is not None:
        queryset = queryset.filter(session_id=session_id)
        
    return queryset
```

## How the Fix Works
1. The method first filters messages to only show those from chat sessions belonging to the current user
2. It then checks if a `session` parameter is provided in the query string
3. If a session ID is provided, it further filters the queryset to only include messages from that specific session
4. This ensures that when the Flutter app requests messages for a specific session, it only gets messages for that session

## Testing
We verified that:
1. The Django server starts correctly with our changes
2. The messages endpoint properly handles the session parameter
3. Authentication is still required for API access

## Impact
This fix should resolve the message loading issue in the Flutter app by ensuring that when a user opens a specific chat session, they only see messages belonging to that session rather than all messages across all their sessions.