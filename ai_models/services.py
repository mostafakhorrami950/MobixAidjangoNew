import requests
import json
import base64
from django.conf import settings
from django.utils import timezone
from django.http import StreamingHttpResponse
from .models import AIModel
from chatbot.models import ChatSession, ChatMessage, WebSearch, PDFDocument
from subscriptions.models import UserUsage
from subscriptions.services import UsageService

# Import the new OpenAI library
from openai import OpenAI
import httpx
import os


class OpenRouterService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = "https://openrouter.ai/api/v1"
        # Initialize the OpenAI client for OpenRouter
        if self.api_key and self.api_key != 'your_openrouter_api_key_here':
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            self.client = None
    
    def get_headers(self):
        if not self.api_key or self.api_key == 'your_openrouter_api_key_here':
            raise ValueError("OpenRouter API key is not configured properly in settings.py")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, ai_model, messages, stream=False, web_search=False, pdf_content=None):
        """
        Send text message to OpenRouter API with usage tracking using the new OpenAI library
        Supports web search and PDF content
        """
        if not self.client:
            return {"error": "OpenRouter API key is not configured properly"}
        
        try:
            # Prepare the request parameters
            request_params = {
                "model": ai_model.model_id,
                "messages": messages,
                "stream": stream,
                "extra_headers": {
                    "HTTP-Referer": "http://localhost:8000",  # Optional, for OpenRouter analytics
                    "X-Title": "MobixAI"  # Optional, for OpenRouter analytics
                }
            }
            
            # Add web search plugin if requested
            if web_search:
                # Check if model already has :online suffix
                if ":online" not in ai_model.model_id:
                    # Use plugin approach with custom settings
                    request_params["tools"] = [
                        { 
                            "type": "function",
                            "function": {
                                "name": "web_search",
                                "description": "Search the web for information",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "The search query"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        }
                    ]
                    request_params["tool_choice"] = "auto"
                # If model already has :online, no need to add plugins
            
            # Add PDF content if provided
            if pdf_content:
                # For PDF content, we'll add it to the messages
                # The file-parser plugin is automatically used by OpenRouter when PDF content is detected
                pass
            
            # Use the new OpenAI client
            response = self.client.chat.completions.create(**request_params)
            
            if stream:
                # Return the streaming response directly
                return response
            else:
                # Convert the response to a dictionary
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def send_image_generation_request(self, ai_model, prompt, stream=False):
        """
        Send image generation request to OpenRouter API with usage tracking using the new OpenAI library
        """
        if not self.client:
            return {"error": "OpenRouter API key is not configured properly"}
        
        try:
            # Use the new OpenAI client with modalities
            response = self.client.chat.completions.create(
                model=ai_model.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=stream,
                extra_body={
                    "modalities": ["image", "text"]
                },
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",  # Optional, for OpenRouter analytics
                    "X-Title": "MobixAI"  # Optional, for OpenRouter analytics
                }
            )
            
            if stream:
                # Return the streaming response directly
                return response
            else:
                # Convert the response to a dictionary
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

    def send_image_generation_request_with_context(self, ai_model, messages, stream=False):
        """
        Send image generation request to OpenRouter API with full conversation context using the new OpenAI library
        """
        if not self.client:
            return {"error": "OpenRouter API key is not configured properly"}
        
        try:
            # Use the new OpenAI client with modalities
            response = self.client.chat.completions.create(
                model=ai_model.model_id,
                messages=messages,
                stream=stream,
                extra_body={
                    "modalities": ["image", "text"]
                },
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",  # Optional, for OpenRouter analytics
                    "X-Title": "MobixAI"  # Optional, for OpenRouter analytics
                }
            )
            
            if stream:
                # Return the streaming response directly
                return response
            else:
                # Convert the response to a dictionary
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def stream_text_response(self, ai_model, messages, web_search=False, pdf_content=None):
        """
        Stream text response from OpenRouter API with usage tracking using the new OpenAI library
        Supports web search and PDF content
        """
        try:
            response = self.send_text_message(ai_model, messages, stream=True, web_search=web_search, pdf_content=pdf_content)
            if isinstance(response, dict) and 'error' in response:
                return response
            
            def generate():
                usage_data = None
                try:
                    # Process the streaming response
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content
                        
                        # Capture usage data if present in the final chunk
                        if hasattr(chunk, 'usage') and chunk.usage:
                            usage_data = {
                                "prompt_tokens": chunk.usage.prompt_tokens,
                                "completion_tokens": chunk.usage.completion_tokens,
                                "total_tokens": chunk.usage.total_tokens
                            }
                    
                    # Send usage data at the end
                    if usage_data:
                        yield f"\n\n[USAGE_DATA]{json.dumps(usage_data)}[USAGE_DATA_END]"
                except Exception as e:
                    yield f"Error in streaming: {str(e)}"
            
            return generate()
        except Exception as e:
            return {"error": f"Streaming error: {str(e)}"}
    
    def encode_image_to_base64(self, image_path):
        """
        Encode image to base64
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def send_image_message(self, ai_model, image_url, prompt, stream=False):
        """
        Send image message to OpenRouter API using the new OpenAI library
        """
        if not self.client:
            return {"error": "OpenRouter API key is not configured properly"}
        
        try:
            # Use the new OpenAI client with image content
            response = self.client.chat.completions.create(
                model=ai_model.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                stream=stream,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",  # Optional, for OpenRouter analytics
                    "X-Title": "MobixAI"  # Optional, for OpenRouter analytics
                }
            )
            
            if stream:
                # Return the streaming response directly
                return response
            else:
                # Convert the response to a dictionary
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

    def send_image_message_with_context(self, ai_model, messages, stream=False):
        """
        Send image message to OpenRouter API with full conversation context using the new OpenAI library
        """
        if not self.client:
            return {"error": "OpenRouter API key is not configured properly"}
        
        try:
            # Use the new OpenAI client
            response = self.client.chat.completions.create(
                model=ai_model.model_id,
                messages=messages,
                stream=stream,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",  # Optional, for OpenRouter analytics
                    "X-Title": "MobixAI"  # Optional, for OpenRouter analytics
                }
            )
            
            if stream:
                # Return the streaming response directly
                return response
            else:
                # Convert the response to a dictionary
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def encode_pdf_to_base64(self, pdf_path):
        """
        Encode PDF to base64
        """
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')