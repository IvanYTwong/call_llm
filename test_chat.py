"""
Test Chat Script for OpenRouter LLM Module

This script demonstrates how to use the call_llm module with streaming responses
and exports all responses to a markdown file.
"""

from call_llm import OpenRouterClient, ConversationHistory
from model_evaluator import ModelEvaluator, EvalResult
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

def compare_models(client, evaluator, question, models, question_title):
    """Ask the same question to multiple models and compare responses.
    
    Args:
        client: OpenRouterClient instance
        evaluator: ModelEvaluator instance for scoring
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
        try:
            client.switch_model(model)
            model_short = model.split('/')[-1]  # Get short name
            
            write_to_md(f"### Model: `{model}`\n\n")
            write_to_md("**Response:**\n\n")
            
            response = ask_question(client, question, model_name=model_short)
            responses.append((model, response))
            
            write_to_md(f"{response}\n\n")
            
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
            write_to_md(f"### Model: `{model}`\n\n")
            write_to_md(f"**Error:** {str(e)}\n\n")
            # Continue with other models
            continue
    
    return responses


def main():
    # Initialize markdown file
    write_to_md(f"# OpenRouter LLM Test Chat Results\n\n", mode='w')
    write_to_md(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    write_to_md("---\n\n")
    
    try:
        # Models to compare (skipped gpt-oss-20b:free due to streaming issues)
        test_models = [
            "meta-llama/llama-4-maverick:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
            "qwen/qwen-2.5-72b-instruct:free"
        ]
        
        # Initialize client for testing models
        client = OpenRouterClient(
            model=test_models[0],
            available_models=test_models
        )
        
        # Initialize judge client for evaluation (use a strong model for judging)
        judge_client = OpenRouterClient(
            model="qwen/qwen-2.5-72b-instruct:free",
            available_models=["qwen/qwen-2.5-72b-instruct:free"]
        )
        
        # Initialize model evaluator
        evaluator = ModelEvaluator(judge_client)
        
        write_to_md("# Model Comparison Test\n\n")
        write_to_md(f"**Testing {len(test_models)} models with challenging questions**\n\n")
        write_to_md("**Models:**\n")
        for model in test_models:
            write_to_md(f"- `{model}`\n")
        write_to_md("\n---\n\n")
        
        # Test 1: AI Startup Strategy
        question1 = "You want to start an AI startup in 2025 with limited funding. What problem should you focus on, and what's your go-to-market strategy? Be specific about your target customer and competitive advantage."
        responses1 = compare_models(client, evaluator, question1, test_models, "Test 1: AI Startup Strategy")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results1 = []
        for model, response in responses1:
            eval_result = evaluator.evaluate_response(model, question1, response)
            eval_results1.append(eval_result)
            
            model_short = model.split('/')[-1]
            write_to_md(f"**{model_short}:**\n")
            write_to_md(f"- Overall Score: **{eval_result.overall_score:.2f}/5.0**\n")
            write_to_md(f"- Correctness: {eval_result.rubric.correctness}/5\n")
            write_to_md(f"- Completeness: {eval_result.rubric.completeness}/5\n")
            write_to_md(f"- Reasoning: {eval_result.rubric.reasoning}/5\n")
            write_to_md(f"- Clarity: {eval_result.rubric.clarity}/5\n")
            write_to_md(f"- Verifiability: {eval_result.rubric.verifiability}/5\n")
            write_to_md(f"- Safety Pass: {eval_result.rubric.safety_pass}\n")
            write_to_md(f"- Judge Rationale: {eval_result.rubric.rationale}\n\n")
        write_to_md("---\n\n")
        
        # Test 2: Algorithmic Trading (Chinese)
        question2 = "解釋如何使用Python和機器學習來建立一個簡單的股票交易策略。需要考慮哪些關鍵因素和風險？請給出具體步驟。"
        responses2 = compare_models(client, evaluator, question2, test_models, "Test 2: Algorithmic Trading Strategy")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results2 = []
        for model, response in responses2:
            eval_result = evaluator.evaluate_response(model, question2, response)
            eval_results2.append(eval_result)
            
            model_short = model.split('/')[-1]
            write_to_md(f"**{model_short}:**\n")
            write_to_md(f"- Overall Score: **{eval_result.overall_score:.2f}/5.0**\n")
            write_to_md(f"- Correctness: {eval_result.rubric.correctness}/5\n")
            write_to_md(f"- Completeness: {eval_result.rubric.completeness}/5\n")
            write_to_md(f"- Reasoning: {eval_result.rubric.reasoning}/5\n")
            write_to_md(f"- Clarity: {eval_result.rubric.clarity}/5\n")
            write_to_md(f"- Verifiability: {eval_result.rubric.verifiability}/5\n")
            write_to_md(f"- Safety Pass: {eval_result.rubric.safety_pass}\n")
            write_to_md(f"- Judge Rationale: {eval_result.rubric.rationale}\n\n")
        write_to_md("---\n\n")
        
        # Test 3: AI Era Education (Chinese)
        question3 = "在AI時代，傳統教育需要如何改革？學生應該培養哪些技能才不會被AI取代？請提出3-5個具體建議。"
        responses3 = compare_models(client, evaluator, question3, test_models, "Test 3: AI Era Education Reform")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results3 = []
        for model, response in responses3:
            eval_result = evaluator.evaluate_response(model, question3, response)
            eval_results3.append(eval_result)
            
            model_short = model.split('/')[-1]
            write_to_md(f"**{model_short}:**\n")
            write_to_md(f"- Overall Score: **{eval_result.overall_score:.2f}/5.0**\n")
            write_to_md(f"- Correctness: {eval_result.rubric.correctness}/5\n")
            write_to_md(f"- Completeness: {eval_result.rubric.completeness}/5\n")
            write_to_md(f"- Reasoning: {eval_result.rubric.reasoning}/5\n")
            write_to_md(f"- Clarity: {eval_result.rubric.clarity}/5\n")
            write_to_md(f"- Verifiability: {eval_result.rubric.verifiability}/5\n")
            write_to_md(f"- Safety Pass: {eval_result.rubric.safety_pass}\n")
            write_to_md(f"- Judge Rationale: {eval_result.rubric.rationale}\n\n")
        write_to_md("---\n\n")
        
        # Test 4: LLM API Selection
        question4 = "What are the 3 most important factors when choosing an LLM API (like OpenAI, Anthropic, or OpenRouter) for a production application? Explain briefly."
        responses4 = compare_models(client, evaluator, question4, test_models, "Test 4: LLM API Selection")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results4 = []
        for model, response in responses4:
            eval_result = evaluator.evaluate_response(model, question4, response)
            eval_results4.append(eval_result)
            
            model_short = model.split('/')[-1]
            write_to_md(f"**{model_short}:**\n")
            write_to_md(f"- Overall Score: **{eval_result.overall_score:.2f}/5.0**\n")
            write_to_md(f"- Correctness: {eval_result.rubric.correctness}/5\n")
            write_to_md(f"- Completeness: {eval_result.rubric.completeness}/5\n")
            write_to_md(f"- Reasoning: {eval_result.rubric.reasoning}/5\n")
            write_to_md(f"- Clarity: {eval_result.rubric.clarity}/5\n")
            write_to_md(f"- Verifiability: {eval_result.rubric.verifiability}/5\n")
            write_to_md(f"- Safety Pass: {eval_result.rubric.safety_pass}\n")
            write_to_md(f"- Judge Rationale: {eval_result.rubric.rationale}\n\n")
        write_to_md("---\n\n")
        
        # Calculate overall scores using rubric evaluation
        print("\n" + "="*60)
        print("=== OVERALL COMPARISON ===")
        print("="*60)
        
        write_to_md("## Overall Model Comparison (Rubric-based)\n\n")
        write_to_md("| Model | Test 1 | Test 2 | Test 3 | Test 4 | Average |\n")
        write_to_md("|-------|--------|--------|--------|--------|----------|\n")
        
        all_eval_results = [eval_results1, eval_results2, eval_results3, eval_results4]
        
        for i, model in enumerate(test_models):
            scores = []
            for eval_results in all_eval_results:
                if i < len(eval_results):
                    score = eval_results[i].overall_score
                    scores.append(score)
                else:
                    scores.append(0.0)  # Fallback if missing results
            
            avg_score = sum(scores) / len(scores)
            model_short = model.split('/')[-1]
            
            print(f"\n{model_short}:")
            print(f"  Test 1 (AI Startup): {scores[0]:.2f}/5.0")
            print(f"  Test 2 (Trading): {scores[1]:.2f}/5.0")
            print(f"  Test 3 (Education): {scores[2]:.2f}/5.0")
            print(f"  Test 4 (API Choice): {scores[3]:.2f}/5.0")
            print(f"  Average: {avg_score:.2f}/5.0")
            
            write_to_md(f"| `{model_short}` | {scores[0]:.2f} | {scores[1]:.2f} | {scores[2]:.2f} | {scores[3]:.2f} | **{avg_score:.2f}** |\n")
        
        write_to_md("\n---\n\n")
        write_to_md("## Evaluation Notes\n\n")
        write_to_md("- **Scoring System:** Rubric-based evaluation using LLM-as-judge\n")
        write_to_md("- **Criteria:** Correctness(4), Completeness(3), Reasoning(2), Clarity(1), Verifiability(1)\n")
        write_to_md("- **Safety Gate:** Models must pass safety check or receive -1.0 score\n")
        write_to_md("- **Judge Model:** qwen-2.5-72b-instruct (temperature=0.1 for consistency)\n")
        write_to_md("- **Scale:** 0-5 for individual criteria, weighted average for overall score\n\n")
        
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

