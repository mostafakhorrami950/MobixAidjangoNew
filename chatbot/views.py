from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import Chatbot, ChatSession, ChatMessage, GeneratedImage, WebSearch, PDFDocument
from ai_models.models import AIModel
from ai_models.services import OpenRouterService
from subscriptions.models import UserSubscription
from subscriptions.services import UsageService
import json

@login_required
def chat(request):
    # Get all available chatbots for the user
    user_subscription = request.user.get_subscription_type()
    
    if user_subscription:
        # Get chatbots available for user's subscription
        available_chatbots = Chatbot.objects.filter(
            Q(is_active=True) & 
            (Q(subscription_types=user_subscription) | Q(subscription_types=None))
        ).distinct()
    else:
        # If no subscription, only show chatbots with no subscription requirement
        available_chatbots = Chatbot.objects.filter(
            is_active=True,
            subscription_types=None
        )
    
    # Also get available AI models for backward compatibility
    available_models = []
    if user_subscription:
        # Get models available for user's subscription
        models = AIModel.objects.filter(
            is_active=True,
            subscriptions__subscription_types=user_subscription
        ).distinct()
        available_models.extend(models)
    
    # Add free models (available to all users)
    free_models = AIModel.objects.filter(is_active=True, is_free=True)
    available_models.extend(free_models)
    
    # Remove duplicates
    available_models = list(set(available_models))
    
    # Get user's chat sessions
    chat_sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    
    context = {
        'available_chatbots': available_chatbots,
        'available_models': available_models,
        'chat_sessions': chat_sessions,
    }
    return render(request, 'chatbot/chat.html', context)

