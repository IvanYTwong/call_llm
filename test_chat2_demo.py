#!/usr/bin/env python3
"""
Demo of test_chat2.py functionality
"""

from call_llm import OpenRouterClient
from datetime import datetime

def demo_comparison():
    """Demo the comparison functionality."""
    
    # Sample question
    question = "What is quantum computing?"
    
    # Sample models
    models = [
        "meta-llama/llama-4-maverick:free",
        "qwen/qwen-2.5-72b-instruct:free"
    ]
    
    print("🤖 Interactive Model Comparison Demo")
    print("="*50)
    print(f"Question: {question}")
    print(f"Models: {[m.split('/')[-1] for m in models]}")
    print("="*50)
    
    # Initialize client
    client = OpenRouterClient(model=models[0], available_models=models)
    
    # Get responses
    print("\nGetting responses...")
    responses = []
    
    for i, model in enumerate(models, 1):
        model_short = model.split('/')[-1]
        print(f"[{i}/{len(models)}] Getting response from {model_short}...", end=" ", flush=True)
        
        try:
            client.switch_model(model)
            response = client.chat(question, temperature=0.7, max_tokens=300)
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
    
    # Display responses
    print(f"\n" + "="*60)
    print("RESPONSES")
    print("="*60)
    
    for i, resp in enumerate(responses, 1):
        print(f"\n[Model {i}: {resp['model_short']}]")
        print("-" * 50)
        print(resp['response'])
        print(f"\nWord count: {resp['word_count']}")
        print("-" * 50)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"demo_comparison_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Model Comparison Demo\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Question:** {question}\n\n")
        f.write("---\n\n")
        
        for i, resp in enumerate(responses, 1):
            f.write(f"## Model {i}: {resp['model_short']}\n\n")
            f.write(f"**Word Count:** {resp['word_count']}\n\n")
            f.write("**Response:**\n\n")
            f.write(f"{resp['response']}\n\n")
            f.write("---\n\n")
    
    print(f"\n✅ Demo complete! Saved to: {filename}")

if __name__ == "__main__":
    demo_comparison()

