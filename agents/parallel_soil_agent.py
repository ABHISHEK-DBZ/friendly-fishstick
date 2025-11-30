"""
Parallel Soil Agent - Runs concurrently with other agents
Demonstrates: Parallel Agent Execution
"""
import logging
from typing import Dict, Any
from agent_framework import BaseAgent, handler

logger = logging.getLogger(__name__)


class ParallelSoilAgent(BaseAgent):
    """
    Soil analysis agent that runs in parallel with other agents.
    Analyzes soil conditions and provides recommendations.
    """
    
    def __init__(self, chat_client):
        super().__init__(name="ParallelSoil")
        self.chat_client = chat_client
        logger.info("Parallel Soil Agent initialized")
    
    async def analyze_soil(self, state: Dict[str, Any]) -> str:
        """
        Analyze soil requirements based on diagnosis.
        Runs in parallel with weather and research agents.
        """
        logger.info("Parallel Soil Agent: Starting soil analysis")
        
        diagnosis = state.get("diagnosis_summary", {})
        location = state.get("location", "India")
        
        try:
            prompt = f"""
Based on the plant diagnosis, analyze soil requirements and conditions:

**Diagnosis**: {diagnosis}

**Location**: {location}

**Provide detailed soil analysis**:
1. **Optimal Soil Type**: What soil type is best for this plant?
2. **pH Requirements**: Ideal pH range and how to adjust
3. **Nutrient Requirements**: NPK and micronutrients needed
4. **Soil Moisture**: Watering requirements and drainage
5. **Soil Amendments**: Specific fertilizers, compost, or amendments
6. **Soil Testing**: What tests should be performed
7. **Problem Indicators**: Signs of soil-related issues in the diagnosis
8. **Treatment Timeline**: Soil improvement schedule

Consider:
- The diagnosed condition and how soil affects it
- Regional soil characteristics for {location}
- Organic vs chemical treatments
- Cost-effective solutions for farmers

Format as JSON with keys: optimal_soil, ph_requirements, nutrients, moisture, amendments, testing, problem_indicators, timeline
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_client.complete(messages=messages)
            
            analysis = response.choices[0].message.content
            logger.info(f"Soil analysis complete: {len(analysis)} chars")
            
            return analysis
        
        except Exception as e:
            logger.error(f"Soil analysis failed: {str(e)}")
            return f'{{"error": "Soil analysis failed: {str(e)}"}}'
    
    @handler
    async def handle_soil(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute soil analysis in parallel."""
        logger.info("Parallel Soil Agent: Running")
        
        soil_analysis = await self.analyze_soil(state)
        
        # Update state with soil analysis
        state["soil_analysis"] = soil_analysis
        
        logger.info("Parallel Soil Agent: Completed")
        return state
