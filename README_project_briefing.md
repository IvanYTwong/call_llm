# OpenRouter LLM Module

A production-ready Python module for OpenRouter.ai API with support for free models, streaming, conversation history, and robust error handling.

## Quick Start

```python
from call_llm import OpenRouterClient

# Initialize with free model
client = OpenRouterClient(model="meta-llama/llama-4-maverick:free")

# Simple chat
response = client.chat("Hello, how are you?")
print(response)

# Streaming response
for chunk in client.chat_stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

## Core Features

| Feature | Description |
|---------|-------------|
| **Model Management** | Switch between models dynamically with validation |
| **Streaming** | Real-time response streaming for better UX |
| **Conversation History** | Multi-turn conversations with save/load to JSON |
| **Error Handling** | Custom exceptions with retry logic |
| **Free Models** | Support for Llama, Qwen, DeepSeek, and more |

## API Reference

### OpenRouterClient

```python
client = OpenRouterClient(
    model="meta-llama/llama-4-maverick:free",
    available_models=["model1", "model2"],  # Optional validation
    max_retries=3,
    retry_delay=1.0
)
```

**Core Methods:**
- `chat(message, history=None, system_prompt=None, **kwargs)` → Complete response
- `chat_stream(message, history=None, system_prompt=None, **kwargs)` → Streaming generator
- `switch_model(new_model)` → Change active model
- `get_current_model()` → Get current model name
- `list_available_models()` → Get configured models
- `add_available_model(model)` → Add model to available list
- `remove_available_model(model)` → Remove model from list

### ConversationHistory

```python
from call_llm import ConversationHistory

history = ConversationHistory()
history.add_message("user", "Hello")
history.add_message("assistant", "Hi there!")
history.save("conversation.json")
history.load("conversation.json")
```

## Usage Examples

### Model Comparison Testing

```python
# Test multiple models with same question
models = [
    "meta-llama/llama-4-maverick:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free"
]

client = OpenRouterClient(model=models[0], available_models=models)

question = "Explain quantum computing in simple terms"
responses = []

for model in models:
    client.switch_model(model)
    response = client.chat(question)
    responses.append((model, response))
    print(f"{model}: {response[:100]}...")
```

### Conversation with History

```python
from call_llm import ConversationHistory

history = ConversationHistory()

# Multi-turn conversation
response1 = client.chat("What's the capital of France?", history=history)
response2 = client.chat("What's its population?", history=history)

# Save conversation
history.save("france_chat.json")

# Load and continue later
new_history = ConversationHistory()
new_history.load("france_chat.json")
response3 = client.chat("What language do they speak?", history=new_history)
```

### Advanced Configuration

```python
# With system prompt and custom parameters
response = client.chat(
    "Write a poem about coding",
    system_prompt="You are a creative poet who loves technology",
    temperature=0.8,
    max_tokens=200
)

# Streaming with error handling
try:
    for chunk in client.chat_stream("Explain machine learning"):
        print(chunk, end="", flush=True)
except RateLimitError:
    print("Rate limit exceeded, please wait")
except APIError as e:
    print(f"API error: {e}")
```

### Batch Testing Workflow

```python
def test_models_on_question(models, question):
    """Test multiple models on the same question."""
    results = []
    
    for model in models:
        client.switch_model(model)
        try:
            response = client.chat(question)
            results.append({
                'model': model,
                'response': response,
                'length': len(response.split())
            })
        except Exception as e:
            results.append({
                'model': model,
                'error': str(e)
            })
    
    return results

# Usage
models = ["meta-llama/llama-4-maverick:free", "qwen/qwen-2.5-72b-instruct:free"]
results = test_models_on_question(models, "How do neural networks work?")
```

## Error Handling

```python
from call_llm import OpenRouterError, RateLimitError, APIError

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

**Free Models:**
- `meta-llama/llama-4-maverick:free`
- `meta-llama/llama-3.2-3b-instruct:free`
- `qwen/qwen-2.5-72b-instruct:free`
- `deepseek/deepseek-r1-distill-llama-70b:free`
- `openai/gpt-oss-20b:free`
- And more...

**Paid Models:**
- `qwen/qwen-2.5-vl-72b-instruct`
- `meta-llama/llama-3.3-70b-instruct`
- Any OpenRouter.ai model

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set API key:**
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

3. **Copy environment template:**
```bash
cp env.example .env
# Edit .env with your API key
```

## Model Evaluation System

### Rubric-based Evaluation

The project now includes a comprehensive model evaluation system using LLM-as-judge:

```python
from model_evaluator import ModelEvaluator, RubricScore, EvalResult

# Initialize evaluator with judge client
judge_client = OpenRouterClient(model="qwen/qwen-2.5-72b-instruct:free")
evaluator = ModelEvaluator(judge_client)

# Evaluate a model response
result = evaluator.evaluate_response("model_name", prompt, response)
print(f"Overall Score: {result.overall_score:.2f}/5.0")
print(f"Correctness: {result.rubric.correctness}/5")
print(f"Judge Rationale: {result.rubric.rationale}")
```

**Evaluation Criteria:**
- **Correctness** (weight 4): Factual accuracy, absence of hallucinations
- **Completeness** (weight 3): Covers all parts of prompt, addresses edge cases
- **Reasoning** (weight 2): Quality of logical structure and justification
- **Clarity** (weight 1): Readable, well-organized, concise
- **Verifiability** (weight 1): Cites sources, provides reproducible steps
- **Safety Pass** (boolean gate): Must pass or receive -1.0 score

**Key Features:**
- LLM-as-judge using OpenRouter API with low temperature (0.1) for consistency
- JSON parsing with retry logic for malformed responses
- Blind judging (no model names revealed to judge)
- Weighted scoring system with safety gate
- Comprehensive rationale from judge

### Integration with test_chat.py

The evaluation system is fully integrated into the model comparison workflow:

```python
# Automatic evaluation during model testing
responses = compare_models(client, evaluator, question, models, "Test Title")

# Detailed rubric scores in markdown output
for model, response in responses:
    eval_result = evaluator.evaluate_response(model, question, response)
    # Results include all rubric scores + judge rationale
```

## Module Structure

```
call_llm/
├── call_llm.py              # Main OpenRouter API module
├── model_evaluator.py       # Rubric-based evaluation system
├── test_chat.py            # Model comparison with evaluation
├── requirements.txt        # Dependencies
├── env.example            # Environment template
└── README_project_briefing.md
```

**Classes:**
- `OpenRouterClient` - Main API client
- `ConversationHistory` - Chat history management
- `ModelEvaluator` - Rubric-based model evaluation
- `RubricScore` - Individual criterion scores
- `EvalResult` - Complete evaluation results
- `OpenRouterError` - Base exception
- `RateLimitError` - Rate limit exceptions
- `APIError` - General API exceptions

## Real-World Use Cases

- **Model Comparison**: Test different models on the same tasks
- **Chat Applications**: Build conversational interfaces
- **Content Generation**: Automated writing and coding assistance
- **Research**: Batch testing and evaluation workflows
- **Education**: Interactive learning tools with multiple AI models