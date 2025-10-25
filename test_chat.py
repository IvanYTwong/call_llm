"""
Test Chat Script for OpenRouter LLM Module

This script demonstrates how to use the call_llm module with streaming responses
and exports all responses to a markdown file.
"""

from call_llm import OpenRouterClient, ConversationHistory
from datetime import datetime

# Initialize markdown output
output_file = "chat_responses_v2.md"

def write_to_md(content, mode='a'):
    """Write content to the markdown file."""
    with open(output_file, mode, encoding='utf-8') as f:
        f.write(content)

def ask_question(client, question, history=None, model_name=None):
    """Helper to ask a question with streaming and save to markdown.
    
    Args:
        client: OpenRouterClient instance
        question: The question to ask
        history: Optional conversation history
        model_name: Optional model name for display
        
    Returns:
        The full response as a string
    """
    display_name = model_name or client.get_current_model()
    print(f"\n[{display_name}]")
    print("Response: ", end="", flush=True)
    
    full_response = ""
    for chunk in client.chat_stream(question, history=history):
        print(chunk, end="", flush=True)
        full_response += chunk
    print("\n")
    
    return full_response

def compare_models(client, question, models, question_title):
    """Ask the same question to multiple models and compare responses.
    
    Args:
        client: OpenRouterClient instance
        question: The question to ask all models
        models: List of model names to test
        question_title: Title for this comparison test
    """
    print(f"\n{'='*60}")
    print(f"=== {question_title} ===")
    print(f"{'='*60}")
    print(f"\nQuestion: {question}\n")
    
    write_to_md(f"## {question_title}\n\n")
    write_to_md(f"**Question:** {question}\n\n")
    write_to_md("---\n\n")
    
    responses = []
    
    for model in models:
        client.switch_model(model)
        model_short = model.split('/')[-1]  # Get short name
        
        write_to_md(f"### Model: `{model}`\n\n")
        write_to_md("**Response:**\n\n")
        
        response = ask_question(client, question, model_name=model_short)
        responses.append((model, response))
        
        write_to_md(f"{response}\n\n")
    
    return responses

def rate_response(response, criteria):
    """Simple heuristic rating based on response characteristics.
    
    Args:
        response: The response text to rate
        criteria: What to evaluate (length, structure, etc.)
        
    Returns:
        Score out of 10
    """
    score = 5.0  # Base score
    
    # Length check (not too short, not too verbose)
    word_count = len(response.split())
    if 50 <= word_count <= 300:
        score += 1.5
    elif word_count < 20:
        score -= 2
    elif word_count > 500:
        score -= 1
    
    # Structure check (has paragraphs or bullet points)
    if '\n\n' in response or '\n-' in response or '\n*' in response:
        score += 1.0
    
    # Example/explanation check
    if any(word in response.lower() for word in ['example', 'for instance', 'such as', '例如', '比如']):
        score += 1.0
    
    # Code check (if applicable)
    if '```' in response or 'def ' in response or 'function' in response:
        score += 0.5
    
    # Depth indicators
    if any(word in response.lower() for word in ['because', 'therefore', 'however', 'specifically', '因为', '所以', '然而']):
        score += 1.0
    
    return min(10.0, max(1.0, score))  # Clamp between 1-10

