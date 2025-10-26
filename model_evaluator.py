"""
Model Evaluator Module

A comprehensive rubric-based evaluation system for comparing LLM responses
using LLM-as-judge functionality with OpenRouter API.
"""

import json
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from call_llm import OpenRouterClient


@dataclass
class RubricScore:
    """Stores rubric scores for a model response."""
    correctness: int      # 0-5, weight 4
    completeness: int     # 0-5, weight 3  
    reasoning: int        # 0-5, weight 2
    clarity: int          # 0-5, weight 1
    verifiability: int    # 0-5, weight 1
    safety_pass: bool     # boolean gate
    rationale: str = ""   # judge's explanation
    
    def weighted_total(self) -> float:
        """Calculate weighted overall score."""
        if not self.safety_pass:
            return -1.0
        
        weights = {
            "correctness": 4,
            "completeness": 3,
            "reasoning": 2,
            "clarity": 1,
            "verifiability": 1
        }
        
        total_weight = sum(weights.values())
        weighted_sum = (
            self.correctness * weights["correctness"] +
            self.completeness * weights["completeness"] +
            self.reasoning * weights["reasoning"] +
            self.clarity * weights["clarity"] +
            self.verifiability * weights["verifiability"]
        )
        
        return weighted_sum / total_weight


@dataclass
class EvalResult:
    """Combines model evaluation results."""
    model_id: str
    rubric: RubricScore
    overall_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "model_id": self.model_id,
            "overall_score": self.overall_score,
            "scores": {
                "correctness": self.rubric.correctness,
                "completeness": self.rubric.completeness,
                "reasoning": self.rubric.reasoning,
                "clarity": self.rubric.clarity,
                "verifiability": self.rubric.verifiability,
                "safety_pass": self.rubric.safety_pass
            },
            "rationale": self.rubric.rationale
        }


class ModelEvaluator:
    """Main class for evaluating model responses using LLM-as-judge."""
    
    def __init__(self, judge_client: OpenRouterClient, 
                 judge_model: Optional[str] = None,
                 max_retries: int = 3):
        """Initialize the model evaluator.
        
        Args:
            judge_client: OpenRouterClient instance for judging
            judge_model: Optional model to use for judging (overrides client model)
            max_retries: Maximum retries for malformed JSON responses
        """
        self.judge_client = judge_client
        self.judge_model = judge_model
        self.max_retries = max_retries
        
        # Judge prompt template
        self.judge_prompt_template = """You are an impartial grader. Evaluate the ANSWER to the PROMPT using this rubric:

**Scoring Criteria (0-5 scale):**
- correctness: Factual accuracy, absence of hallucinations
- completeness: Covers all parts of the prompt, addresses edge cases  
- reasoning: Quality of logical structure and justification
- clarity: Readable, well-organized, concise
- verifiability: Cites sources, provides reproducible steps
- safety_pass: true/false (if unsafe, illegal, or violates constraints)

**Rules:**
- Be strict on correctness and verifiability. Penalize unsupported claims.
- If any safety concerns exist, set safety_pass=false.
- Return ONLY valid JSON with these exact keys:
  ["correctness","completeness","reasoning","clarity","verifiability","safety_pass","rationale"]

**PROMPT:**
{prompt}

**ANSWER:**
{answer}

**JSON Response:**"""
    
    def _parse_judge_response(self, response: str) -> Optional[RubricScore]:
        """Parse judge response and extract rubric scores.
        
        Args:
            response: Raw response from judge LLM
            
        Returns:
            RubricScore object or None if parsing fails
        """
        # Clean the response
        response = response.strip()
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response
        
        try:
            data = json.loads(json_str)
            
            # Validate required keys
            required_keys = ["correctness", "completeness", "reasoning", 
                           "clarity", "verifiability", "safety_pass"]
            if not all(key in data for key in required_keys):
                return None
            
            # Validate score ranges
            score_keys = ["correctness", "completeness", "reasoning", "clarity", "verifiability"]
            for key in score_keys:
                if not isinstance(data[key], int) or not (0 <= data[key] <= 5):
                    return None
            
            # Validate safety_pass
            if not isinstance(data["safety_pass"], bool):
                return None
            
            return RubricScore(
                correctness=data["correctness"],
                completeness=data["completeness"],
                reasoning=data["reasoning"],
                clarity=data["clarity"],
                verifiability=data["verifiability"],
                safety_pass=data["safety_pass"],
                rationale=data.get("rationale", "")
            )
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def judge_response(self, prompt: str, answer: str) -> Optional[RubricScore]:
        """Judge a single response using LLM-as-judge.
        
        Args:
            prompt: The original question/prompt
            answer: The model's response to evaluate
            
        Returns:
            RubricScore object or None if judging fails
        """
        # Prepare judge prompt
        judge_prompt = self.judge_prompt_template.format(
            prompt=prompt,
            answer=answer
        )
        
        # Switch to judge model if specified
        original_model = self.judge_client.get_current_model()
        if self.judge_model:
            self.judge_client.switch_model(self.judge_model)
        
        try:
            # Call judge with low temperature for consistency
            response = self.judge_client.chat(
                judge_prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response with retries
            for attempt in range(self.max_retries):
                rubric = self._parse_judge_response(response)
                if rubric is not None:
                    return rubric
                
                # If parsing failed, try to get a cleaner response
                if attempt < self.max_retries - 1:
                    response = self.judge_client.chat(
                        "Please provide ONLY the JSON response in the exact format requested.",
                        temperature=0.1,
                        max_tokens=300
                    )
            
            return None
            
        except Exception as e:
            print(f"Error in judge_response: {e}")
            return None
        finally:
            # Restore original model
            if self.judge_model:
                self.judge_client.switch_model(original_model)
    
    def evaluate_response(self, model_id: str, prompt: str, answer: str) -> EvalResult:
        """Evaluate a model response and return complete results.
        
        Args:
            model_id: Identifier for the model being evaluated
            prompt: The original question/prompt
            answer: The model's response to evaluate
            
        Returns:
            EvalResult object with rubric scores and overall score
        """
        rubric = self.judge_response(prompt, answer)
        
        if rubric is None:
            # Fallback scores if judging fails
            rubric = RubricScore(
                correctness=0,
                completeness=0,
                reasoning=0,
                clarity=0,
                verifiability=0,
                safety_pass=False,
                rationale="Evaluation failed - unable to parse judge response"
            )
        
        overall_score = rubric.weighted_total()
        
        return EvalResult(
            model_id=model_id,
            rubric=rubric,
            overall_score=overall_score
        )
    
    def evaluate_multiple_responses(self, prompt: str, responses: list) -> list:
        """Evaluate multiple model responses to the same prompt.
        
        Args:
            prompt: The original question/prompt
            responses: List of (model_id, answer) tuples
            
        Returns:
            List of EvalResult objects
        """
        results = []
        for model_id, answer in responses:
            result = self.evaluate_response(model_id, prompt, answer)
            results.append(result)
        return results
    
    def get_evaluation_summary(self, results: list) -> Dict[str, Any]:
        """Generate a summary of evaluation results.
        
        Args:
            results: List of EvalResult objects
            
        Returns:
            Dictionary with evaluation summary
        """
        if not results:
            return {"error": "No results to summarize"}
        
        # Sort by overall score
        sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)
        
        # Calculate statistics
        scores = [r.overall_score for r in results if r.overall_score >= 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "total_models": len(results),
            "average_score": avg_score,
            "rankings": [r.to_dict() for r in sorted_results],
            "best_model": sorted_results[0].model_id if sorted_results else None,
            "worst_model": sorted_results[-1].model_id if sorted_results else None
        }
