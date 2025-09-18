from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.db.models import Q
from django.apps import apps
from django.conf import settings
from django.urls import reverse
from ai_models.services import OpenRouterService
from subscriptions.models import UserSubscription
from subscriptions.services import UsageService
from .file_services import FileUploadService
from .models import UploadedFile, UploadedImage, SidebarMenuItem  # Add UploadedFile import and SidebarMenuItem
import json

# Add these imports for image handling
import base64
import requests
import mimetypes

# Add import for PDF processing
import PyPDF2
import io

@login_required
def chat(request):
    # Get all available chatbots for the user
    Chatbot = apps.get_model('chatbot', 'Chatbot')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    AIModel = apps.get_model('ai_models', 'AIModel')
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
def get_available_models_for_user(request):
    """
    Get all available AI models for the current user based on their subscription
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        AIModel = apps.get_model('ai_models', 'AIModel')
        user_subscription = request.user.get_subscription_type()
        
        # Get text generation models only (for chat)
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
            'models': model_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_available_models_for_chatbot(request, chatbot_id):
    """
    Get available AI models for a specific chatbot based on its type
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        AIModel = apps.get_model('ai_models', 'AIModel')
        chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
        user_subscription = request.user.get_subscription_type()
        
        # Filter models based on chatbot type
        if chatbot.chatbot_type == 'image_editing':
            # For image editing chatbots, only show image generation models
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
def create_default_session(request):
    """
    Create a new chat session with default settings (chatbot and AI model)
    """
    if request.method == 'POST':
        try:
            Chatbot = apps.get_model('chatbot', 'Chatbot')
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            AIModel = apps.get_model('ai_models', 'AIModel')
            DefaultChatSettings = apps.get_model('chatbot', 'DefaultChatSettings')
            
            # Get data from request
            data = json.loads(request.body) if request.body else {}
            ai_model_id = data.get('ai_model_id')
            
            # Initialize selected_ai_model as None
            selected_ai_model = None
            
            # If AI model ID is provided, use it
            if ai_model_id:
                try:
                    selected_ai_model = AIModel.objects.get(model_id=ai_model_id, is_active=True)
                    # Check if user has access to the selected model
                    if not request.user.has_access_to_model(selected_ai_model):
                        return JsonResponse({
                            'error': 'شما دسترسی لازم به مدل انتخابی را ندارید'
                        }, status=403)
                except AIModel.DoesNotExist:
                    return JsonResponse({
                        'error': 'مدل انتخابی وجود ندارد'
                    }, status=400)
            
            # Get default settings
            default_settings = DefaultChatSettings.objects.filter(is_active=True).first()
            if not default_settings:
                # If no default settings, create one or use fallback
                # Try to find a free chatbot and model
                free_chatbot = Chatbot.objects.filter(
                    is_active=True, 
                    subscription_types__isnull=True
                ).first()
                
                free_model = AIModel.objects.filter(
                    is_active=True, 
                    is_free=True, 
                    model_type='text'
                ).first()
                
                if not free_chatbot or not free_model:
                    return JsonResponse({
                        'error': 'هیچ چت‌بات یا مدل پیش‌فرض فعالی یافت نشد. لطفاً از طریق منو چت جدید ایجاد کنید.'
                    }, status=400)
                
                chatbot = free_chatbot
                ai_model = selected_ai_model if selected_ai_model else free_model
            else:
                chatbot = default_settings.default_chatbot
                ai_model = selected_ai_model if selected_ai_model else default_settings.default_ai_model
            
            # Check if user has access to this chatbot
            if chatbot.subscription_types.exists():
                user_subscription = request.user.get_subscription_type()
                if not user_subscription or not chatbot.subscription_types.filter(id=user_subscription.id).exists():
                    return JsonResponse({
                        'error': 'شما دسترسی لازم به چت‌بات پیش‌فرض را ندارید'
                    }, status=403)
            
            # Check if user has access to the AI model
            if not request.user.has_access_to_model(ai_model):
                return JsonResponse({
                    'error': 'شما دسترسی لازم به مدل پیش‌فرض را ندارید'
                }, status=403)
            
            # Create new chat session
            session = ChatSession.objects.create(
                user=request.user,
                chatbot=chatbot,
                ai_model=ai_model,
                title='چت جدید'
            )
            
            return JsonResponse({
                'session_id': session.id,
                'title': session.title,
                'chatbot_name': chatbot.name,
                'chatbot_type': chatbot.chatbot_type,
                'chatbot_id': chatbot.id,
                'ai_model_name': ai_model.name
            })
            
        except Exception as e:
            return JsonResponse({'error': f'خطا در ایجاد جلسه: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def create_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        AIModel = apps.get_model('ai_models', 'AIModel')
        
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
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    ChatMessage = apps.get_model('chatbot', 'ChatMessage')
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    messages = session.messages.filter(disabled=False).all()
    message_list = []
    for message in messages:
        message_data = {
            'id': message.message_id,  # Use message_id for editing functionality
            'db_id': message.id,  # Keep database ID for other functionality
            'type': message.message_type,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'disabled': message.disabled
        }
        # Include image_url if it exists
        if message.image_url:
            message_data['image_url'] = message.image_url
        message_list.append(message_data)
    
    # Determine session type and name
    if session.chatbot:
        session_name = session.chatbot.name
        chatbot_type = session.chatbot.chatbot_type
        chatbot_id = session.chatbot.id
        # Get AI model name for chatbot sessions
        ai_model_name = session.ai_model.name if session.ai_model else None
    elif session.ai_model:
        session_name = session.ai_model.name
        chatbot_type = 'text'  # Default to text for direct AI model sessions
        chatbot_id = None
        ai_model_name = session.ai_model.name
    else:
        session_name = "Unknown"
        chatbot_type = 'text'
        chatbot_id = None
        ai_model_name = None
    
    return JsonResponse({
        'messages': message_list,
        'session_title': session.title,
        'session_name': session_name,
        'chatbot_type': chatbot_type,
        'chatbot_id': chatbot_id,
        'ai_model_name': ai_model_name
    })

@login_required
def send_message(request, session_id):
    # Define logger at the function level to ensure it's accessible in all blocks
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        try:
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            ChatMessage = apps.get_model('chatbot', 'ChatMessage')
            ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)

            # Handle both multipart/form-data (for file uploads) and JSON
            if request.content_type.startswith('multipart/form-data'):
                user_message_content = request.POST.get('message', '')
                uploaded_file = request.FILES.get('file')
                use_web_search = request.POST.get('use_web_search', 'false') == 'true'
                generate_image = request.POST.get('generate_image', 'false') == 'true'
            else:  # Handle regular JSON request
                data = json.loads(request.body.decode('utf-8'))
                user_message_content = data.get('message', '')
                uploaded_file = None
                use_web_search = data.get('use_web_search', False)
                generate_image = data.get('generate_image', False)

            # For image editing chatbots, always generate images by default
            if session.chatbot and session.chatbot.chatbot_type == 'image_editing':
                generate_image = True

            if not user_message_content and not uploaded_file:
                return JsonResponse({'error': 'محتوای پیام یا فایل الزامی است'}, status=400)

            # Check usage limits
            subscription_type = request.user.get_subscription_type()

            is_free_model = False
            ai_model = None

            if use_web_search:
                try:
                    WebSearchSettings = apps.get_model('ai_models', 'WebSearchSettings')
                    web_search_settings = WebSearchSettings.objects.get(is_active=True)
                    enabled_subscription_types = web_search_settings.enabled_subscription_types.all()

                    if subscription_type and subscription_type in enabled_subscription_types:
                        ai_model = web_search_settings.web_search_model
                        is_free_model = ai_model.is_free
                    elif not subscription_type and enabled_subscription_types.filter(name='Free').exists():
                        ai_model = web_search_settings.web_search_model
                        is_free_model = ai_model.is_free
                    else:
                        use_web_search = False
                except Exception:
                    use_web_search = False

            if not ai_model:
                if session.ai_model:
                    ai_model = session.ai_model
                    is_free_model = ai_model.is_free if ai_model else False
                else:
                    return JsonResponse({'error': 'هیچ مدل هوش مصنوعی با این جلسه مرتبط نیست'}, status=500)

            # فقط توکن‌های پیام جدید کاربر را محاسبه کن
            user_message_tokens = UsageService.calculate_tokens_for_message(user_message_content)

            # Perform comprehensive usage limit checking before sending any message to AI
            if subscription_type:
                # Update the comprehensive check to use actual token count
                within_limit, message = UsageService.comprehensive_check(
                    request.user, ai_model, subscription_type
                )
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)

            # Check image generation limits if requested
            if generate_image and subscription_type:
                within_limit, message = UsageService.check_image_generation_limit(
                    request.user, subscription_type
                )
                if not within_limit:
                    return JsonResponse({'error': message}, status=403)

            # Handle file upload if present
            content_parts = []
            user_message_to_save = user_message_content

            if user_message_content:
                content_parts.append({"type": "text", "text": user_message_content})

            # Check if this is an image editing request without a new file upload
            if (session.chatbot and session.chatbot.chatbot_type == 'image_editing' and 
                not uploaded_file and user_message_content):
                # Find the last assistant-generated image in this session
                last_image_message = session.messages.filter(
                    message_type='assistant'
                ).exclude(image_url='').order_by('-created_at').first()
                
                if last_image_message and last_image_message.image_url:
                    # Get the first image URL (in case there are multiple)
                    image_urls = last_image_message.image_url.split(',')
                    if image_urls:
                        first_image_url = image_urls[0].strip()
                        # Convert to absolute path if it's a relative path
                        from django.conf import settings
                        import os
                        image_path = os.path.join(settings.MEDIA_ROOT, first_image_url[7:])  # Remove '/media/' prefix
                        # Check if file exists
                        if os.path.exists(image_path):
                            # Read and encode the image
                            with open(image_path, "rb") as image_file:
                                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                                mime_type = 'image/png'  # Default, could be improved
                                image_data_url = f"data:{mime_type};base64,{encoded_image}"
                                content_parts.append({"type": "image_url", "image_url": {"url": image_data_url}})

            if uploaded_file:
                # Check file upload limits
                if subscription_type:
                    within_limit, message = FileUploadService.check_file_upload_limit(
                        request.user, subscription_type, session
                    )
                    if not within_limit:
                        return JsonResponse({'error': message}, status=403)
                    
                    # Check file size limit
                    within_limit, message = FileUploadService.check_file_size_limit(
                        subscription_type, uploaded_file.size
                    )
                    if not within_limit:
                        return JsonResponse({'error': message}, status=403)
                    
                    # Check file extension
                    file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else ''
                    if file_extension and not FileUploadService.check_file_extension_allowed(
                        subscription_type, file_extension
                    ):
                        return JsonResponse({'error': f"فرمت فایل {file_extension} مجاز نیست"}, status=403)
                
                # Save file information to database
                import uuid
                filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                mime_type, _ = mimetypes.guess_type(uploaded_file.name)
                
                # Save uploaded file record
                uploaded_file_record = UploadedFile(
                    user=request.user,
                    session=session,
                    filename=filename,
                    original_filename=uploaded_file.name,
                    mimetype=mime_type or 'application/octet-stream',
                    size=uploaded_file.size
                )
                uploaded_file_record.save()
                
                # Save the actual file
                # Create the directory if it doesn't exist
                import os
                from django.conf import settings
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_files')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file to disk
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Update the download URL to point to the saved file
                file_download_url = f"/media/uploaded_files/{filename}"
                
                # Handle different file types
                if mime_type and mime_type.startswith('image/'):
                    # Image processing (vision capability)
                    # For images, we still save to UploadedImage for vision processing
                    uploaded_image = UploadedImage(user=request.user, session=session, image_file=uploaded_file)
                    uploaded_image.save()

                    # Read and encode image properly using the file path from the model
                    image_file_path = str(uploaded_image.image_file)
                    full_image_path = os.path.join(str(settings.MEDIA_ROOT), image_file_path)
                    with open(full_image_path, "rb") as image_file:
                        image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                    image_url = f"data:{mime_type};base64,{encoded_image}"

                    content_parts.append({"type": "image_url", "image_url": {"url": image_url}})
                    user_message_to_save += f" (تصویر: {uploaded_file.name})"
                elif mime_type and (mime_type.startswith('text/') or 
                                   mime_type in ['application/json', 'application/xml', 'application/javascript', 
                                                'text/html', 'text/css', 'text/csv']):
                    # Text file processing
                    file_content = uploaded_file.read().decode('utf-8', errors='ignore')
                    # Limit file content to prevent token overflow
                    if len(file_content) > 10000:  # Limit to 10KB
                        file_content = file_content[:10000] + "... (محتوای اضافی حذف شد)"
                    
                    file_info = f"محتوای فایل '{uploaded_file.name}':\n{file_content}"
                    content_parts.append({"type": "text", "text": file_info})
                    user_message_to_save += f" (فایل متنی: {uploaded_file.name})"
                elif mime_type and mime_type == 'application/pdf':
                    # PDF file processing
                    try:
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                        text_content = ""
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() + "\n"
                        
                        # Limit PDF content to prevent token overflow
                        if len(text_content) > 10000:  # Limit to 10KB
                            text_content = text_content[:10000] + "... (محتوای اضافی حذف شد)"
                        
                        file_info = f"محتوای فایل PDF '{uploaded_file.name}':\n{text_content}"
                        content_parts.append({"type": "text", "text": file_info})
                    except Exception as e:
                        content_parts.append({"type": "text", "text": f"کاربر فایل PDF با نام '{uploaded_file.name}' را آپلود کرده است. لطفاً از کاربر بخواهید محتوای فایل را توضیح دهد."})
                    user_message_to_save += f" (فایل PDF: {uploaded_file.name})"
                elif mime_type and mime_type in ['application/msword', 
                                               'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                               'application/vnd.ms-excel',
                                               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                    # Office document processing (Word, Excel)
                    user_message_to_save += f" (فایل اداری: {uploaded_file.name})"
                    content_parts.append({"type": "text", "text": f"کاربر فایل اداری '{uploaded_file.name}' را آپلود کرده است. لطفاً از کاربر بخواهید محتوای فایل را توضیح دهد."})
                elif mime_type and mime_type in ['application/zip', 'application/x-rar-compressed']:
                    # Compressed file processing (ZIP, RAR)
                    user_message_to_save += f" (فایل فشرده: {uploaded_file.name})"
                    content_parts.append({"type": "text", "text": f"کاربر فایل فشرده '{uploaded_file.name}' را آپلود کرده است. لطفاً از کاربر بخواهید محتوای فایل را توضیح دهد."})
                else:
                    # Other file types
                    user_message_to_save += f" (فایل: {uploaded_file.name})"
                    content_parts.append({"type": "text", "text": f"کاربر فایل '{uploaded_file.name}' را آپلود کرده است. لطفاً از کاربر بخواهید محتوای فایل را توضیح دهد."})
                
                # Increment file upload usage if subscription type is available
                if subscription_type:
                    FileUploadService.increment_file_upload_usage(
                        request.user, subscription_type, session
                    )

            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message_to_save,
                tokens_count=user_message_tokens
            )

            session.updated_at = timezone.now()
            session.save()

            messages = session.messages.all().order_by('created_at')
            openrouter_messages = []

            if session.chatbot and session.chatbot.system_prompt:
                openrouter_messages.append({
                    'role': 'system',
                    'content': session.chatbot.system_prompt
                })

            for msg in messages:
                 openrouter_messages.append({
                    'role': msg.message_type,
                    'content': msg.content
                })


            # Only modify the last message if we have content parts with image or file content
            if len(content_parts) > 1 or (len(content_parts) == 1 and content_parts[0].get('type') == 'image_url'):
                 if openrouter_messages and openrouter_messages[-1]['role'] == 'user':
                    openrouter_messages[-1]['content'] = content_parts


            openrouter_service = OpenRouterService()
            
            # Set modalities for image generation if requested
            modalities = None
            if generate_image:
                modalities = ["image", "text"]
            
            response = openrouter_service.stream_text_response(
                ai_model, openrouter_messages, modalities=modalities
            )

            if isinstance(response, dict) and 'error' in response:
                return JsonResponse({'error': response['error']}, status=500)

            def generate():
                # Add USER_MESSAGE markers to send user message data to frontend
                user_message_data = {
                    'id': str(user_message.message_id),  # Use message_id (UUID) for editing
                    'db_id': user_message.id,  # Keep database ID for other functionality
                    'type': user_message.message_type,
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat(),
                }
                
                yield f"[USER_MESSAGE]{json.dumps(user_message_data)}[USER_MESSAGE_END]".encode('utf-8')
                
                full_response = ""
                usage_data = None
                images_data = None
                assistant_message_obj = None  # Object to hold assistant message for updating

                try:
                    # Create an empty assistant message object to update later
                    assistant_message_obj = ChatMessage.objects.create(
                        session=session,
                        message_type='assistant',
                        content="",  # Initial content is empty
                        tokens_count=0
                    )

                    for chunk in response:
                        # Handle image data
                        if '[IMAGES]' in chunk and '[IMAGES_END]' in chunk:
                            start_idx = chunk.find('[IMAGES]') + 8
                            end_idx = chunk.find('[IMAGES_END]')
                            images_json = chunk[start_idx:end_idx]
                            try:
                                images_data = json.loads(images_json)
                                # Increment image generation usage if subscription type is available
                                if subscription_type and generate_image:
                                    UsageService.increment_image_generation_usage(
                                        request.user, subscription_type
                                    )
                            except json.JSONDecodeError:
                                pass
                            continue
                        
                        # Handle usage data
                        if '[USAGE_DATA]' in chunk and '[USAGE_DATA_END]' in chunk:
                            start_idx = chunk.find('[USAGE_DATA]') + 12
                            end_idx = chunk.find('[USAGE_DATA_END]')
                            usage_json = chunk[start_idx:end_idx]
                            try:
                                usage_data = json.loads(usage_json)
                            except json.JSONDecodeError:
                                pass
                            continue
                        
                        # As soon as we receive a chunk of the response, we add it to the message and save to database
                        full_response += chunk
                        assistant_message_obj.content = full_response
                        assistant_message_obj.save(update_fields=['content']) # Only update content field

                        yield chunk.encode('utf-8')

                except Exception as e:
                    # In case of an error, log it and inform the user
                    logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                    yield f"Error: {str(e)}".encode('utf-8')

                finally:
                    # This block always runs, whether the response is fully received or the connection is lost
                    if assistant_message_obj:
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens_used = 0
                        
                        if usage_data:
                            # اولویت با داده‌های دقیق API است
                            prompt_tokens = usage_data.get('prompt_tokens', 0)
                            completion_tokens = usage_data.get('completion_tokens', 0)
                            total_tokens_used = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                            assistant_message_obj.tokens_count = total_tokens_used # ثبت کل توکن‌های تبادل
                        else:
                            # در صورت نبود داده، از محاسبه خودمان استفاده می‌کنیم
                            # **اصلاح منطق:** توکن‌های ورودی فقط پیام کاربر است
                            # توکن‌های خروجی پاسخ دستیار است
                            prompt_tokens = user_message_tokens
                            completion_tokens = UsageService.calculate_tokens_for_message(full_response)
                            total_tokens_used = prompt_tokens + completion_tokens
                            assistant_message_obj.tokens_count = completion_tokens # فقط توکن‌های پاسخ را ذخیره کن
                        
                        # If image data is available, save the URLs
                        images_saved = False
                        if images_data:
                            saved_image_urls, _ = openrouter_service.process_image_response(images_data, session)
                            if saved_image_urls:
                                assistant_message_obj.image_url = ",".join(saved_image_urls)
                                images_saved = True
                        
                        assistant_message_obj.save()
                        
                        # Update session timestamp
                        session.updated_at = timezone.now()
                        session.save()
                        
                        # Update usage counters - only for image editing chatbots if images were successfully generated
                        if subscription_type:
                            # For image editing chatbots, only increment usage if images were successfully generated
                            if session.chatbot and session.chatbot.chatbot_type == 'image_editing':
                                if images_saved:
                                    # Only increment usage if images were successfully saved
                                    UsageService.increment_image_generation_usage(
                                        request.user, subscription_type
                                    )
                            
                            # For other chatbots or if images were generated successfully, increment regular usage
                            if not (session.chatbot and session.chatbot.chatbot_type == 'image_editing') or images_saved:
                                if usage_data:
                                    # Use actual token counts from API
                                    prompt_tokens = usage_data.get('prompt_tokens', 0)
                                    completion_tokens = usage_data.get('completion_tokens', 0)
                                    total_tokens_used = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                                    
                                    # Log token usage for debugging
                                    logger.info(f"Token usage from API - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens_used}")
                                    
                                    UsageService.increment_usage(
                                        request.user, subscription_type,
                                        messages_count=2,  # User message + assistant message
                                        tokens_count=total_tokens_used,
                                        is_free_model=is_free_model
                                    )
                                else:
                                    # Fallback to our calculation if API doesn't provide usage data
                                    # **اصلاح منطق:** توکن‌های ورودی فقط پیام کاربر است
                                    # توکن‌های خروجی پاسخ دستیار است
                                    prompt_tokens = user_message_tokens
                                    completion_tokens = UsageService.calculate_tokens_for_message(full_response)
                                    total_tokens_used = prompt_tokens + completion_tokens
                                    
                                    # Log token usage for debugging
                                    logger.info(f"Token usage calculated - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens_used}")
                                    
                                    UsageService.increment_usage(
                                        request.user, subscription_type,
                                        messages_count=2,  # User message + assistant message
                                        tokens_count=total_tokens_used,
                                        is_free_model=is_free_model
                                    )
                                    
                                    # Also update ChatSessionUsage
                                    try:
                                        chat_session_usage, created = ChatSessionUsage.objects.get_or_create(
                                            session=session,
                                            user=request.user,
                                            subscription_type=subscription_type,
                                            defaults={'is_free_model': is_free_model}
                                        )
                                        if is_free_model:
                                            chat_session_usage.free_model_tokens_count = chat_session_usage.free_model_tokens_count + total_tokens_used
                                        else:
                                            chat_session_usage.tokens_count = chat_session_usage.tokens_count + total_tokens_used
                                        chat_session_usage.save()
                                        logger.info(f"ChatSessionUsage updated - Session: {session.id}, Tokens: {total_tokens_used}")
                                    except Exception as e:
                                        logger.error(f"Error updating ChatSessionUsage: {str(e)}")

            return StreamingHttpResponse(
                generate(),
                content_type='text/plain; charset=utf-8'
            )

        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_user_sessions(request):
    ChatSession = apps.get_model('chatbot', 'ChatSession')
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
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        AIModel = apps.get_model('ai_models', 'AIModel')
        first_message = data.get('first_message')
        
        # Check if generating title for chatbot or AI model
        if 'chatbot_id' in data:
            chatbot_id = data.get('chatbot_id')
            # Get the chatbot
            chatbot = get_object_or_404(Chatbot, id=chatbot_id, is_active=True)
            # For chatbots, we need to get a default AI model
            # Since chatbots don't directly have an AI model, we'll get one from the available models
            # Let's get the first available text model for this chatbot
            user_subscription = request.user.get_subscription_type()
            models_query = AIModel.objects.filter(
                is_active=True,
                model_type='text'
            )
            
            if user_subscription:
                # Get models available for user's subscription
                ai_model = models_query.filter(
                    Q(is_free=True) | Q(subscriptions__subscription_types=user_subscription)
                ).first()
            else:
                # If no subscription, only show free models
                ai_model = models_query.filter(is_free=True).first()
            
            # If no model found, use any active text model
            if not ai_model:
                ai_model = AIModel.objects.filter(
                    is_active=True,
                    model_type='text'
                ).first()
        elif 'model_id' in data:
            model_id = data.get('model_id')
            # Get the AI model
            ai_model = get_object_or_404(AIModel, model_id=model_id, is_active=True)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        # Make sure we have an AI model
        if not ai_model:
            return JsonResponse({'error': 'No AI model available'}, status=400)
        
        # Create a prompt for generating a chat title
        prompt = f"Create a short, descriptive title (maximum 5 words) for a chat about: {first_message}"
        
        # Send to OpenRouter API to generate title
        openrouter_service = OpenRouterService()
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = openrouter_service.send_text_message(ai_model, messages)
        
        if isinstance(response, dict) and 'error' in response:
            # Return a default title if AI fails
            return JsonResponse({'title': 'چت جدید'})
        
        if isinstance(response, dict) and 'choices' in response:
            try:
                # Safely extract title from response
                choices = response.get('choices', [])
                if choices and len(choices) > 0:
                    choice = choices[0]
                    if isinstance(choice, dict) and 'message' in choice:
                        message = choice['message']
                        if isinstance(message, dict) and 'content' in message:
                            content = message['content']
                            if content:
                                title = content.strip()
                                # Limit title to 50 characters
                                title = title[:50]
                                return JsonResponse({'title': title})
                # Return a default title if AI fails
                return JsonResponse({'title': 'چت جدید'})
            except (KeyError, IndexError, TypeError):
                # Return a default title if AI fails
                return JsonResponse({'title': 'چت جدید'})
        else:
            # Return a default title if AI fails
            return JsonResponse({'title': 'چت جدید'})
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def delete_session(request, session_id):
    if request.method == 'DELETE':
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.is_active = False
        session.save()
        return JsonResponse({'success': True})
    
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def update_session_title(request, session_id):
    if request.method == 'POST':
        try:
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            data = json.loads(request.body)
            new_title = data.get('title', 'چت جدید')
            
            session.title = new_title
            session.save()
            
            return JsonResponse({'success': True, 'title': new_title})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def check_web_search_access(request, session_id):
    """
    Check if the user has access to web search functionality for this session
    """
    if request.method == 'GET':
        try:
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            user_subscription = request.user.get_subscription_type()
            
            # Check if web search is enabled and if user has access
            try:
                WebSearchSettings = apps.get_model('ai_models', 'WebSearchSettings')
                web_search_settings = WebSearchSettings.objects.get(is_active=True)
                enabled_subscription_types = web_search_settings.enabled_subscription_types.all()
                
                # Check if user's subscription type is in the enabled list
                has_access = False
                if user_subscription and user_subscription in enabled_subscription_types:
                    has_access = True
                elif not user_subscription and enabled_subscription_types.filter(name='Free').exists():
                    # If user has no subscription, check if Free subscription is enabled
                    has_access = True
                
                return JsonResponse({
                    'has_access': has_access,
                    'web_search_model_id': web_search_settings.web_search_model.model_id if has_access else None
                })
            except Exception:
                # Web search is not configured
                return JsonResponse({
                    'has_access': False,
                    'web_search_model_id': None
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def check_image_generation_access(request, session_id):
    """
    Check if user has access to image generation functionality for a specific session
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        
        # Check if this is an image editing chatbot
        if session.chatbot and session.chatbot.chatbot_type == 'image_editing':
            return JsonResponse({'has_access': True})
        
        return JsonResponse({'has_access': False})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def analyze_image(request, session_id):
    """
    Handle image upload and analysis for vision-capable AI models
    """
    if request.method == 'POST':
        try:
            ChatSession = apps.get_model('chatbot', 'ChatSession')
            UploadedImage = apps.get_model('chatbot', 'UploadedImage')
            ChatMessage = apps.get_model('chatbot', 'ChatMessage')
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            uploaded_file = request.FILES.get('file')
            
            if not uploaded_file:
                return JsonResponse({'error': 'فایل تصویر الزامی است'}, status=400)
            
            # Check if file is an image
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if not mime_type or not mime_type.startswith('image/'):
                return JsonResponse({'error': 'فقط فایل‌های تصویری پشتیبانی می‌شوند'}, status=400)
            
            # Save the uploaded image
            uploaded_image = UploadedImage(user=request.user, session=session, image_file=uploaded_file)
            uploaded_image.save()
            
            # Read and encode image
            image_data = uploaded_image.image_file.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:{mime_type};base64,{encoded_image}"
            
            # Prepare message content with image
            content_parts = [
                {"type": "text", "text": "Describe this image in detail."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
            
            # Get conversation history
            messages = list(session.messages.order_by('created_at').values('message_type', 'content'))
            openrouter_messages = []
            
            # Add system prompt if exists
            if session.chatbot and session.chatbot.system_prompt:
                openrouter_messages.append({
                    'role': 'system',
                    'content': session.chatbot.system_prompt
                })
            
            # Add conversation history
            for msg in messages:
                openrouter_messages.append({
                    'role': msg['message_type'],
                    'content': msg['content']
                })
            
            # Add the new image message
            openrouter_messages.append({
                'role': 'user',
                'content': content_parts
            })
            
            # Get AI model for vision processing
            # Try to get from VisionProcessingSettings first, fallback to session model
            try:
                VisionProcessingSettings = apps.get_model('chatbot', 'VisionProcessingSettings')
                vision_settings = VisionProcessingSettings.objects.filter(is_active=True).first()
                if vision_settings:
                    ai_model = vision_settings.ai_model
                else:
                    ai_model = session.ai_model
            except:
                ai_model = session.ai_model
            
            if not ai_model:
                return JsonResponse({'error': 'هیچ مدل هوش مصنوعی با این جلسه مرتبط نیست'}, status=500)
            
            # Use the configured vision model or a default one
            vision_model_id = ai_model.model_id if ai_model else "anthropic/claude-3-haiku-20240307"
            
            # Send to OpenRouter API
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": vision_model_id,
                "messages": openrouter_messages
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            response_data = response.json()
            bot_response = response_data['choices'][0]['message']['content']
            
            # Save messages to database
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=f"Uploaded image: {uploaded_file.name}"
            )
            
            # Save bot response
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=bot_response
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            return JsonResponse({'response': bot_response})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def chat_session(request, session_id):
    """Dedicated view for a specific chat session"""
    # Verify the session exists and belongs to the user
    Chatbot = apps.get_model('chatbot', 'Chatbot')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    AIModel = apps.get_model('ai_models', 'AIModel')
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
def update_session_model(request, session_id):
    """
    Update the AI model for a specific chat session
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        AIModel = apps.get_model('ai_models', 'AIModel')
        
        # Get the session
        session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
        
        # Get the model_id from the request
        data = json.loads(request.body)
        model_id = data.get('model_id')
        
        if not model_id:
            return JsonResponse({'error': 'Model ID is required'}, status=400)
        
        # Get the AI model
        ai_model = get_object_or_404(AIModel, model_id=model_id, is_active=True)
        
        # Check if user has access to this model
        if not request.user.has_access_to_model(ai_model):
            return JsonResponse({'error': 'You do not have access to this AI model'}, status=403)
        
        # Update the session model
        session.ai_model = ai_model
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Model updated successfully',
            'model_name': ai_model.name
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_web_search_access_no_session(request):
    """
    Check if the user has access to web search functionality without a session
    """
    if request.method == 'GET':
        try:
            user_subscription = request.user.get_subscription_type()
            
            # Check if web search is enabled and if user has access
            try:
                WebSearchSettings = apps.get_model('ai_models', 'WebSearchSettings')
                web_search_settings = WebSearchSettings.objects.get(is_active=True)
                enabled_subscription_types = web_search_settings.enabled_subscription_types.all()
                
                # Check if user's subscription type is in the enabled list
                has_access = False
                if user_subscription and user_subscription in enabled_subscription_types:
                    has_access = True
                elif not user_subscription and enabled_subscription_types.filter(name='Free').exists():
                    # If user has no subscription, check if Free subscription is enabled
                    has_access = True
                
                return JsonResponse({
                    'has_access': has_access
                })
            except Exception:
                # Web search is not configured
                return JsonResponse({
                    'has_access': False
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'روش درخواست نامعتبر است'}, status=400)

@login_required
def get_sidebar_menu_items(request):
    """
    Get all active sidebar menu items that the user has permission to view
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        
        # Get all active menu items ordered by display order
        menu_items = SidebarMenuItem.objects.filter(is_active=True).order_by('order')
        
        # Filter items based on user permissions
        user_menu_items = []
        for item in menu_items:
            # If item should only be shown to authenticated users and user is not authenticated, skip it
            if item.show_only_for_authenticated and not request.user.is_authenticated:
                continue
                
            # If item should only be shown to non-authenticated users and user is authenticated, skip it
            if item.show_only_for_non_authenticated and request.user.is_authenticated:
                continue
            
            # If no permission is required, or user has the required permission
            if not item.required_permission or request.user.has_perm(item.required_permission):
                # Resolve the URL
                try:
                    # Handle namespaced URLs (e.g., 'chat:chat')
                    if ':' in item.url_name:
                        url = reverse(item.url_name)
                    else:
                        # Try to resolve as a chat app URL first, then fall back to global
                        try:
                            url = reverse(f'chat:{item.url_name}')
                        except:
                            url = reverse(item.url_name)
                    user_menu_items.append({
                        'name': item.name,
                        'url': url,
                        'icon_class': item.icon_class,
                        'order': item.order,
                        'show_only_for_authenticated': item.show_only_for_authenticated,
                        'show_only_for_non_authenticated': item.show_only_for_non_authenticated
                    })
                except:
                    # Skip items with invalid URLs
                    continue
        
        return JsonResponse({
            'menu_items': user_menu_items
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def edit_message(request, session_id, message_id):
    """
    Edit a user message and regenerate subsequent assistant messages
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        ChatMessage = apps.get_model('chatbot', 'ChatMessage')
        
        # Get the session and verify ownership
        session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
        
        # Get the message to edit
        message = get_object_or_404(ChatMessage, message_id=message_id, session=session, message_type='user')
        
        # Parse the new content
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)
        
        # Check usage limits before proceeding
        subscription_type = request.user.get_subscription_type()
        ai_model = session.ai_model or (session.chatbot and session.chatbot.get_default_model())
        
        if ai_model and subscription_type:
            # Perform comprehensive usage limit checking
            within_limit, message_limit = UsageService.comprehensive_check(
                request.user, ai_model, subscription_type
            )
            if not within_limit:
                return JsonResponse({'error': message_limit}, status=403)
        
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
        
        # Also mark the edited message as needing regeneration if it's an assistant message
        if message.message_type == 'assistant':
            message.needs_regeneration = True
            message.save()
        
        # Get all messages up to and including the edited message, excluding disabled messages
        messages_up_to_edited = session.messages.filter(
            created_at__lte=message.created_at,
            disabled=False
        ).order_by('created_at')
        
        # Prepare messages for AI regeneration
        openrouter_messages = []
        
        # Add system prompt if exists
        if session.chatbot and session.chatbot.system_prompt:
            openrouter_messages.append({
                'role': 'system',
                'content': session.chatbot.system_prompt
            })
        
        # Add conversation history up to the edited message
        for msg in messages_up_to_edited:
            openrouter_messages.append({
                'role': msg.message_type,
                'content': msg.content
            })
        
        # Send to AI for regeneration
        openrouter_service = OpenRouterService()
        
        # Get the AI model for this session
        if session.chatbot:
            # For chatbots, we might need to get a model from the chatbot configuration
            ai_model = session.ai_model
        else:
            ai_model = session.ai_model
        
        if not ai_model:
            return JsonResponse({'error': 'No AI model available for this session'}, status=500)
        
        response = openrouter_service.stream_text_response(
            ai_model, openrouter_messages
        )
        
        if isinstance(response, dict) and 'error' in response:
            return JsonResponse({'error': response['error']}, status=500)
        
        # Create a new assistant message for the response
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content="",  # Will be populated by streaming
            tokens_count=0
        )
        
        # Stream the response and update the assistant message
        def generate():
            # Send disabled message IDs to frontend
            disabled_data = {
                'disabled_message_ids': disabled_message_ids
            }
            yield f"[DISABLED_MESSAGES]{json.dumps(disabled_data)}[DISABLED_MESSAGES_END]".encode('utf-8')
            
            # Send the new assistant message ID to frontend
            assistant_message_data = {
                'assistant_message_id': str(assistant_message.message_id)
            }
            yield f"[ASSISTANT_MESSAGE_ID]{json.dumps(assistant_message_data)}[ASSISTANT_MESSAGE_ID_END]".encode('utf-8')
            
            full_response = ""
            usage_data = None
            
            try:
                for chunk in response:
                    # Handle usage data
                    if '[USAGE_DATA]' in chunk and '[USAGE_DATA_END]' in chunk:
                        start_idx = chunk.find('[USAGE_DATA]') + 12
                        end_idx = chunk.find('[USAGE_DATA_END]')
                        usage_json = chunk[start_idx:end_idx]
                        try:
                            usage_data = json.loads(usage_json)
                        except json.JSONDecodeError:
                            pass
                        continue
                    
                    # Accumulate response and update message
                    full_response += chunk
                    assistant_message.content = full_response
                    assistant_message.save(update_fields=['content'])
                    
                    yield chunk.encode('utf-8')
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in message editing stream: {str(e)}", exc_info=True)
                yield f"Error: {str(e)}".encode('utf-8')
            
            finally:
                # Finalize the assistant message
                if usage_data:
                    prompt_tokens = usage_data.get('prompt_tokens', 0)
                    completion_tokens = usage_data.get('completion_tokens', 0)
                    total_tokens = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                    assistant_message.tokens_count = total_tokens
                else:
                    # Fallback to character counting if API doesn't provide usage data
                    assistant_message.tokens_count = UsageService.calculate_tokens_for_message(full_response)
                
                # Process images if they were generated
                images_saved = False
                # Note: images_data is not available in this scope for edit_message function
                # Image processing for edit_message would need to be handled differently
                
                assistant_message.save()
                
                # Update session timestamp
                session.updated_at = timezone.now()
                session.save()
                
                # Update usage counters - only for image editing chatbots if images were successfully generated
                if subscription_type:
                    # For image editing chatbots, increment usage (images are processed in the main send_message function)
                    # In edit_message, we don't generate new images, so we don't increment image usage here
                    if session.chatbot and session.chatbot.chatbot_type == 'image_editing':
                        # For image editing chatbots during edit, we don't increment usage as no new images are generated
                        pass
                    else:
                        # For other chatbots, increment regular usage
                        if usage_data:
                            # Use actual token counts from API - these are the REAL consumption
                            prompt_tokens = usage_data.get('prompt_tokens', 0)
                            completion_tokens = usage_data.get('completion_tokens', 0)
                            total_tokens = usage_data.get('total_tokens', prompt_tokens + completion_tokens)
                            
                            UsageService.increment_usage(
                                request.user, subscription_type,
                                messages_count=1,  # Only count one interaction
                                tokens_count=total_tokens,  # Use actual API consumption
                                is_free_model=ai_model.is_free if ai_model else False
                            )
                        else:
                            # Fallback calculation - only the actual assistant response tokens
                            # Don't re-calculate conversation history as it's already been paid for
                            assistant_output_tokens = assistant_message.tokens_count
                            # Estimate prompt tokens based on edited message + small context overhead
                            edited_message_tokens = UsageService.calculate_tokens_for_message(new_content)
                            estimated_prompt_tokens = edited_message_tokens + 50  # Small overhead for system prompt
                            total_tokens = estimated_prompt_tokens + assistant_output_tokens
                            
                            UsageService.increment_usage(
                                request.user, subscription_type,
                                messages_count=1,  # Only count one interaction
                                tokens_count=total_tokens,  # Only actual new consumption
                                is_free_model=ai_model.is_free if ai_model else False
                            )
        
        return StreamingHttpResponse(
            generate(),
            content_type='text/plain; charset=utf-8'
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in edit_message: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
