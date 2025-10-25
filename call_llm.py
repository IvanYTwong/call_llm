"""
OpenRouter LLM OOP Module

A production-ready, object-oriented Python module to interact with OpenRouter.ai API
supporting free models (llama, qwen, etc.) with chat completion, streaming, 
conversation history, and error handling.
"""

import os
import time
import json
import requests
from typing import List, Dict, Any, Optional, Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OpenRouterError(Exception):
    """Base exception class for OpenRouter API errors."""
    pass


class RateLimitError(OpenRouterError):
    """Raised when API rate limit is exceeded."""
    pass


class APIError(OpenRouterError):
    """Raised when API returns an error response."""
    pass


class ConversationHistory:
    """Manages conversation history for multi-turn conversations."""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: 'user', 'assistant', or 'system'
            content: The message content
        """
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation history."""
        return self.messages.copy()
    
    def clear(self) -> None:
        """Clear all messages from the conversation history."""
        self.messages.clear()
    
    def save(self, filename: str) -> None:
        """Save conversation history to a JSON file.
        
        Args:
            filename: Path to save the conversation
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)
    
    def load(self, filename: str) -> None:
        """Load conversation history from a JSON file.
        
        Args:
            filename: Path to load the conversation from
        """
        with open(filename, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)


class OpenRouterClient:
    """Main client for interacting with OpenRouter.ai API."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, 
                 max_retries: int = 3, retry_delay: float = 1.0,
                 available_models: Optional[List[str]] = None):
        """Initialize the OpenRouter client.
        
        Args:
            model: Model name (e.g., "meta-llama/llama-4-maverick:free")
            api_key: OpenRouter API key (if None, reads from OPENROUTER_API_KEY env var)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            available_models: Optional list of available models for validation
        """
        self.model = model
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = "https://openrouter.ai/api/v1"
        self.available_models = available_models or []
        
        if not self.api_key:
            raise ValueError("API key not provided. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Optional: replace with your repo
            "X-Title": "OpenRouter LLM Module"  # Optional: replace with your app name
        }
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle API error responses.
        
        Args:
            response: The HTTP response object
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        try:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
        except:
            error_message = f"HTTP {response.status_code}: {response.text}"
        
        if response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        else:
            raise APIError(f"API error ({response.status_code}): {error_message}")
    
    def _make_request(self, payload: Dict[str, Any], stream: bool = False) -> requests.Response:
        """Make a request to the OpenRouter API with retry logic.
        
        Args:
            payload: The request payload
            stream: Whether to stream the response
            
        Returns:
            The HTTP response object
            
        Raises:
            OpenRouterError: For API errors after retries
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    stream=stream,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response
                else:
                    self._handle_error(response)
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise OpenRouterError(f"Request failed after {self.max_retries} retries: {str(e)}")
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)
        
        raise OpenRouterError("Max retries exceeded")
    
    def chat(self, message: str, history: Optional[ConversationHistory] = None, 
             system_prompt: Optional[str] = None, **kwargs) -> str:
        """Send a chat message and get the complete response.
        
        Args:
            message: The user message
            history: Optional conversation history
            system_prompt: Optional system prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The assistant's response as a string
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if provided
        if history:
            messages.extend(history.get_messages())
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Prepare payload
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        # Make request
        response = self._make_request(payload)
        data = response.json()
        
        # Extract and return the response
        assistant_message = data['choices'][0]['message']['content']
        
        # Add messages to history if provided
        if history:
            history.add_message("user", message)
            history.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def chat_stream(self, message: str, history: Optional[ConversationHistory] = None,
                   system_prompt: Optional[str] = None, **kwargs) -> Generator[str, None, None]:
        """Send a chat message and get streaming response.
        
        Args:
            message: The user message
            history: Optional conversation history
            system_prompt: Optional system prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            Chunks of the assistant's response as strings
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if provided
        if history:
            messages.extend(history.get_messages())
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Prepare payload
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        # Make streaming request
        response = self._make_request(payload, stream=True)
        
        # Collect full response for history
        full_response = ""
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                delta = chunk_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    full_response += content
                                    yield content
                        except json.JSONDecodeError:
                            continue
        
        except Exception as e:
            raise OpenRouterError(f"Error processing streaming response: {str(e)}")
        
        # Add messages to history if provided
        if history:
            history.add_message("user", message)
            history.add_message("assistant", full_response)
    
    def switch_model(self, new_model: str) -> None:
        """Switch to a different model.
        
        Args:
            new_model: The new model name to switch to
            
        Raises:
            ValueError: If model validation is enabled and model is not in available_models
        """
        # Validate model if available_models is configured
        if self.available_models and new_model not in self.available_models:
            raise ValueError(f"Model '{new_model}' not in available models: {self.available_models}")
        
        self.model = new_model
    
    def get_current_model(self) -> str:
        """Get the currently active model name.
        
        Returns:
            The current model name
        """
        return self.model
    
    def list_available_models(self) -> List[str]:
        """Get the list of available models (if configured).
        
        Returns:
            List of available model names, or empty list if not configured
        """
        return self.available_models.copy()
    
    def add_available_model(self, model: str) -> None:
        """Add a model to the available models list.
        
        Args:
            model: Model name to add
        """
        if model not in self.available_models:
            self.available_models.append(model)
    
    def remove_available_model(self, model: str) -> None:
        """Remove a model from the available models list.
        
        Args:
            model: Model name to remove
        """
        if model in self.available_models:
            self.available_models.remove(model)

