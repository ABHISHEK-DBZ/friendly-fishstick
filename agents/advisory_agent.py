"""
Advisory Agent for Farmer-Friendly Action Plans
Converts technical diagnosis and research into clear, actionable instructions
"""
from typing import Dict, Any
from agent_framework import Executor, WorkflowContext, handler
from agent_framework import ChatAgent, ChatMessage
from config import Config
import sys
from pathlib import Path

# Add parent directory to path for translations
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from translations import get_advisory_instruction


class AdvisoryAgent(Executor):
    """
    Agent responsible for creating farmer-friendly action plans.
    
    This agent:
    1. Receives technical diagnosis and research data
    2. Translates complex information into simple language
    3. Creates step-by-step action plans
    4. Provides timeline and follow-up schedule
    5. Supports multilingual output (English/Hindi)
    """
    
    agent: ChatAgent
    
    def __init__(self, chat_client, id: str = "advisory_agent"):
        """
        Initialize the Advisory Agent.
        
        Args:
            chat_client: Azure OpenAI chat client
            id: Unique identifier for this executor
        """
        self.agent = chat_client.create_agent(
            instructions="""You are an experienced agricultural extension officer who helps farmers.

Your communication style:
- Simple, clear language (avoid jargon)
- Step-by-step instructions
- Visual references where possible
- Practical and actionable
- Empathetic and encouraging
- Culturally appropriate for rural Indian farmers

Your tasks:
1. Take technical diagnosis and research data
2. Create a SIMPLE action plan with numbered steps
3. Provide clear timeline (today, tomorrow, next week, etc.)
4. Include safety warnings in plain language
5. Suggest follow-up schedule
6. Estimate costs in INR (Indian Rupees)
7. Provide contact info for emergencies

Output format:
Use clear sections with emojis:
🌱 PROBLEM IDENTIFIED
🔍 WHAT YOU NEED TO DO
⏰ TIMELINE
💰 ESTIMATED COST
⚠️ SAFETY TIPS
📅 FOLLOW-UP SCHEDULE
📞 NEED HELP?

Keep it conversational but structured.
Use bullet points and numbered lists.
""",
            model=Config.TEXT_MODEL
        )
        super().__init__(id=id)
    
    @handler
    async def create_action_plan(
        self,
        research_data: Dict[str, Any],
        ctx: WorkflowContext[None, Dict[str, Any]]
    ) -> None:
        """
        Create farmer-friendly action plan.
        
        Args:
            research_data: Complete data from Research Agent
            ctx: Workflow context to yield final output
        """
        diagnosis = research_data.get("diagnosis", "")
        research = research_data.get("research", "")
        treatment_info = research_data.get("treatment_info", {})
        weather = research_data.get("weather", {})
        language = research_data.get("language", "en")  # Default to English
        
        # Build advisory prompt using translations
        advisory_prompt = get_advisory_instruction(
            diagnosis=diagnosis,
            research=research,
            weather=str(weather),
            language=language
        )
        
        message = ChatMessage(role="user", text=advisory_prompt)
        response = await self.agent.run([message])
        action_plan = response.messages[-1].text
        
        # Package final output
        final_output = {
            "user_id": research_data.get("user_id"),
            "diagnosis_summary": diagnosis,
            "action_plan": action_plan,
            "weather_context": weather,
            "image_path": research_data.get("image_path"),
            "generated_at": research_data.get("timestamp"),
            "language": language,
            "follow_up_required": True,
            "follow_up_days": 2  # Check back in 2 days
        }
        
        # Yield final output - this completes the workflow
        await ctx.yield_output(final_output)
