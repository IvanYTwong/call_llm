# OpenRouter LLM Module - Project Briefing

## Project Overview
A production-ready, object-oriented Python module for interacting with OpenRouter.ai API. The system provides a clean, easy-to-use interface for calling various LLM models (including free models like Llama, Qwen) with support for chat completion, streaming responses, conversation history management, and robust error handling.

## Core Functions

### 1. OpenRouterClient Class
- **Purpose**: Main interface for API communication
- **Key Features**:
  - Initialize with any OpenRouter model (free or paid)
  - Automatic API key management from environment variables
  - Configurable retry logic with exponential backoff
  - Support for both standard and streaming responses
  - **Dynamic model switching** with validation
  - **Model management** with available models list

### 2. Model Management Methods
- **`switch_model()`**: Dynamically change to a different model
- **`get_current_model()`**: Get the currently active model name
- **`list_available_models()`**: Show configured available models
- **`add_available_model()`**: Add a model to the available list
- **`remove_available_model()`**: Remove a model from the available list

### 3. Chat Methods
- **`chat()`**: Standard completion that returns the full response
- **`chat_stream()`**: Streaming completion that yields chunks in real-time
- **Both methods support**:
  - Conversation history integration
  - System prompts
  - Custom parameters (temperature, max_tokens, etc.)

### 3. ConversationHistory Class
- **Purpose**: Manages multi-turn conversations
- **Key Features**:
  - Track user and assistant messages
  - Save/load conversations to/from JSON files
  - Clear conversation history
  - Seamless integration with chat methods

### 4. Error Handling System
- **Custom Exceptions**:
  - `OpenRouterError`: Base exception class
  - `RateLimitError`: For rate limit issues
  - `APIError`: For general API errors
- **Retry Logic**: Automatic retries with exponential backoff
- **Graceful Degradation**: Detailed error messages for debugging

## Workflow Logic

### 1. Initialization
```
1. Load API key from environment variable (OPENROUTER_API_KEY)
2. Initialize OpenRouterClient with model name
3. Configure retry settings (optional)
```

### 2. Standard Chat Flow
```
1. User calls client.chat(message)
2. System builds message array (system + history + user message)
3. Send request to OpenRouter API with retry logic
4. Parse response and return assistant message
5. Update conversation history (if provided)
```

### 3. Streaming Chat Flow
```
1. User calls client.chat_stream(message)
2. System builds message array (same as standard)
3. Send streaming request to OpenRouter API
4. Yield response chunks as they arrive
5. Collect full response for history update
6. Update conversation history (if provided)
```

### 4. Conversation Management
```
1. Create ConversationHistory object
2. Pass history to chat methods
3. System automatically adds user/assistant messages
4. Optional: Save/load conversations to files
```

## Module Structure

### File Organization
```
call_llm/
├── call_llm.py          # Main module with all classes
├── requirements.txt     # Python dependencies
├── env.example         # Environment variable template
└── README_project_briefing.md  # This documentation
```

### Class Hierarchy
```
OpenRouterError (Base Exception)
├── RateLimitError
└── APIError

ConversationHistory
├── add_message()
├── get_messages()
├── clear()
├── save()
└── load()

OpenRouterClient
├── __init__()
├── chat()
├── chat_stream()
├── _get_headers()
├── _handle_error()
└── _make_request()
```

## Current Status

### ✅ What's Working
- Complete OpenRouterClient implementation
- Standard chat completion with error handling
- Streaming chat with real-time responses
- Conversation history management
- Robust retry logic with exponential backoff
- Custom exception classes
- Environment variable configuration
- Support for all OpenRouter models (free and paid)

### 🔧 Configuration Required
- User needs to set OPENROUTER_API_KEY environment variable
- Copy env.example to .env and add actual API key
- Install dependencies: `pip install -r requirements.txt`

### 🎯 Ready for Use
- Module is production-ready
- Includes comprehensive error handling
- Supports all requested features
- Well-documented with examples

## Usage Examples

### Basic Setup
```python
from call_llm import OpenRouterClient

# Initialize with free model
client = OpenRouterClient(model="meta-llama/llama-4-maverick:free")

# Simple chat
response = client.chat("Hello, how are you?")
print(response)
```

### Streaming Response
```python
# Real-time streaming
for chunk in client.chat_stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Model Management
```python
# Initialize with available models for validation
available_models = [
    "meta-llama/llama-4-maverick:free",
    "qwen/qwen-2.5-vl-72b-instruct", 
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.3-8b-instruct:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-chat-v3.1:free",
    "google/gemma-3n-e4b-it:free"
]
client = OpenRouterClient(
    model="meta-llama/llama-4-maverick:free",
    available_models=available_models
)

# Switch between models dynamically
client.switch_model("qwen/qwen-2.5-vl-72b-instruct")
print(f"Current model: {client.get_current_model()}")

# List available models
print(f"Available: {client.list_available_models()}")
```

### Conversation with History
```python
from call_llm import ConversationHistory

history = ConversationHistory()
response1 = client.chat("What's the capital of France?", history=history)
response2 = client.chat("What's its population?", history=history)
```

### Advanced Usage
```python
# With system prompt and custom parameters
response = client.chat(
    "Write a poem",
    system_prompt="You are a creative poet",
    temperature=0.8,
    max_tokens=200
)
```

### Error Handling
```python
try:
    response = client.chat("Hello")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except APIError as e:
    print(f"API error: {e}")
except OpenRouterError as e:
    print(f"General error: {e}")
```

## Supported Models
- **Free Models**: meta-llama/llama-4-maverick:free, meta-llama/llama-3.2-3b-instruct:free
- **Paid Models**: qwen/qwen-2.5-vl-72b-instruct, meta-llama/llama-3.3-70b-instruct
- **Any OpenRouter Model**: Fully compatible with all models on OpenRouter.ai

## Next Steps
1. Set up environment variables
2. Install dependencies
3. Test with your preferred models
4. Integrate into your applications
5. Customize retry settings if needed
