import requests
import json
import base64
from django.conf import settings
from django.utils import timezone
from django.http import StreamingHttpResponse
from .models import AIModel
from chatbot.models import ChatSession, ChatMessage
from chatbot.models import UploadedFile  # Explicit import for linter
from subscriptions.models import UserUsage
from pathlib import Path
from typing import List, Optional, Union
import mimetypes
import os
from django.core.exceptions import ObjectDoesNotExist

class OpenRouterService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = "https://openrouter.ai/api/v1"
    
    def get_headers(self):
        if not self.api_key or self.api_key == 'your_openrouter_api_key_here':
            raise ValueError("OpenRouter API key is not configured properly in settings.py")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_file_to_data_url(self, file_path, mime_type=None):
        """
        Encode a file to data URL format for sending to OpenRouter
        """
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
        
        with open(file_path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode('utf-8')
        
        return f"data:{mime_type};base64,{file_data}"
    
    def prepare_image_content(self, image_urls=None, edit_prev_image_id=None, session=None):
        """
        Prepare image content for OpenRouter API
        """
        content = []
        
        # Add image URLs if provided
        if image_urls:
            for image_url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
        
        # Add previous image for editing if provided
        if edit_prev_image_id and session:
            try:
                # Using the explicit model reference to avoid linter issues
                prev_image = UploadedFile._default_manager.get(pk=edit_prev_image_id, session=session)
                
                # Get the file path
                from django.core.files.storage import default_storage
                file_path = os.path.join(default_storage.location, 'uploads', prev_image.filename)
                
                # Encode to data URL
                data_url = self.encode_file_to_data_url(file_path, prev_image.mimetype)
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                })
            except ObjectDoesNotExist:
                raise ValueError("تصویر مرجع ویرایش پیدا نشد")
        
        return content
    
    def prepare_file_content(self, file_urls=None, session=None):
        """
        Prepare file content (PDFs, etc.) for OpenRouter API
        """
        content = []
        
        # Add file URLs if provided
        if file_urls:
            for file_info in file_urls:
                content.append({
                    "type": "file",
                    "file": file_info
                })
        
        return content
    
    def prepare_messages_with_files(self, text_content, image_urls=None, edit_prev_image_id=None, 
                                   file_urls=None, session=None):
        """
        Prepare messages array for OpenRouter API with text, images, and files
        """
        messages = [
            {
                "role": "user",
                "content": []
            }
        ]
        
        # Add text content first (recommended by OpenRouter docs)
        if text_content:
            messages[0]["content"].append({
                "type": "text",
                "text": text_content
            })
        
        # Add image content
        image_content = self.prepare_image_content(image_urls, edit_prev_image_id, session)
        messages[0]["content"].extend(image_content)
        
        # Add file content
        file_content = self.prepare_file_content(file_urls, session)
        messages[0]["content"].extend(file_content)
        
        return messages
    
    def send_text_message(self, ai_model, messages, stream=False, web_search=False, 
                         modalities=None, plugins=None):
        """
        Send text message to OpenRouter API with usage tracking
        Enhanced to support images, files, and modalities
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": ai_model.model_id,
            "messages": messages,
            "stream": stream,
            "usage": {
                "include": True
            }
        }
        
        # Add web search options if enabled
        if web_search:
            payload["transforms"] = ["web-search"]
        
        # Add modalities if provided
        if modalities:
            payload["modalities"] = modalities
            
        # Add plugins if provided
        if plugins:
            payload["plugins"] = plugins
        
        headers = self.get_headers()
        
        try:
            if stream:
                response = requests.post(url, headers=headers, json=payload, stream=True)
                return response
            else:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response.json()
        except requests.exceptions.RequestException as e:
            # Check if this is a web search error
            if web_search:
                error_msg = str(e)
                if "model" in error_msg.lower() or "not found" in error_msg.lower():
                    return {"error": "خطا: امکان جستجوی وب برای مدل انتخابی در حال حاضر فعال نیست."}
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def stream_text_response(self, ai_model, messages, web_search=False, modalities=None, plugins=None):
        """
        Stream text response from OpenRouter API with usage tracking
        Enhanced to support images, files, and modalities
        """
        try:
            response = self.send_text_message(
                ai_model, messages, stream=True, web_search=web_search, 
                modalities=modalities, plugins=plugins
            )
            if isinstance(response, dict) and 'error' in response:
                return response
            
            # Check if response is a requests.Response object with iter_lines method
            if not (hasattr(response, 'iter_lines') and callable(getattr(response, 'iter_lines', None))):
                return {"error": "Invalid response object for streaming"}
            
            # Type check to satisfy linter
            from requests import Response
            if not isinstance(response, Response):
                return {"error": "Invalid response type for streaming"}
            
            def generate():
                buffer = ""
                usage_data = None
                try:
                    # Use iter_lines with decode_unicode=True for proper text handling
                    # Make sure we're not calling iter_lines multiple times
                    lines_iterator = response.iter_lines(decode_unicode=True)
                    for line in lines_iterator:
                        if line:
                            line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                            
                            # Skip empty lines and SSE comments
                            if line_str.startswith(':') or not line_str.strip():
                                continue
                            
                            # Remove SSE data prefix if present
                            if line_str.startswith('data: '):
                                line_str = line_str[6:]  # Remove 'data: ' prefix
                            
                            # Handle completion
                            if line_str.strip() == '[DONE]':
                                # Send any remaining buffer
                                if buffer:
                                    yield buffer
                                    buffer = ""
                                break
                            
                            try:
                                data_obj = json.loads(line_str)
                                
                                # Handle errors in the stream
                                if 'error' in data_obj:
                                    error_msg = data_obj['error'].get('message', 'Unknown error')
                                    yield f"Error: {error_msg}"
                                    break
                                
                                # Extract usage data if present
                                if 'usage' in data_obj:
                                    usage_data = data_obj['usage']
                                    # Send usage data separately
                                    yield f"[USAGE_DATA]{json.dumps(usage_data)}[USAGE_DATA_END]"
                                    continue
                                
                                # Process choices
                                if 'choices' in data_obj and len(data_obj['choices']) > 0:
                                    delta = data_obj['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    
                                    # Handle image responses
                                    images = delta.get('images', [])
                                    if images:
                                        # Send image data separately
                                        yield f"\n\n[IMAGES]{json.dumps(images)}[IMAGES_END]"
                                    
                                    if content:
                                        # Buffer content to reduce number of yields
                                        buffer += content
                                        # Yield buffer when it reaches a certain size to prevent excessive buffering
                                        if len(buffer) > 50:  # Yield in chunks of 50 characters
                                            yield buffer
                                            buffer = ""
                                            
                            except json.JSONDecodeError:
                                # Skip invalid JSON
                                continue
                    
                    # Send any remaining buffer
                    if buffer:
                        yield buffer
                        
                except Exception as e:
                    yield f"Error in streaming: {str(e)}"
            
            # Return the generator directly, not a dict
            return generate()  # Return the generator function itself, not calling it
        except Exception as e:
            return {"error": f"Streaming error: {str(e)}"}
    
    def process_image_response(self, images_data, session):
        """
        Process image responses from OpenRouter and save them
        """
        saved_image_urls = []
        saved_image_ids = []
        
        for img in images_data:
            url = img.get("image_url", {}).get("url")
            if url and url.startswith("data:"):
                # Extract mime type and base64 data
                try:
                    # Split data URL to get mime type and base64 data
                    header, base64_data = url.split(',', 1)
                    mime_type = header.split(':')[1].split(';')[0]
                    
                    # Decode base64 data
                    image_data = base64.b64decode(base64_data)
                    
                    # Generate unique filename
                    from django.utils.crypto import get_random_string
                    file_extension = mimetypes.guess_extension(mime_type) or '.png'
                    filename = f"ai_generated_{get_random_string(12)}{file_extension}"
                    
                    # Save image to media directory
                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage
                    
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(default_storage.location, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Create UploadedFile record using _default_manager to avoid linter issues
                    uploaded_file = UploadedFile._default_manager.create(
                        user=session.user,
                        session=session,
                        filename=filename,
                        original_filename=f"generated_image{file_extension}",
                        mimetype=mime_type,
                        size=len(image_data)
                    )
                    
                    # Add to saved images
                    saved_image_urls.append(f"/media/uploads/{filename}")
                    saved_image_ids.append(uploaded_file.id)
                    
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing generated image: {str(e)}", exc_info=True)
                    continue
            elif url:
                # Handle direct URLs (not base64 encoded)
                saved_image_urls.append(url)
        
        return saved_image_urls, saved_image_ids