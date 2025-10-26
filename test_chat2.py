#!/usr/bin/env python3
"""
Interactive Model Comparison Tool

A simple command-line tool for comparing LLM responses to a custom question.
User can input their own question, select models, and view side-by-side responses.
"""

from call_llm import OpenRouterClient
from datetime import datetime
import os
import sys

def get_user_question() -> str:
    """Get question from code or prompt user."""
    print("\n" + "="*50)
    print("🤖 Interactive Model Comparison")
    print("="*50)
    
    # ==========================================
    # WRITE YOUR QUESTION HERE:
    # ==========================================
    CUSTOM_QUESTION = """
    一個朋友會來香港玩2天，你介紹行程給我們，最好可以有景點，餐廳，住宿，交通，費用等資料，俱体一点
    """
    # ==========================================
    
    # Check if custom question is set
    if CUSTOM_QUESTION.strip():
        print(f"\nUsing custom question from code:")
        print(f"Question: {CUSTOM_QUESTION.strip()}")
        return CUSTOM_QUESTION.strip()
    
    # Fallback to interactive input
    print("\nEnter your question (or press Enter for sample questions):")
    question = input("> ").strip()
    
    if not question:
        print("\nSample questions:")
        samples = [
            "1. What is quantum computing?",
            #"2. How does machine learning work?",
            #"3. Explain blockchain technology",
            #"4. What are the benefits of renewable energy?",
            #"5. How to start a successful business?"
        ]
        for sample in samples:
            print(f"   {sample}")
        
        choice = input("\nSelect a sample (1-5) or enter your own question: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            sample_questions = [
                "What is quantum computing and how does it differ from classical computing?",
                #"How does machine learning work and what are its main applications?",
                #"Explain blockchain technology and its potential uses beyond cryptocurrency.",
                #"What are the main benefits and challenges of renewable energy sources?",
                #"What are the key steps to starting a successful business in 2025?"
            ]
            question = sample_questions[int(choice) - 1]
        else:
            question = choice
    
    return question

def display_available_models() -> list:
    """Show model list, return user selection."""
    print(f"\nAvailable models:")
    
    models = [
        "meta-llama/llama-4-maverick:free",
        "deepseek/deepseek-r1-distill-llama-70b:free", 
        "qwen/qwen-2.5-72b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "openai/gpt-oss-20b:free"
    ]
    
    for i, model in enumerate(models, 1):
        model_short = model.split('/')[-1]
        print(f"{i}. {model_short}")
    
    # ==========================================
    # SELECT YOUR MODELS HERE (or leave empty for all):
    # ==========================================
    SELECTED_MODEL_INDICES = [3]  # Skip llama-4-maverick (moderation issues), use others
    # SELECTED_MODEL_INDICES = [1, 3, 5]  # Or specify which ones you want
    # SELECTED_MODEL_INDICES = []  # Empty = use all models
    # ==========================================
    
    if SELECTED_MODEL_INDICES:
        # Use predefined selection
        selected_models = [models[i-1] for i in SELECTED_MODEL_INDICES if 1 <= i <= len(models)]
        print(f"\nUsing predefined model selection from code:")
    else:
        # Use all models
        selected_models = models
        print(f"\nUsing all available models:")
    
    for i, model in enumerate(selected_models, 1):
        model_short = model.split('/')[-1]
        print(f"  {i}. {model_short}")
    
    return selected_models

def get_responses(client, models, question) -> list:
    """Query all models and collect responses."""
    print(f"\nGetting responses...")
    print("-" * 30)
    
    responses = []
    
    for i, model in enumerate(models, 1):
        model_short = model.split('/')[-1]
        print(f"[{i}/{len(models)}] Getting response from {model_short}...", end=" ", flush=True)
        
        try:
            client.switch_model(model)
            response = client.chat(question, temperature=0.7, max_tokens=800)
            word_count = len(response.split())
            
            responses.append({
                'model': model,
                'model_short': model_short,
                'response': response,
                'word_count': word_count
            })
            
            print(f"✓ ({word_count} words)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}...")
            responses.append({
                'model': model,
                'model_short': model_short,
                'response': f"Error: {str(e)}",
                'word_count': 0
            })
    
    return responses

def display_responses(question, responses):
    """Print responses side-by-side in terminal."""
    print(f"\n" + "="*60)
    print("RESPONSES")
    print("="*60)
    print(f"Question: {question}")
    print("="*60)
    
    for i, resp in enumerate(responses, 1):
        print(f"\n[Model {i}: {resp['model_short']}]")
        print("-" * 50)
        print(resp['response'])
        print(f"\nWord count: {resp['word_count']}")
        print("-" * 50)

def save_to_markdown(question, responses, filename):
    """Export results to markdown file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Model Comparison Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Question:** {question}\n\n")
        f.write("---\n\n")
        
        for i, resp in enumerate(responses, 1):
            f.write(f"## Model {i}: {resp['model_short']}\n\n")
            f.write(f"**Word Count:** {resp['word_count']}\n\n")
            f.write("**Response:**\n\n")
            f.write(f"{resp['response']}\n\n")
            f.write("---\n\n")
    
    print(f"✓ Saved to: {filename}")

def main():
    """Main interactive flow."""
    try:
        # Get user question
        question = get_user_question()
        if not question:
            print("No question provided. Exiting.")
            return
        
        # Get model selection
        selected_models = display_available_models()
        
        # Initialize client
        print(f"\nInitializing OpenRouter client...")
        client = OpenRouterClient(
            model=selected_models[0],
            available_models=selected_models
        )
        
        # Get responses
        responses = get_responses(client, selected_models, question)
        
        # Display responses
        display_responses(question, responses)
        
        # Auto-save results
        print(f"\n" + "="*60)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"comparison_{timestamp}.md"
        save_to_markdown(question, responses, filename)
        
        print(f"\n✅ Done!")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure your OPENROUTER_API_KEY is set correctly.")

if __name__ == "__main__":
    main()