@login_required
def get_available_models_for_chatbot(request, chatbot_id):
    """
    Get available AI models for a specific chatbot based on its type
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
        user_subscription = request.user.get_subscription_type()
        
        # Filter models based on chatbot type
        if chatbot.chatbot_type == 'image':
            # For image chatbots, only show image generation models
            models_query = AIModel.objects.filter(
                is_active=True,
                model_type='image'
            )
        else:
            # For text chatbots, only show text generation models
            models_query = AIModel.objects.filter(
                is_active=True,
                model_type='text'
            )
        
        # Apply subscription filtering
        if user_subscription:
            # Get models available for user's subscription
            models = models_query.filter(
                Q(is_free=True) | Q(subscriptions__subscription_types=user_subscription)
            ).distinct()
        else:
            # If no subscription, only show free models
            models = models_query.filter(is_free=True).distinct()
        
        # Format models for JSON response
        model_list = []
        for model in models:
            model_list.append({
                'model_id': model.model_id,
                'name': model.name,
                'is_free': model.is_free,
                'model_type': model.model_type
            })
        
        return JsonResponse({
            'models': model_list,
            'chatbot_type': chatbot.chatbot_type
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def create_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Check if creating with chatbot
        if 'chatbot_id' in data:
            chatbot_id = data.get('chatbot_id')
            title = data.get('title', 'چت جدید')
            
            # Get the chatbot
            chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
            
            # Check if user has access to this chatbot
            if chatbot.subscription_types.exists():
                user_subscription = request.user.get_subscription_type()
                if not user_subscription or not chatbot.subscription_types.filter(id=user_subscription.id).exists():
                    return JsonResponse({'error': 'شما دسترسی لازم به این چت‌بات را ندارید'}, status=403)
            
            # Check if AI model is provided
            ai_model_id = data.get('ai_model_id')
            if not ai_model_id:
                return JsonResponse({'error': 'انتخاب مدل هوش مصنوعی الزامی است'}, status=400)
            
            # Check if user has access to the selected model
            try:
                selected_model = AIModel.objects.get(model_id=ai_model_id, is_active=True)
                if not request.user.has_access_to_model(selected_model):
                    return JsonResponse({'error': 'شما دسترسی لازم به مدل انتخابی را ندارید'}, status=403)
            except AIModel.DoesNotExist:
                return JsonResponse({'error': 'مدل انتخابی وجود ندارد'}, status=400)
            
            # Create new chat session with chatbot only
            # Store the selected AI model in the session's ai_model field for backward compatibility
            session = ChatSession.objects.create(
                user=request.user,
                chatbot=chatbot,
                ai_model=selected_model,  # This is kept for backward compatibility
                title=title
            )
            
            return JsonResponse({
                'session_id': session.id,
                'title': session.title,
                'chatbot_name': chatbot.name,
                'chatbot_type': chatbot.chatbot_type
            })
        else:
            return JsonResponse({'error': 'انتخاب چت‌بات الزامی است'}, status=400)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def get_session_messages(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    messages = session.messages.all()
    message_list = []
    for message in messages:
        message_list.append({
            'id': message.id,
            'type': message.message_type,
            'content': message.content,
            'image_url': message.image_url,
            'created_at': message.created_at.isoformat()
        })
    
    # Determine session type and name
    if session.chatbot:
        session_name = session.chatbot.name
        chatbot_type = session.chatbot.chatbot_type
    elif session.ai_model:
        session_name = session.ai_model.name
        chatbot_type = 'text'  # Default to text for direct AI model sessions
    else:
        session_name = "Unknown"
        chatbot_type = 'text'
    
    # Get AI model ID for web search support check
    ai_model_id = None
    if session.ai_model:
        ai_model_id = session.ai_model.model_id
    
    return JsonResponse({
        'messages': message_list,
        'session_title': session.title,
        'session_name': session_name,
        'chatbot_type': chatbot_type,
        'ai_model_id': ai_model_id
    })

@login_required
def send_message(request, session_id):
    if request.method == 'POST':
        try:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            # Ensure UTF-8 decoding for Persian text
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            user_message_content = data.get('message')
            
            # Check for web search request
            web_search = data.get('web_search', False)
            
            # Check for PDF file
            pdf_file = request.FILES.get('pdf_file')
            pdf_url = data.get('pdf_url')
            
            if not user_message_content and not web_search and not pdf_file and not pdf_url:
                return JsonResponse({'error': 'محتوای پیام الزامی است'}, status=400)
            
            # Check usage limits
            subscription_type = request.user.get_subscription_type()
            
            # Determine if this is a free model
            is_free_model = False
            ai_model = None
            
            # Get the AI model from either:
            # 1. The session's ai_model field (for backward compatibility)
            # 2. Future implementation might use chatbot's default model or user selection
            if session.ai_model:
                ai_model = session.ai_model
                is_free_model = ai_model.is_free if ai_model else False
            else:
                return JsonResponse({'error': 'هیچ مدل هوش مصنوعی با این جلسه مرتبط نیست'}, status=500)
            
            # Check web search limits if requested
            if web_search and subscription_type:
                # Check if the current model supports web search
                if not (":online" in ai_model.model_id or ai_model.model_id.startswith("openrouter/auto")):
                    return JsonResponse({'error': 'مدل انتخاب‌شده قابلیت جستجوی وب ندارد'}, status=400)
                
                within_limit, message = UsageService.check_web_search_limit(
                    request.user, subscription_type
                )
                
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)
            
            # Check PDF processing limits if provided
            pdf_content = None
            if (pdf_file or pdf_url) and subscription_type:
                # Get file size for limit checking
                pdf_file_size_mb = 0
                if pdf_file:
                    pdf_file_size_mb = pdf_file.size / (1024 * 1024)  # Convert bytes to MB
                elif pdf_url:
                    # For URL, we can't easily get file size without downloading it
                    # We'll assume a reasonable size for now
                    pdf_file_size_mb = 5  # Default assumption
                
                within_limit, message = UsageService.check_pdf_processing_limit(
                    request.user, subscription_type, pdf_file_size_mb
                )
                
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)
                
                # Process PDF content
                pdf_content = {
                    "engine": data.get('pdf_engine', 'pdf-text')  # Default to pdf-text engine
                }
                
                # If file is uploaded, encode it to base64
                if pdf_file:
                    # Save PDF document to server
                    pdf_document = PDFDocument(
                        session=session,
                        user=request.user,
                        file_name=pdf_file.name,
                        file_size=pdf_file.size,
                        processing_engine=pdf_content["engine"]
                    )
                    pdf_document.pdf_file.save(pdf_file.name, pdf_file, save=True)
                    
                    # Encode PDF to base64 for sending to AI
                    pdf_base64 = OpenRouterService().encode_pdf_to_base64(pdf_document.pdf_file.path)
                    pdf_content["data"] = f"data:application/pdf;base64,{pdf_base64}"
                elif pdf_url:
                    # Use the URL directly
                    pdf_content["url"] = pdf_url
            
            # Get conversation history for context and token calculation
            conversation_messages = session.messages.all().order_by('created_at')
            
            if subscription_type:
                # Calculate input tokens for LIMIT CHECKING:
                # 1. User message
                input_tokens = UsageService.calculate_tokens_for_message(user_message_content or "")
                
                # 2. Add tokens for system prompt if exists (for chatbots)
                if session.chatbot and session.chatbot.system_prompt:
                    input_tokens += UsageService.calculate_tokens_for_message(session.chatbot.system_prompt)
                
                # 3. Add tokens for conversation history (previous messages)
                input_tokens += UsageService.calculate_tokens_for_messages(conversation_messages)
                
                # For limit checking, we check against the input tokens
                # (we don't know the output tokens yet since the AI hasn't responded)
                within_limit, message = UsageService.check_usage_limit(
                    request.user, subscription_type, input_tokens, is_free_model
                )
                
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)
            
            # Save user message
            # For user messages, we'll use character counting as a fallback since we don't get prompt tokens for individual messages
            user_message_tokens = UsageService.calculate_tokens_for_message(user_message_content or "")
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message_content or ("Web Search Request" if web_search else "PDF Processing Request"),
                tokens_count=user_message_tokens
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            # Get conversation history for context
            messages = session.messages.all().order_by('created_at')
            openrouter_messages = []
            
            # Add system prompt if exists (for chatbots)
            if session.chatbot and session.chatbot.system_prompt:
                openrouter_messages.append({
                    'role': 'system',
                    'content': session.chatbot.system_prompt
                })
            
            # Preserve complete chat history context
            for msg in messages:
                openrouter_messages.append({
                    'role': msg.message_type,
                    'content': msg.content
                })
            
            # Add the current user message
            current_message = {
                'role': 'user',
                'content': user_message_content or ""
            }
            
            # Add web search or PDF content to the message if needed
            if web_search:
                current_message['content'] += " (با استفاده از جستجوی وب)"
            elif pdf_content:
                current_message['content'] += " (با پردازش فایل PDF)"
            
            openrouter_messages.append(current_message)
            
            # Send to OpenRouter API with streaming
            openrouter_service = OpenRouterService()
            
            if ai_model.model_type == 'image':
                # Image generation model
                # Show "generating image" message to user
                generating_message = ChatMessage.objects.create(
                    session=session,
                    message_type='assistant',
                    content='در حال تولید تصویر، لطفاً منتظر بمانید...',
                    tokens_count=0
                )
                
                response = openrouter_service.send_image_generation_request_with_context(
                    ai_model, openrouter_messages
                )
                
                # Update the generating message with the actual response
                if 'error' in response:
                    generating_message.content = f"خطا در تولید تصویر: {response['error']}"
                    generating_message.save()
                    return JsonResponse({'error': response['error']}, status=500)
                
                # Process response and save assistant message
                if isinstance(response, dict) and 'choices' in response:
                    assistant_content = response['choices'][0]['message']['content']
                    
                    # Get actual token counts from OpenRouter API
                    prompt_tokens = response.get('usage', {}).get('prompt_tokens', 0)
                    completion_tokens = response.get('usage', {}).get('completion_tokens', 0)
                    total_tokens = response.get('usage', {}).get('total_tokens', prompt_tokens + completion_tokens)
                    
                    # Use the actual token count from API
                    assistant_tokens = total_tokens
                    
                    # Check if there are images in the response
                    image_url = ""
                    if 'images' in response['choices'][0]['message']:
                        images = response['choices'][0]['message']['images']
                        if images:
                            image_url = images[0]['image_url']['url']
                    
                    # Update the generating message with the actual response
                    generating_message.content = assistant_content
                    generating_message.image_url = image_url
                    generating_message.tokens_count = assistant_tokens
                    generating_message.save()
                    
                    # Increment usage counters with actual token counts from API
                    if subscription_type:
                        # For image generation, we use the total tokens from the API response
                        UsageService.increment_usage(
                            request.user, subscription_type, 
                            messages_count=2,  # User message + assistant message
                            tokens_count=total_tokens,
                            is_free_model=is_free_model
                        )
                        
                        # Create or update ChatSessionUsage record for this session
                        from .models import ChatSessionUsage
                        chat_session_usage, created = ChatSessionUsage.objects.get_or_create(
                            session=session,
                            user=request.user,
                            subscription_type=subscription_type,
                            defaults={
                                'tokens_count': total_tokens,
                                'free_model_tokens_count': total_tokens if is_free_model else 0,
                                'is_free_model': is_free_model
                            }
                        )
                        if not created:
                            # Update existing record
                            if is_free_model:
                                chat_session_usage.free_model_tokens_count += total_tokens
                            else:
                                chat_session_usage.tokens_count += total_tokens
                            chat_session_usage.save()
                    
                    # Ensure UTF-8 encoding for the response
                    response_data = {
                        'message_id': generating_message.id,
                        'content': assistant_content,
                        'image_url': image_url,
                        'tokens_count': assistant_tokens
                    }
                    response_json = json.dumps(response_data, ensure_ascii=False)
                    return JsonResponse(json.loads(response_json), safe=False, json_dumps_params={'ensure_ascii': False})
                else:
                    generating_message.content = "پاسخ نامعتبر از مدل هوش مصنوعی"
                    generating_message.save()
                    return JsonResponse({'error': 'Invalid response from AI model'}, status=500)
            else:
                # Text generation model with streaming
                response = openrouter_service.stream_text_response(
                    ai_model, openrouter_messages, web_search=web_search, pdf_content=pdf_content
                )
                
                if isinstance(response, dict) and 'error' in response:
                    return JsonResponse({'error': response['error']}, status=500)
                
                # For streaming, we'll return a streaming response
                def generate():
                    full_response = ""
                    usage_data = None
                    try:
                        for chunk in response:
                            # Check if this chunk contains usage data
                            if '[USAGE_DATA]' in chunk and '[USAGE_DATA_END]' in chunk:
                                # Extract usage data
                                start_idx = chunk.find('[USAGE_DATA]') + 12
                                end_idx = chunk.find('[USAGE_DATA_END]')
                                usage_json = chunk[start_idx:end_idx]
                                try:
                                    usage_data = json.loads(usage_json)
                                except json.JSONDecodeError:
                                    pass
                                continue
                            full_response += chunk
                            # Ensure proper UTF-8 encoding for Persian text
                            yield chunk.encode('utf-8')
                    except Exception as e:
                        yield f"Error in streaming: {str(e)}".encode('utf-8')
                    
                    # Save the complete assistant message
                    # Use actual token count from API if available, otherwise fallback to character count
                    if usage_data:
                        prompt_tokens = usage_data.get('prompt_tokens', 0)
                        completion_tokens = usage_data.get('completion_tokens', 0)
                        total_tokens = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                        assistant_tokens = total_tokens
                    else:
                        # Fallback to character counting if API doesn't provide usage data
                        assistant_tokens = UsageService.calculate_tokens_for_message(full_response)
                    
                    assistant_message = ChatMessage.objects.create(
                        session=session,
                        message_type='assistant',
                        content=full_response,
                        tokens_count=assistant_tokens
                    )
                    
                    # Increment usage counters
                    if subscription_type:
                        # For text generation, we calculate the total tokens used
                        total_tokens_used = 0
                        if usage_data:
                            # Use actual token counts from API
                            prompt_tokens = usage_data.get('prompt_tokens', 0)
                            completion_tokens = usage_data.get('completion_tokens', 0)
                            total_tokens = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                            total_tokens_used = total_tokens
                            
                            UsageService.increment_usage(
                                request.user, subscription_type, 
                                messages_count=2,  # User message + assistant message
                                tokens_count=total_tokens,
                                is_free_model=is_free_model
                            )
                        else:
                            # Fallback to our calculation if API doesn't provide usage data
                            # Calculate total tokens for usage tracking:
                            # Input tokens: user message + system prompt + conversation history
                            input_tokens = user_message_tokens
                            if session.chatbot and session.chatbot.system_prompt:
                                input_tokens += UsageService.calculate_tokens_for_message(session.chatbot.system_prompt)
                            input_tokens += UsageService.calculate_tokens_for_messages(conversation_messages)
                            
                            # Output tokens: assistant response
                            output_tokens = assistant_tokens
                            
                            # Total tokens = input + output
                            total_tokens = input_tokens + output_tokens
                            total_tokens_used = total_tokens
                            
                            UsageService.increment_usage(
                                request.user, subscription_type, 
                                messages_count=2,  # User message + assistant message
                                tokens_count=total_tokens,
                                is_free_model=is_free_model
                            )
                        
                        # Create or update ChatSessionUsage record for this session
                        from .models import ChatSessionUsage
                        chat_session_usage, created = ChatSessionUsage.objects.get_or_create(
                            session=session,
                            user=request.user,
                            subscription_type=subscription_type,
                            defaults={
                                'tokens_count': total_tokens_used,
                                'free_model_tokens_count': total_tokens_used if is_free_model else 0,
                                'is_free_model': is_free_model
                            }
                        )
                        if not created:
                            # Update existing record
                            if is_free_model:
                                chat_session_usage.free_model_tokens_count += total_tokens_used
                            else:
                                chat_session_usage.tokens_count += total_tokens_used
                            chat_session_usage.save()
                        
                        # Increment web search usage if applicable
                        if web_search:
                            UsageService.increment_web_search_usage(request.user, subscription_type)
                        
                        # Increment PDF processing usage if applicable
                        if pdf_content:
                            UsageService.increment_pdf_processing_usage(request.user, subscription_type)
                
                # Return streaming response with proper encoding
                return StreamingHttpResponse(
                    generate(), 
                    content_type='text/plain; charset=utf-8'
                )
                
        except Exception as e:
            # Log the actual error for debugging
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error in send_message: {str(e)}", exc_info=True)
            error_details = {
                'error': 'Internal server error',
                'details': str(e),
                'type': type(e).__name__
            }
            # Ensure UTF-8 encoding for error response
            response_json = json.dumps(error_details, ensure_ascii=False)
            return JsonResponse(json.loads(response_json), status=500, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_user_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    session_list = []
    for session in sessions:
        # Determine session type and access level
        if session.chatbot:
            session_name = session.chatbot.name
            # Check if chatbot requires premium access
            requires_premium = session.chatbot.subscription_types.exists()
            model_access = "Premium" if requires_premium else "Free"
        elif session.ai_model:
            session_name = session.ai_model.name
            model_access = "Free" if session.ai_model.is_free else "Premium"
        else:
            session_name = "Unknown"
            model_access = "Unknown"
        
        session_list.append({
            'id': session.id,
            'title': session.title,
            'session_name': session_name,
            'model_access': model_access,
            'updated_at': session.updated_at.isoformat(),
            'message_count': session.messages.count()
        })
    
    return JsonResponse({'sessions': session_list})

@login_required
def generate_chat_title(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_message = data.get('first_message')
        
        # Check if generating title for chatbot or AI model
        if 'chatbot_id' in data:
            chatbot_id = data.get('chatbot_id')
            # Get the chatbot
            chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
            ai_model = chatbot.ai_model
        elif 'model_id' in data:
            model_id = data.get('model_id')
            # Get the AI model
            ai_model = get_object_or_404(AIModel, model_id=model_id, is_active=True)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        # Create a prompt for generating a chat title
        prompt = f"Create a short, descriptive title (maximum 5 words) for a chat about: {first_message}"
        
        # Send to OpenRouter API to generate title
        openrouter_service = OpenRouterService()
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = openrouter_service.send_text_message(ai_model, messages)
        
        if 'error' in response:
            # Return a default title if AI fails
            return JsonResponse({'title': 'چت جدید'})
        
        if isinstance(response, dict) and 'choices' in response:
            title = response['choices'][0]['message']['content'].strip()
            # Limit title to 50 characters
            title = title[:50]
            return JsonResponse({'title': title})
        else:
            # Return a default title if AI fails
            return JsonResponse({'title': 'چت جدید'})
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def delete_session(request, session_id):
    if request.method == 'DELETE':
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.is_active = False
        session.save()
        return JsonResponse({'success': True})
    
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def chat_session(request, session_id):
    """Dedicated view for a specific chat session"""
    # Verify the session exists and belongs to the user
    session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
    
    # Get all available chatbots for the user
    user_subscription = request.user.get_subscription_type()
    
    if user_subscription:
        # Get chatbots available for user's subscription
        available_chatbots = Chatbot.objects.filter(
            Q(is_active=True) & 
            (Q(subscription_types=user_subscription) | Q(subscription_types=None))
        ).distinct()
    else:
        # If no subscription, only show chatbots with no subscription requirement
        available_chatbots = Chatbot.objects.filter(
            is_active=True,
            subscription_types=None
        )
    
    # Also get available AI models for backward compatibility
    available_models = []
    if user_subscription:
        # Get models available for user's subscription
        models = AIModel.objects.filter(
            is_active=True,
            subscriptions__subscription_types=user_subscription
        ).distinct()
        available_models.extend(models)
    
    # Add free models (available to all users)
    free_models = AIModel.objects.filter(is_active=True, is_free=True)
    available_models.extend(free_models)
    
    # Remove duplicates
    available_models = list(set(available_models))
    
    # Get user's chat sessions
    chat_sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    
    context = {
        'available_chatbots': available_chatbots,
        'available_models': available_models,
        'chat_sessions': chat_sessions,
    }
    return render(request, 'chatbot/chat.html', context)

@login_required
def send_image_message(request, session_id):
    """
    Handle image uploads for image generation chatbots
    """
    if request.method == 'POST':
        try:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            
            # Check if this is an image generation chatbot
            if not session.chatbot or session.chatbot.chatbot_type != 'image':
                return JsonResponse({'error': 'این چت‌بات از ارسال تصویر پشتیبانی نمی‌کند'}, status=400)
            
            # Get the AI model for this session
            ai_model = session.ai_model
            if not ai_model or ai_model.model_type != 'image':
                return JsonResponse({'error': 'مدل انتخابی از تولید تصویر پشتیبانی نمی‌کند'}, status=400)
            
            # Get the prompt and image from the request
            prompt = request.POST.get('prompt', '').strip()
            image_file = request.FILES.get('image')
            modify_image_url = request.POST.get('modify_image_url', '').strip()
            
            # Check if this is a modification request (based on prompt content)
            is_modification_request = False
            if prompt and ('اصلاح' in prompt or 'تغییر' in prompt or 'ویرایش' in prompt or 'modify' in prompt.lower() or 'edit' in prompt.lower()):
                is_modification_request = True
            
            # If this is a modification request, check for previous image
            if is_modification_request and not image_file and not modify_image_url:
                # Get the last generated image from the database
                last_generated_image = GeneratedImage.objects.filter(
                    session=session,
                    user=request.user,
                    is_active=True
                ).order_by('-created_at').first()
                
                if last_generated_image:
                    # Use the last generated image for modification
                    modify_image_url = request.build_absolute_uri(last_generated_image.image.url)
                else:
                    # No previous image found
                    return JsonResponse({'error': 'تصویر قبلی برای ویرایش یافت نشد'}, status=400)
            
            # Validate input
            if not prompt and not image_file and not modify_image_url:
                return JsonResponse({'error': 'متن یا تصویر برای تحلیل الزامی است'}, status=400)
            
            # Check usage limits for image generation
            subscription_type = request.user.get_subscription_type()
            is_free_model = ai_model.is_free if ai_model else False
            
            # Check image generation limits before proceeding
            if subscription_type:
                within_limit, message = UsageService.check_image_generation_limit(
                    request.user, subscription_type, is_free_model
                )
                
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)
            
            # Save user message
            user_message_content = prompt if prompt else "تصویر ارسال شد"
            user_message_tokens = UsageService.calculate_tokens_for_message(user_message_content)
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message_content,
                tokens_count=user_message_tokens
            )
            
            # If an image was uploaded, save it to the server and to the message
            image_url = None
            if image_file:
                # Save the user uploaded image to the server
                try:
                    from .models import UserUploadedImage
                    import os
                    from django.utils.text import slugify
                    
                    # Create a UserUploadedImage record
                    user_uploaded_image = UserUploadedImage(
                        session=session,
                        user=request.user
                    )
                    
                    # Generate a filename
                    filename = f"{slugify(os.path.splitext(image_file.name)[0])}_{timezone.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(image_file.name)[1]}"
                    
                    # Save the image content
                    user_uploaded_image.image.save(
                        filename,
                        image_file,
                        save=True
                    )
                    
                    # Update the user message with the local image URL
                    user_message.image_url = request.build_absolute_uri(user_uploaded_image.image.url)
                    user_message.save()
                    
                    # Set image_url for use in the request to AI
                    image_url = request.build_absolute_uri(user_uploaded_image.image.url)
                except Exception as e:
                    # Log the error but don't fail the request
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving user uploaded image: {str(e)}")
                    # Fallback to placeholder
                    user_message.image_url = "user_uploaded_image"
                    user_message.save()
                    image_url = "user_uploaded_image"
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            # Send to OpenRouter API
            openrouter_service = OpenRouterService()
            
            # Preserve complete chat history context for image generation
            # Get conversation history for context
            messages = session.messages.all().order_by('created_at')
            openrouter_messages = []
            
            # Add system prompt if exists (for chatbots)
            if session.chatbot and session.chatbot.system_prompt:
                openrouter_messages.append({
                    'role': 'system',
                    'content': session.chatbot.system_prompt
                })
            
            # Add conversation history to provide context for image generation
            for msg in messages:
                # For image messages, we need to format them properly
                if msg.image_url and msg.image_url.startswith('http'):
                    # This is an assistant message with a generated image or user uploaded image
                    openrouter_messages.append({
                        'role': msg.message_type,
                        'content': [
                            {
                                'type': 'text',
                                'text': msg.content
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': msg.image_url
                                }
                            }
                        ]
                    })
                else:
                    # Regular text message
                    openrouter_messages.append({
                        'role': msg.message_type,
                        'content': msg.content
                    })
            
            # Add the current user message to the context
            current_user_message = {
                'role': 'user',
                'content': prompt if prompt else "تصویر ارسال شد"
            }
            
            # If an image was uploaded, add it to the current message
            if image_file:
                # First, encode the image to base64 for sending to AI
                import base64
                from io import BytesIO
                
                # Reset file pointer to beginning
                image_file.seek(0)
                # Read the image file
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Determine content type
                content_type = image_file.content_type
                if content_type not in ['image/png', 'image/jpeg', 'image/webp', 'image/gif']:
                    content_type = 'image/jpeg'  # Default to jpeg
                
                data_url = f"data:{content_type};base64,{base64_image}"
                
                # Update the current user message to include the image
                current_user_message['content'] = [
                    {
                        'type': 'text',
                        'text': prompt if prompt else "تصویر ارسال شد"
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': data_url
                        }
                    }
                ]
            elif modify_image_url:
                # This is a modification request for a previously generated image
                current_user_message['content'] = [
                    {
                        'type': 'text',
                        'text': prompt if prompt else "لطفاً این تصویر را اصلاح کنید"
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': modify_image_url
                        }
                    }
                ]
            
            # Add the current message to the context
            openrouter_messages.append(current_user_message)
            
            # Determine if this is an image analysis or generation request
            if (image_file or modify_image_url) and prompt:
                # Image analysis/modification request
                response = openrouter_service.send_image_message_with_context(
                    ai_model, openrouter_messages
                )
            elif image_file or modify_image_url:
                # Only image uploaded/modified - this is an unusual case, treat as prompt
                return JsonResponse({'error': 'برای تحلیل/اصلاح تصویر، متن توضیحی نیز الزامی است'}, status=400)
            else:
                # Only prompt - send as image generation request with full context
                response = openrouter_service.send_image_generation_request_with_context(
                    ai_model, openrouter_messages
                )
            
            if isinstance(response, dict) and 'error' in response:
                return JsonResponse({'error': response['error']}, status=500)
            
            # Process response and save assistant message
            if isinstance(response, dict) and 'choices' in response:
                assistant_content = response['choices'][0]['message']['content']
                
                # Get actual token counts from OpenRouter API
                prompt_tokens = response.get('usage', {}).get('prompt_tokens', 0)
                completion_tokens = response.get('usage', {}).get('completion_tokens', 0)
                total_tokens = response.get('usage', {}).get('total_tokens', prompt_tokens + completion_tokens)
                
                # Use the actual token count from API
                assistant_tokens = total_tokens
                
                # Check if there are images in the response
                image_urls = []
                if 'images' in response['choices'][0]['message']:
                    images = response['choices'][0]['message']['images']
                    for img in images:
                        if 'image_url' in img and 'url' in img['image_url']:
                            image_urls.append(img['image_url']['url'])
                
                # Save the assistant message
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    message_type='assistant',
                    content=assistant_content,
                    tokens_count=assistant_tokens
                )
                
                # Save image URLs if any and download the images to the server
                if image_urls:
                    assistant_message.image_url = image_urls[0]  # Save the first image URL
                    assistant_message.save()
                    
                    # Download and save the generated image to the server
                    try:
                        import requests
                        from django.core.files.base import ContentFile
                        from urllib.parse import urlparse
                        import os
                        
                        # Get the image content
                        image_response = requests.get(image_urls[0])
                        if image_response.status_code == 200:
                            # Create a GeneratedImage record
                            generated_image = GeneratedImage(
                                session=session,
                                user=request.user,
                                original_prompt=prompt if not modify_image_url else "",
                                modification_prompt=prompt if modify_image_url else ""
                            )
                            
                            # Generate a filename
                            parsed_url = urlparse(image_urls[0])
                            filename = os.path.basename(parsed_url.path)
                            if not filename:
                                filename = f"generated_image_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png"
                            
                            # Save the image content
                            generated_image.image.save(
                                filename,
                                ContentFile(image_response.content),
                                save=True
                            )
                            
                            # Update the assistant message with the local image URL
                            assistant_message.image_url = request.build_absolute_uri(generated_image.image.url)
                            assistant_message.save()
                    except Exception as e:
                        # Log the error but don't fail the request
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error saving generated image: {str(e)}")
                
                # Increment usage counters with actual token counts from API
                if subscription_type:
                    # For image generation, we use the total tokens from the API response
                    UsageService.increment_usage(
                        request.user, subscription_type, 
                        messages_count=2,  # User message + assistant message
                        tokens_count=total_tokens,
                        is_free_model=is_free_model
                    )
                    
                    # Create or update ChatSessionUsage record for this session
                    from .models import ChatSessionUsage
                    chat_session_usage, created = ChatSessionUsage.objects.get_or_create(
                        session=session,
                        user=request.user,
                        subscription_type=subscription_type,
                        defaults={
                            'tokens_count': total_tokens,
                            'free_model_tokens_count': total_tokens if is_free_model else 0,
                            'is_free_model': is_free_model
                        }
                    )
                    if not created:
                        # Update existing record
                        if is_free_model:
                            chat_session_usage.free_model_tokens_count += total_tokens
                        else:
                            chat_session_usage.tokens_count += total_tokens
                        chat_session_usage.save()
                
                # Ensure UTF-8 encoding for the response
                response_data = {
                    'message_id': assistant_message.id,
                    'content': assistant_content,
                    'image_urls': image_urls,
                    'tokens_count': assistant_tokens
                }
                response_json = json.dumps(response_data, ensure_ascii=False)
                return JsonResponse(json.loads(response_json), safe=False, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({'error': 'پاسخ نامعتبر از مدل هوش مصنوعی'}, status=500)
                
        except Exception as e:
            # Log the actual error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in send_image_message: {str(e)}", exc_info=True)
            error_details = {
                'error': 'خطای سرور داخلی',
                'details': str(e),
                'type': type(e).__name__
            }
            # Ensure UTF-8 encoding for error response
            response_json = json.dumps(error_details, ensure_ascii=False)
            return JsonResponse(json.loads(response_json), status=500, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)
