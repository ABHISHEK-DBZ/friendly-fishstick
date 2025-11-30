"""
Evaluation Agent - Assesses diagnosis quality and completeness
Demonstrates: Agent Evaluation
"""
import logging
import json
from typing import Dict, Any
from agent_framework import BaseAgent, handler

logger = logging.getLogger(__name__)


class EvaluationAgent(BaseAgent):
    """
    Evaluation agent that assesses the quality of diagnosis and recommendations.
    
    Evaluates:
    1. Diagnosis accuracy and completeness
    2. Recommendation quality and actionability
    3. Information coverage
    4. Response consistency
    5. User value score
    """
    
    def __init__(self, chat_client):
        super().__init__(name="Evaluation")
        self.chat_client = chat_client
        logger.info("Evaluation Agent initialized")
        
        # Evaluation metrics
        self.metrics = {
            "total_evaluations": 0,
            "average_quality_score": 0.0,
            "high_quality_count": 0,
            "improvement_suggestions": []
        }
    
    async def evaluate_diagnosis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the complete diagnosis output for quality.
        
        Returns evaluation scores and improvement suggestions.
        """
        logger.info("Evaluation Agent: Starting quality assessment")
        
        diagnosis = state.get("diagnosis_summary", "")
        action_plan = state.get("action_plan", "")
        weather_analysis = state.get("weather_analysis", "")
        soil_analysis = state.get("soil_analysis", "")
        
        try:
            evaluation_prompt = f"""
You are a quality assurance agent evaluating agricultural diagnosis outputs.

**Diagnosis Output to Evaluate**:
- Diagnosis: {diagnosis}
- Action Plan: {action_plan}
- Weather Analysis: {weather_analysis}
- Soil Analysis: {soil_analysis}

**Evaluate on these criteria (score 0-10 each)**:

1. **Accuracy**: Is the diagnosis medically/agriculturally sound?
2. **Completeness**: Are all relevant aspects covered?
3. **Clarity**: Is the information clear and understandable?
4. **Actionability**: Are recommendations practical and specific?
5. **Consistency**: Do all parts align logically?
6. **User Value**: How helpful is this for a farmer?

**Provide**:
- Individual scores for each criterion
- Overall quality score (average)
- Strengths identified
- Improvement suggestions
- Confidence level (0-100%)
- Risk assessment (any missing critical info?)

Format as JSON with keys: accuracy, completeness, clarity, actionability, consistency, user_value, overall_score, strengths, improvements, confidence, risks
"""
            
            messages = [{"role": "user", "content": evaluation_prompt}]
            response = await self.chat_client.complete(messages=messages)
            
            evaluation_text = response.choices[0].message.content
            
            # Parse evaluation results
            try:
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                evaluation = {"raw_evaluation": evaluation_text, "overall_score": 7.0}
            
            # Update metrics
            self.metrics["total_evaluations"] += 1
            overall_score = evaluation.get("overall_score", 7.0)
            
            # Update running average
            old_avg = self.metrics["average_quality_score"]
            count = self.metrics["total_evaluations"]
            self.metrics["average_quality_score"] = (old_avg * (count - 1) + overall_score) / count
            
            if overall_score >= 8.0:
                self.metrics["high_quality_count"] += 1
            
            # Collect improvement suggestions
            improvements = evaluation.get("improvements", [])
            if improvements:
                self.metrics["improvement_suggestions"].extend(improvements)
            
            logger.info(f"Evaluation complete - Score: {overall_score}/10")
            logger.info(f"Metrics: {self.metrics}")
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return {
                "error": str(e),
                "overall_score": 5.0,
                "note": "Evaluation failed, defaulting to neutral score"
            }
    
    @handler
    async def handle_evaluation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute evaluation."""
        logger.info("Evaluation Agent: Running quality assessment")
        
        evaluation = await self.evaluate_diagnosis(state)
        
        # Add evaluation to state
        state["evaluation"] = evaluation
        state["quality_score"] = evaluation.get("overall_score", 7.0)
        
        # Add quality badge
        score = state["quality_score"]
        if score >= 9.0:
            state["quality_badge"] = "EXCELLENT"
        elif score >= 7.5:
            state["quality_badge"] = "GOOD"
        elif score >= 6.0:
            state["quality_badge"] = "SATISFACTORY"
        else:
            state["quality_badge"] = "NEEDS_IMPROVEMENT"
        
        logger.info(f"Evaluation Agent: Completed - Badge: {state['quality_badge']}")
        
        return state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get evaluation metrics for monitoring."""
        return {
            **self.metrics,
            "high_quality_percentage": (
                self.metrics["high_quality_count"] / self.metrics["total_evaluations"] * 100
                if self.metrics["total_evaluations"] > 0 else 0
            )
        }