def main():
    # Initialize markdown file
    write_to_md(f"# OpenRouter LLM Test Chat Results\n\n", mode='w')
    write_to_md(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    write_to_md("---\n\n")
    
    try:
        # Models to compare
        test_models = [
            "meta-llama/llama-4-maverick:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "openai/gpt-oss-20b:free"
        ]
        
        # Initialize client
        client = OpenRouterClient(
            model=test_models[0],
            available_models=test_models
        )
        
        write_to_md("# Model Comparison Test\n\n")
        write_to_md(f"**Testing {len(test_models)} models with challenging questions**\n\n")
        write_to_md("**Models:**\n")
        for model in test_models:
            write_to_md(f"- `{model}`\n")
        write_to_md("\n---\n\n")
        
        # Test 1: AI Startup Strategy
        question1 = "You want to start an AI startup in 2025 with limited funding. What problem should you focus on, and what's your go-to-market strategy? Be specific about your target customer and competitive advantage."
        responses1 = compare_models(client, question1, test_models, "Test 1: AI Startup Strategy")
        
        write_to_md("**Ratings:**\n\n")
        for model, response in responses1:
            score = rate_response(response, "business")
            write_to_md(f"- `{model}`: **{score:.1f}/10**\n")
        write_to_md("\n---\n\n")
        
        # Test 2: Algorithmic Trading (Chinese)
        question2 = "解釋如何使用Python和機器學習來建立一個簡單的股票交易策略。需要考慮哪些關鍵因素和風險？請給出具體步驟。"
        responses2 = compare_models(client, question2, test_models, "Test 2: Algorithmic Trading Strategy")
        
        write_to_md("**Ratings:**\n\n")
        for model, response in responses2:
            score = rate_response(response, "technical")
            write_to_md(f"- `{model}`: **{score:.1f}/10**\n")
        write_to_md("\n---\n\n")
        
        # Test 3: AI Era Education (Chinese)
        question3 = "在AI時代，傳統教育需要如何改革？學生應該培養哪些技能才不會被AI取代？請提出3-5個具體建議。"
        responses3 = compare_models(client, question3, test_models, "Test 3: AI Era Education Reform")
        
        write_to_md("**Ratings:**\n\n")
        for model, response in responses3:
            score = rate_response(response, "education")
            write_to_md(f"- `{model}`: **{score:.1f}/10**\n")
        write_to_md("\n---\n\n")
        
        # Test 4: LLM API Selection
        question4 = "What are the 3 most important factors when choosing an LLM API (like OpenAI, Anthropic, or OpenRouter) for a production application? Explain briefly."
        responses4 = compare_models(client, question4, test_models, "Test 4: LLM API Selection")
        
        write_to_md("**Ratings:**\n\n")
        for model, response in responses4:
            score = rate_response(response, "logic")
            write_to_md(f"- `{model}`: **{score:.1f}/10**\n")
        write_to_md("\n---\n\n")
        
        # Calculate overall scores
        print("\n" + "="*60)
        print("=== OVERALL COMPARISON ===")
        print("="*60)
        
        write_to_md("## Overall Model Comparison\n\n")
        write_to_md("| Model | Test 1 | Test 2 | Test 3 | Test 4 | Average |\n")
        write_to_md("|-------|--------|--------|--------|--------|----------|\n")
        
        all_responses = [responses1, responses2, responses3, responses4]
        
        for i, model in enumerate(test_models):
            scores = []
            for responses in all_responses:
                response = responses[i][1]
                score = rate_response(response, "general")
                scores.append(score)
            
            avg_score = sum(scores) / len(scores)
            model_short = model.split('/')[-1]
            
            print(f"\n{model_short}:")
            print(f"  Test 1 (AI Startup): {scores[0]:.1f}/10")
            print(f"  Test 2 (Trading): {scores[1]:.1f}/10")
            print(f"  Test 3 (Education): {scores[2]:.1f}/10")
            print(f"  Test 4 (API Choice): {scores[3]:.1f}/10")
            print(f"  Average: {avg_score:.1f}/10")
            
            write_to_md(f"| `{model_short}` | {scores[0]:.1f} | {scores[1]:.1f} | {scores[2]:.1f} | {scores[3]:.1f} | **{avg_score:.1f}** |\n")
        
        write_to_md("\n---\n\n")
        write_to_md("## Notes\n\n")
        write_to_md("- Ratings are based on heuristic analysis (response length, structure, depth, examples, etc.)\n")
        write_to_md("- These scores are approximate and meant for quick comparison\n")
        write_to_md("- Human evaluation is recommended for final assessment\n\n")
        
        print("\n" + "="*60)
        print(f"✅ Test complete! Results saved to: {output_file}")
        print("="*60)
        
    except Exception as e:
        error_msg = f"\n## Error\n\n```\n{str(e)}\n```\n"
        print(f"Error: {e}")
        write_to_md(error_msg)
        print("\nMake sure to:")
        print("1. Set your OPENROUTER_API_KEY environment variable")
        print("2. Install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

