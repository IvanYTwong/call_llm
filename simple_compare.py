#!/usr/bin/env python3
"""
Simple Model Comparison with Real LLM Judge

Quick test of the evaluation system with a single question.
"""

from call_llm import OpenRouterClient
from model_evaluator import ModelEvaluator
import time

def simple_model_comparison():
    """Run a simple model comparison with real LLM judge."""
    
    print("🔍 Simple Model Comparison with Real LLM Judge")
    print("=" * 60)
    
    # Test models
    test_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free", 
        "deepseek/deepseek-r1-distill-llama-70b:free"
    ]
    
    # Question for testing
    question = "Explain the difference between TCP and UDP protocols in simple terms. Give one real-world example for each."
    
    print(f"\n📝 Question: {question}\n")
    
    # Initialize clients
    client = OpenRouterClient(model=test_models[0], available_models=test_models)
    judge_client = OpenRouterClient(model="qwen/qwen-2.5-72b-instruct:free")
    evaluator = ModelEvaluator(judge_client)
    
    responses = []
    
    # Get responses from each model
    print("🤖 Getting responses from models...")
    print("-" * 40)
    
    for i, model in enumerate(test_models, 1):
        print(f"\n[{i}/3] Testing {model.split('/')[-1]}...")
        
        try:
            client.switch_model(model)
            response = client.chat(question, temperature=0.7, max_tokens=300)
            responses.append((model, response))
            
            print(f"✅ Response received ({len(response.split())} words)")
            print(f"Preview: {response[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            responses.append((model, f"Error: {e}"))
    
    # Evaluate responses with LLM judge
    print(f"\n⚖️  Evaluating responses with LLM judge...")
    print("-" * 40)
    
    eval_results = []
    
    for i, (model, response) in enumerate(responses, 1):
        if response.startswith("Error:"):
            print(f"\n[{i}/3] {model.split('/')[-1]}: Skipped (error)")
            continue
            
        print(f"\n[{i}/3] Evaluating {model.split('/')[-1]}...")
        
        try:
            eval_result = evaluator.evaluate_response(model, question, response)
            eval_results.append(eval_result)
            
            print(f"✅ Evaluation complete!")
            print(f"   Overall Score: {eval_result.overall_score:.2f}/5.0")
            print(f"   Correctness: {eval_result.rubric.correctness}/5")
            print(f"   Completeness: {eval_result.rubric.completeness}/5")
            print(f"   Reasoning: {eval_result.rubric.reasoning}/5")
            print(f"   Clarity: {eval_result.rubric.clarity}/5")
            print(f"   Verifiability: {eval_result.rubric.verifiability}/5")
            print(f"   Safety Pass: {eval_result.rubric.safety_pass}")
            print(f"   Judge Rationale: {eval_result.rubric.rationale}")
            
        except Exception as e:
            print(f"❌ Evaluation error: {e}")
    
    # Final ranking
    if eval_results:
        print(f"\n🏆 Final Rankings:")
        print("=" * 30)
        
        sorted_results = sorted(eval_results, key=lambda r: r.overall_score, reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            model_short = result.model_id.split('/')[-1]
            print(f"{i}. {model_short}: {result.overall_score:.2f}/5.0")
        
        print(f"\n📊 Total LLM Calls Made:")
        print(f"   - Response Generation: {len(responses)} calls")
        print(f"   - Judge Evaluations: {len(eval_results)} calls")
        print(f"   - Total: {len(responses) + len(eval_results)} calls")
        
    else:
        print("\n❌ No successful evaluations completed")
    
    print(f"\n✅ Comparison complete!")

if __name__ == "__main__":
    simple_model_comparison()

