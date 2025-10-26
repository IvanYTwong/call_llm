#!/usr/bin/env python3
"""
Demo of the Model Evaluation System

This script demonstrates the rubric-based evaluation system
with mock data to show the reasoning and scoring process.
"""

from model_evaluator import ModelEvaluator, RubricScore, EvalResult
from call_llm import OpenRouterClient
import json

def demo_evaluation_system():
    """Demonstrate the evaluation system with mock data."""
    
    print("🔍 Model Evaluation System Demo")
    print("=" * 50)
    
    # Mock responses for demonstration
    mock_responses = [
        {
            "model": "llama-4-maverick",
            "question": "Explain quantum computing in simple terms",
            "response": """Quantum computing is like having a computer that can be in multiple states at once, unlike regular computers that are either 0 or 1. Think of it like a spinning coin - while it's spinning, it's both heads and tails simultaneously. This allows quantum computers to process many possibilities at once, making them incredibly powerful for certain problems like cryptography and drug discovery. However, they're very sensitive to interference and currently only work in specialized environments."""
        },
        {
            "model": "qwen-2.5-72b", 
            "question": "Explain quantum computing in simple terms",
            "response": """Quantum computing uses quantum mechanical phenomena like superposition and entanglement to process information. Unlike classical bits that are either 0 or 1, quantum bits (qubits) can exist in superposition - being both 0 and 1 simultaneously. This allows quantum computers to explore many solutions in parallel, potentially solving certain problems exponentially faster than classical computers. Applications include cryptography, optimization, and scientific simulations."""
        },
        {
            "model": "deepseek-r1",
            "question": "Explain quantum computing in simple terms", 
            "response": """Quantum computing is a revolutionary technology that harnesses quantum mechanical principles to perform calculations. The key difference from traditional computers is the use of quantum bits (qubits) that can exist in multiple states simultaneously through superposition. This enables quantum computers to process vast amounts of data in parallel, offering exponential speedups for specific algorithms. While promising, quantum computers face challenges like quantum decoherence and require extremely low temperatures to operate."""
        }
    ]
    
    print("\n📊 Mock Evaluation Results:")
    print("-" * 30)
    
    # Simulate rubric evaluation results
    mock_evaluations = [
        {
            "model": "llama-4-maverick",
            "scores": {
                "correctness": 4,
                "completeness": 5, 
                "reasoning": 4,
                "clarity": 5,
                "verifiability": 3,
                "safety_pass": True,
                "overall": 4.2
            },
            "rationale": "Excellent explanation with clear analogies (spinning coin). Covers key concepts well with good examples. Slightly lacks specific technical details but very accessible."
        },
        {
            "model": "qwen-2.5-72b",
            "scores": {
                "correctness": 5,
                "completeness": 4,
                "reasoning": 5, 
                "clarity": 4,
                "verifiability": 4,
                "safety_pass": True,
                "overall": 4.6
            },
            "rationale": "Highly accurate technical explanation with proper terminology. Well-structured reasoning but slightly more technical than needed for 'simple terms'. Good coverage of applications."
        },
        {
            "model": "deepseek-r1", 
            "scores": {
                "correctness": 5,
                "completeness": 4,
                "reasoning": 4,
                "clarity": 3,
                "verifiability": 3,
                "safety_pass": True,
                "overall": 4.1
            },
            "rationale": "Technically accurate and comprehensive. Covers key concepts and challenges well. However, language is quite technical for 'simple terms' request. Good scientific accuracy."
        }
    ]
    
    # Display evaluation results
    for eval_result in mock_evaluations:
        print(f"\n🤖 Model: {eval_result['model']}")
        print(f"   Overall Score: {eval_result['scores']['overall']:.1f}/5.0")
        print(f"   Correctness: {eval_result['scores']['correctness']}/5")
        print(f"   Completeness: {eval_result['scores']['completeness']}/5") 
        print(f"   Reasoning: {eval_result['scores']['reasoning']}/5")
        print(f"   Clarity: {eval_result['scores']['clarity']}/5")
        print(f"   Verifiability: {eval_result['scores']['verifiability']}/5")
        print(f"   Safety Pass: {eval_result['scores']['safety_pass']}")
        print(f"   Judge Rationale: {eval_result['rationale']}")
    
    print("\n" + "=" * 50)
    print("📈 Ranking Summary:")
    print("-" * 20)
    
    # Sort by overall score
    ranked_results = sorted(mock_evaluations, key=lambda x: x['scores']['overall'], reverse=True)
    
    for i, result in enumerate(ranked_results, 1):
        print(f"{i}. {result['model']}: {result['scores']['overall']:.1f}/5.0")
    
    print("\n" + "=" * 50)
    print("🔧 How the LLM Judge Works:")
    print("-" * 30)
    print("1. Judge receives question + response (blind evaluation)")
    print("2. Judge evaluates on 6 criteria using 0-5 scale")
    print("3. Weighted scoring: Correctness(4), Completeness(3), Reasoning(2), Clarity(1), Verifiability(1)")
    print("4. Safety gate: Must pass or get -1.0 score")
    print("5. Judge provides detailed rationale for scores")
    print("6. System calculates weighted overall score")
    
    print("\n" + "=" * 50)
    print("💡 Key Features Demonstrated:")
    print("-" * 35)
    print("✅ Blind evaluation (no model names revealed to judge)")
    print("✅ Structured rubric with weighted criteria") 
    print("✅ Safety gate for content filtering")
    print("✅ Detailed judge rationale for transparency")
    print("✅ Consistent scoring with low temperature (0.1)")
    print("✅ JSON parsing with retry logic for reliability")
    
    print("\n" + "=" * 50)
    print("🚀 Ready for Production Use!")
    print("The system provides comprehensive, unbiased model evaluation")
    print("with detailed reasoning for each score decision.")

if __name__ == "__main__":
    demo_evaluation_system()

