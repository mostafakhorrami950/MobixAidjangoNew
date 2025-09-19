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
            # Use the :online suffix approach as it's equivalent to the web plugin
            payload["model"] = f"{ai_model.model_id}:online"
            # Also add web search options as fallback
            payload["web_search_options"] = {
                "search_context_size": "medium"
            }
        
        # Add modalities for image generation
        if modalities:
            payload["modalities"] = modalities
        
        # Add plugins for PDF processing
        if plugins:
            payload["plugins"] = plugins
        
        try:
            headers = self.get_headers()
        except ValueError as e:
            return {"error": str(e)}
        
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
            
            # Check if response is a requests.Response object
            if not hasattr(response, 'iter_content'):
                return {"error": "Invalid response object for streaming"}
            
            def generate():
                buffer = ""
                usage_data = None
                try:
                    # Type check: ensure response has iter_content method
                    if not isinstance(response, requests.Response):
                        yield "Error: Invalid response object for streaming"
                        return
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            # Decode chunk with UTF-8
                            try:
                                chunk_str = chunk.decode('utf-8')
                                buffer += chunk_str
                            except UnicodeDecodeError:
                                # Try different encodings if UTF-8 fails
                                try:
                                    chunk_str = chunk.decode('latin-1')
                                    buffer += chunk_str
                                except UnicodeDecodeError:
                                    continue
                            
                            # Process SSE events correctly
                            while '\n\n' in buffer:
                                message_end = buffer.find('\n\n')
                                message = buffer[:message_end]
                                buffer = buffer[message_end + 2:]
                                
                                for line in message.split('\n'):
                                    if line.startswith('data: '):
                                        data = line[6:]  # Remove 'data: ' prefix
                                        if data == '[DONE]':
                                            # Send usage data at the end
                                            if usage_data:
                                                yield f"\n\n[USAGE_DATA]{json.dumps(usage_data)}[USAGE_DATA_END]"
                                            return  # Exit the generator completely
                                        try:
                                            data_obj = json.loads(data)
                                            # Capture usage data if present
                                            if 'usage' in data_obj:
                                                usage_data = data_obj['usage']
                                            if 'choices' in data_obj and len(data_obj['choices']) > 0:
                                                delta = data_obj['choices'][0].get('delta', {})
                                                content = delta.get('content', '')
                                                
                                                # Handle image responses
                                                images = delta.get('images', [])
                                                if images:
                                                    # Send image data separately
                                                    yield f"\n\n[IMAGES]{json.dumps(images)}[IMAGES_END]"
                                                
                                                if content:
                                                    yield content
                                        except json.JSONDecodeError:
                                            # Skip invalid JSON
                                            continue
                except Exception as e:
                    yield f"Error in streaming: {str(e)}"
            
            return generate()
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
                    header, b64data = url.split(",", 1)
                    mime = header.split(";")[0].split(":")[1]
                    
                    # Determine file extension
                    ext = "png"  # default
                    if mime == "image/png":
                        ext = "png"
                    elif mime == "image/jpeg":
                        ext = "jpg"
                    elif mime == "image/webp":
                        ext = "webp"
                    elif mime == "image/gif":
                        ext = "gif"
                    
                    # Generate unique filename
                    from uuid import uuid4
                    filename = f"{uuid4().hex}.{ext}"
                    
                    # Save file
                    from django.core.files.storage import default_storage
                    from django.core.files.base import ContentFile
                    import base64
                    
                    file_path = os.path.join('uploads', filename)
                    file_content = base64.b64decode(b64data)
                    path = default_storage.save(file_path, ContentFile(file_content))
                    
                    # Save to database
                    img_record = UploadedFile(
                        user=session.user,
                        session=session,
                        filename=filename,
                        original_filename=f"generated_image.{ext}",
                        mimetype=mime,
                        size=len(file_content)
                    )
                    img_record.save()
                    
                    saved_image_ids.append(img_record.pk)
                    saved_image_urls.append(f"/media/uploads/{filename}")
                except Exception as e:
                    print(f"Error processing image: {e}")
                    continue
            else:
                # If it's a public URL, just add it to the list
                saved_image_urls.append(url)
        
        return saved_image_urls, saved_image_ids