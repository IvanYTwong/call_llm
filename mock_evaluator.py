#!/usr/bin/env python3
"""
Mock Model Evaluator - Demonstrates the evaluation system
without requiring a real API key.
"""

from model_evaluator import RubricScore, EvalResult
import random

class MockModelEvaluator:
    """Mock evaluator that simulates LLM-as-judge reasoning."""
    
    def __init__(self):
        self.evaluation_count = 0
    
    def evaluate_response(self, model_id: str, prompt: str, answer: str) -> EvalResult:
        """Simulate evaluation with realistic reasoning."""
        self.evaluation_count += 1
        
        # Analyze the response characteristics
        word_count = len(answer.split())
        has_examples = any(word in answer.lower() for word in ['example', 'for instance', 'such as', 'like'])
        has_technical_terms = any(word in answer.lower() for word in ['algorithm', 'function', 'method', 'process'])
        has_structure = '\n' in answer or '•' in answer or '-' in answer
        has_reasoning = any(word in answer.lower() for word in ['because', 'therefore', 'however', 'specifically'])
        
        # Simulate judge reasoning based on response characteristics
        if word_count < 50:
            correctness = 2
            completeness = 2
            reasoning = 2
            clarity = 3
            verifiability = 1
            rationale = "Response is too brief and lacks depth. Missing key concepts and explanations."
        elif word_count > 500:
            correctness = 4
            completeness = 5
            reasoning = 4
            clarity = 2
            verifiability = 3
            rationale = "Comprehensive response with good technical accuracy, but somewhat verbose and could be more concise."
        else:
            # Balanced response
            correctness = 4 if has_technical_terms else 3
            completeness = 4 if has_examples else 3
            reasoning = 4 if has_reasoning else 3
            clarity = 4 if has_structure else 3
            verifiability = 3 if has_examples else 2
            rationale = self._generate_rationale(answer, correctness, completeness, reasoning, clarity, verifiability)
        
        # Safety check (simulate)
        safety_pass = not any(word in answer.lower() for word in ['harmful', 'dangerous', 'illegal', 'unethical'])
        if not safety_pass:
            rationale += " Safety concerns detected in response."
        
        rubric = RubricScore(
            correctness=correctness,
            completeness=completeness,
            reasoning=reasoning,
            clarity=clarity,
            verifiability=verifiability,
            safety_pass=safety_pass,
            rationale=rationale
        )
        
        return EvalResult(
            model_id=model_id,
            rubric=rubric,
            overall_score=rubric.weighted_total()
        )
    
    def _generate_rationale(self, answer, correctness, completeness, reasoning, clarity, verifiability):
        """Generate realistic judge rationale."""
        rationales = []
        
        if correctness >= 4:
            rationales.append("Technically accurate with good factual content")
        elif correctness >= 3:
            rationales.append("Generally accurate with minor technical issues")
        else:
            rationales.append("Contains some inaccuracies or unclear technical details")
        
        if completeness >= 4:
            rationales.append("Covers the topic comprehensively")
        elif completeness >= 3:
            rationales.append("Addresses most aspects of the question")
        else:
            rationales.append("Missing some key points or incomplete coverage")
        
        if reasoning >= 4:
            rationales.append("Well-structured logical flow")
        elif reasoning >= 3:
            rationales.append("Reasonable organization with some gaps")
        else:
            rationales.append("Could benefit from better logical structure")
        
        if clarity >= 4:
            rationales.append("Clear and well-organized presentation")
        elif clarity >= 3:
            rationales.append("Generally readable with minor clarity issues")
        else:
            rationales.append("Could be more clearly written and organized")
        
        if verifiability >= 3:
            rationales.append("Includes some verifiable claims or examples")
        else:
            rationales.append("Limited verifiable information or examples")
        
        return ". ".join(rationales) + "."

def demo_mock_evaluation():
    """Run a complete mock evaluation demo."""
    
    print("🤖 Mock Model Evaluation Demo")
    print("=" * 50)
    
    # Sample responses for different models
    test_cases = [
        {
            "model": "llama-4-maverick",
            "question": "Explain machine learning in simple terms",
            "response": """Machine learning is like teaching a computer to recognize patterns, just like how you learn to recognize faces or understand speech. Instead of programming every rule, we give the computer lots of examples and let it figure out the patterns itself. For example, if you show it thousands of photos of cats and dogs, it can eventually learn to tell them apart. The computer gets better with more examples, just like how you get better at recognizing things with practice."""
        },
        {
            "model": "qwen-2.5-72b",
            "question": "Explain machine learning in simple terms", 
            "response": """Machine learning (ML) is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every scenario. It works by using algorithms to identify patterns in large datasets, then applying these patterns to make predictions or classifications on new data. Common applications include image recognition, natural language processing, and recommendation systems. The process typically involves training a model on historical data, validating its performance, and then deploying it to make predictions on new, unseen data."""
        },
        {
            "model": "deepseek-r1",
            "question": "Explain machine learning in simple terms",
            "response": """Machine learning is a method of data analysis that automates analytical model building. It's a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention. The key components include algorithms, training data, and model evaluation. Popular techniques include supervised learning (learning with labeled examples), unsupervised learning (finding hidden patterns), and reinforcement learning (learning through trial and error)."""
        }
    ]
    
    # Initialize mock evaluator
    evaluator = MockModelEvaluator()
    
    print(f"\n📊 Evaluating {len(test_cases)} model responses...")
    print("-" * 40)
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {case['model']}")
        print(f"Question: {case['question']}")
        print(f"Response: {case['response'][:100]}...")
        
        # Evaluate the response
        result = evaluator.evaluate_response(
            case['model'], 
            case['question'], 
            case['response']
        )
        
        results.append(result)
        
        # Display results
        print(f"\n📈 Evaluation Results:")
        print(f"   Overall Score: {result.overall_score:.2f}/5.0")
        print(f"   Correctness: {result.rubric.correctness}/5")
        print(f"   Completeness: {result.rubric.completeness}/5")
        print(f"   Reasoning: {result.rubric.reasoning}/5")
        print(f"   Clarity: {result.rubric.clarity}/5")
        print(f"   Verifiability: {result.rubric.verifiability}/5")
        print(f"   Safety Pass: {result.rubric.safety_pass}")
        print(f"   Judge Rationale: {result.rubric.rationale}")
    
    # Overall ranking
    print("\n" + "=" * 50)
    print("🏆 Final Rankings:")
    print("-" * 20)
    
    sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result.model_id}: {result.overall_score:.2f}/5.0")
    
    print(f"\n📊 Total Evaluations: {evaluator.evaluation_count}")
    print("✅ Mock evaluation complete!")

if __name__ == "__main__":
    demo_mock_evaluation()
