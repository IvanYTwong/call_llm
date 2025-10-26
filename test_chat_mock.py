#!/usr/bin/env python3
"""
Test Chat Script with Mock Evaluation System

This demonstrates the complete evaluation workflow using mock responses
and mock LLM-as-judge reasoning, without requiring a real API key.
"""

from mock_evaluator import MockModelEvaluator
from datetime import datetime

# Initialize markdown output
output_file = "chat_responses_mock.md"

def write_to_md(content, mode='a'):
    """Write content to the markdown file."""
    with open(output_file, mode, encoding='utf-8') as f:
        f.write(content)

def compare_models_mock(evaluator, question, models, question_title):
    """Ask the same question to multiple models and compare responses (mock version).
    
    Args:
        evaluator: MockModelEvaluator instance for scoring
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
    
    # Mock responses for different models
    mock_responses = {
        "llama-4-maverick": """Starting an AI startup in 2025 with limited funding requires focusing on a specific, high-value problem. I recommend targeting small businesses that need AI-powered customer service automation. The go-to-market strategy involves creating a simple chatbot that can handle common customer inquiries, reducing the need for human support staff. Target customers are small e-commerce businesses and local service providers who can't afford expensive enterprise solutions. The competitive advantage is offering a no-code solution that businesses can set up in minutes, with pricing starting at $29/month. This approach has low technical barriers, clear customer pain points, and a scalable business model.""",
        
        "qwen-2.5-72b": """For a 2025 AI startup with limited funding, focus on AI-powered content generation for small businesses. The problem: Small businesses struggle to create consistent, high-quality content for marketing. Go-to-market strategy: Offer a SaaS platform that generates blog posts, social media content, and email campaigns using AI. Target customers: Marketing agencies and small businesses (10-50 employees) with limited content creation resources. Competitive advantage: Industry-specific templates, multi-language support, and integration with popular tools like WordPress and Mailchimp. Pricing: $49/month for basic plan, $149/month for agencies. This addresses a clear pain point with measurable ROI for customers.""",
        
        "deepseek-r1": """In 2025, focus on AI-powered data analysis for small to medium businesses. The problem: Most SMBs have valuable data but lack the expertise to extract insights. Solution: Create an AI platform that automatically analyzes business data and provides actionable recommendations. Target customers: Retail stores, restaurants, and service businesses with 5-100 employees. Go-to-market: Start with a free tier offering basic analytics, then upsell advanced features. Competitive advantage: No technical knowledge required, works with existing business tools, and provides clear ROI through improved decision-making. Pricing: $99/month for basic analytics, $299/month for advanced insights. This market has high demand, clear value proposition, and recurring revenue potential.""",
        
        "gpt-oss-20b": """For a 2025 AI startup, I recommend focusing on AI-powered inventory management for small retailers. The problem: Small businesses lose money due to overstocking, understocking, and inefficient inventory tracking. Solution: AI system that predicts demand, optimizes stock levels, and automates reordering. Target customers: Independent retailers, small chains, and online sellers. Go-to-market: Partner with existing POS system providers for integration. Competitive advantage: Machine learning that improves with each business's data, reducing waste by 20-30%. Pricing: $79/month per location. This addresses a universal business problem with measurable cost savings, making it easy to sell and scale."""
    }
    
    responses = []
    
    for model in models:
        model_short = model.split('/')[-1] if '/' in model else model
        
        write_to_md(f"### Model: `{model}`\n\n")
        write_to_md("**Response:**\n\n")
        
        # Get mock response
        response = mock_responses.get(model_short, "No response available.")
        responses.append((model, response))
        
        print(f"[{model_short}]")
        print(f"Response: {response[:200]}...")
        print()
        
        write_to_md(f"{response}\n\n")
    
    return responses

def main():
    # Initialize markdown file
    write_to_md(f"# Mock Model Comparison Test Results\n\n", mode='w')
    write_to_md(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    write_to_md("---\n\n")
    
    try:
        # Models to compare
        test_models = [
            "llama-4-maverick",
            "qwen-2.5-72b", 
            "deepseek-r1",
            "gpt-oss-20b"
        ]
        
        # Initialize mock evaluator
        evaluator = MockModelEvaluator()
        
        write_to_md("# Mock Model Comparison Test\n\n")
        write_to_md(f"**Testing {len(test_models)} models with challenging questions**\n\n")
        write_to_md("**Models:**\n")
        for model in test_models:
            write_to_md(f"- `{model}`\n")
        write_to_md("\n---\n\n")
        
        # Test 1: AI Startup Strategy
        question1 = "You want to start an AI startup in 2025 with limited funding. What problem should you focus on, and what's your go-to-market strategy? Be specific about your target customer and competitive advantage."
        responses1 = compare_models_mock(evaluator, question1, test_models, "Test 1: AI Startup Strategy")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results1 = []
        for model, response in responses1:
            eval_result = evaluator.evaluate_response(model, question1, response)
            eval_results1.append(eval_result)
            
            model_short = model.split('/')[-1] if '/' in model else model
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
        
        # Test 2: Technical Problem Solving
        question2 = "How would you design a scalable system to process 1 million API requests per minute? Include architecture, technologies, and cost considerations."
        responses2 = compare_models_mock(evaluator, question2, test_models, "Test 2: System Design Challenge")
        
        # Evaluate responses with rubric scoring
        write_to_md("**Rubric Evaluation:**\n\n")
        eval_results2 = []
        for model, response in responses2:
            eval_result = evaluator.evaluate_response(model, question2, response)
            eval_results2.append(eval_result)
            
            model_short = model.split('/')[-1] if '/' in model else model
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
        write_to_md("| Model | Test 1 | Test 2 | Average |\n")
        write_to_md("|-------|--------|--------|----------|\n")
        
        all_eval_results = [eval_results1, eval_results2]
        
        for i, model in enumerate(test_models):
            scores = []
            for eval_results in all_eval_results:
                if i < len(eval_results):
                    score = eval_results[i].overall_score
                    scores.append(score)
                else:
                    scores.append(0.0)  # Fallback if missing results
            
            avg_score = sum(scores) / len(scores)
            model_short = model.split('/')[-1] if '/' in model else model
            
            print(f"\n{model_short}:")
            print(f"  Test 1 (Startup): {scores[0]:.2f}/5.0")
            print(f"  Test 2 (System Design): {scores[1]:.2f}/5.0")
            print(f"  Average: {avg_score:.2f}/5.0")
            
            write_to_md(f"| `{model_short}` | {scores[0]:.2f} | {scores[1]:.2f} | **{avg_score:.2f}** |\n")
        
        write_to_md("\n---\n\n")
        write_to_md("## Evaluation Notes\n\n")
        write_to_md("- **Scoring System:** Mock rubric-based evaluation system\n")
        write_to_md("- **Criteria:** Correctness(4), Completeness(3), Reasoning(2), Clarity(1), Verifiability(1)\n")
        write_to_md("- **Safety Gate:** Models must pass safety check or receive -1.0 score\n")
        write_to_md("- **Judge System:** Simulated LLM-as-judge with realistic reasoning\n")
        write_to_md("- **Scale:** 0-5 for individual criteria, weighted average for overall score\n\n")
        
        print("\n" + "="*60)
        print(f"✅ Mock test complete! Results saved to: {output_file}")
        print("="*60)
        
    except Exception as e:
        error_msg = f"\n## Error\n\n```\n{str(e)}\n```\n"
        print(f"Error: {e}")
        write_to_md(error_msg)

if __name__ == "__main__":
    main()

