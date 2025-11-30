"""
Main Coordinator - AI Krishi Sahayak
Orchestrates the multi-agent workflow for agricultural assistance
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from agent_framework import WorkflowBuilder
from agent_framework.openai import OpenAIChatClient
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from agents.vision_agent import VisionAgent
from agents.research_agent import ResearchAgent
from agents.advisory_agent import AdvisoryAgent
from agents.memory_agent import MemoryAgent
from config import Config


class KrishiSahayakCoordinator:
    """
    Main coordinator for the AI Krishi Sahayak system.
    
    Orchestrates the multi-agent workflow:
    Vision Agent → Research Agent → Advisory Agent
    
    Memory Agent runs in parallel to store/retrieve data.
    """
    
    def __init__(self):
        """Initialize the coordinator with all agents."""
        # Initialize chat client based on configuration
        if Config.GEMINI_API_KEY:
            # Use Gemini (recommended)
            self.chat_client = self._init_gemini_client()
        elif Config.GITHUB_TOKEN:
            # Use GitHub Models
            self.chat_client = self._init_github_client()
        elif Config.AZURE_OPENAI_KEY:
            # Use Azure OpenAI
            self.chat_client = self._init_azure_client()
        else:
            raise ValueError("No API credentials found. Set GEMINI_API_KEY, GITHUB_TOKEN or AZURE_OPENAI_KEY in .env")
        
        # Initialize agents
        self.vision_agent = VisionAgent(self.chat_client)
        self.research_agent = ResearchAgent(self.chat_client)
        self.advisory_agent = AdvisoryAgent(self.chat_client)
        self.memory_agent = MemoryAgent()
        
        # Build the workflow
        self.workflow = self._build_workflow()
    
    def _init_gemini_client(self) -> OpenAIChatClient:
        """Initialize Gemini client using OpenAI-compatible interface."""
        # Gemini through OpenAI SDK requires specific format
        import openai
        client = openai.OpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        return OpenAIChatClient(
            api_key=Config.GEMINI_API_KEY,
            model_id="gemini-2.5-flash",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    def _init_github_client(self) -> OpenAIChatClient:
        """Initialize GitHub Models client."""
        return OpenAIChatClient(
            api_key=Config.GITHUB_TOKEN,
            model_id=Config.VISION_MODEL,
            base_url="https://models.inference.ai.azure.com"
        )
    
    def _init_azure_client(self) -> AzureOpenAIChatClient:
        """Initialize Azure OpenAI client."""
        return AzureOpenAIChatClient(
            credential=DefaultAzureCredential(),
            endpoint=Config.AZURE_OPENAI_ENDPOINT,
            model_name=Config.VISION_MODEL
        )
    
    def _build_workflow(self):
        """
        Build the multi-agent workflow.
        
        Flow: Vision → Research → Advisory
        """
        workflow = (
            WorkflowBuilder()
            .set_start_executor(self.vision_agent)
            .add_edge(self.vision_agent, self.research_agent)
            .add_edge(self.research_agent, self.advisory_agent)
            .build()
        )
        return workflow
    
    async def diagnose_plant(
        self,
        image_path: str,
        user_id: str,
        location: str = "",
        additional_context: str = "",
        language: str = "en"
    ) -> dict:
        """
        Main method to diagnose plant disease and provide action plan.
        
        Args:
            image_path: Path to plant image
            user_id: User identifier
            location: Farmer's location (for weather data)
            additional_context: Any additional info from farmer
            language: Language for output ("en" or "hi")
            
        Returns:
            Complete diagnosis and action plan
        """
        # Prepare input data
        input_data = {
            "image_path": image_path,
            "user_id": user_id,
            "location": location,
            "additional_context": additional_context,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        print("🌱 Starting AI Krishi Sahayak diagnosis...")
        print(f"📸 Analyzing image: {image_path}")
        
        # Run the workflow with streaming
        final_output = None
        async for event in self.workflow.run_stream(input_data):
            # You can handle different event types here for detailed logging
            from agent_framework import WorkflowOutputEvent
            if isinstance(event, WorkflowOutputEvent):
                final_output = event.data
                print("✅ Diagnosis complete!")
        
        # Save to memory
        if final_output:
            await self._save_to_memory(final_output)
        
        return final_output
    
    async def _save_to_memory(self, output: dict):
        """Save diagnosis session to memory database."""
        try:
            # Parse diagnosis to extract key info
            diagnosis_text = output.get("diagnosis_summary", "")
            
            # Simple parsing to extract disease and confidence
            disease_name = "unknown"
            confidence = 0.0
            plant_type = "unknown"
            
            try:
                diagnosis_json = json.loads(diagnosis_text)
                disease_name = diagnosis_json.get("disease_name", "unknown")
                confidence = float(diagnosis_json.get("confidence", 0))
                plant_type = diagnosis_json.get("plant_type", "unknown")
            except:
                # Fallback if not valid JSON
                pass
            
            # Save session
            session_id = self.memory_agent.save_session(
                user_id=output.get("user_id"),
                image_path=output.get("image_path"),
                plant_type=plant_type,
                disease_detected=disease_name,
                confidence=confidence,
                diagnosis_json=diagnosis_text,
                action_plan=output.get("action_plan", "")
            )
            
            # Schedule follow-up
            if session_id and output.get("follow_up_required"):
                follow_up_days = output.get("follow_up_days", 2)
                self.memory_agent.schedule_follow_up(
                    session_id=session_id,
                    user_id=output.get("user_id"),
                    days_ahead=follow_up_days,
                    notes="Check progress on treatment"
                )
                print(f"📅 Follow-up scheduled in {follow_up_days} days")
        
        except Exception as e:
            print(f"⚠️ Warning: Could not save to memory: {e}")
    
    def get_user_history(self, user_id: str, limit: int = 5):
        """Get user's past diagnoses."""
        return self.memory_agent.get_user_history(user_id, limit)
    
    def get_follow_ups(self, user_id: str):
        """Get pending follow-ups for user."""
        return self.memory_agent.get_pending_follow_ups(user_id)
    
    def create_user(self, user_id: str, name: str, location: str, phone: str = ""):
        """Create a new user profile."""
        return self.memory_agent.create_user(user_id, name, location, phone)


async def main():
    """
    Demo: Test the complete workflow with a sample image.
    """
    print("=" * 60)
    print("🌾 AI KRISHI SAHAYAK - Intelligent Agricultural Assistant")
    print("=" * 60)
    print()
    
    # Initialize coordinator
    coordinator = KrishiSahayakCoordinator()
    
    # Create a demo user
    coordinator.create_user(
        user_id="farmer001",
        name="Ramesh Kumar",
        location="Pune",  # or "Mumbai" or any city
        phone="+91-9876543210"
    )
    
    # Example: Diagnose a plant
    # NOTE: You'll need to provide an actual image path
    # For demo purposes, create a placeholder or use a test image
    
    print("📋 Demo User Profile Created")
    print("   User ID: farmer001")
    print("   Name: Ramesh Kumar")
    print("   Location: Pune")
    print()
    
    # Check if there's a sample image in uploads directory
    sample_image = Config.UPLOADS_DIR / "sample_leaf.jpg"
    
    if sample_image.exists():
        print(f"🔍 Using sample image: {sample_image}")
        
        # Run diagnosis
        result = await coordinator.diagnose_plant(
            image_path=str(sample_image),
            user_id="farmer001",
            location="Pune",
            additional_context="Noticed brown spots on tomato leaves yesterday"
        )
        
        print()
        print("=" * 60)
        print("📊 DIAGNOSIS RESULT")
        print("=" * 60)
        print()
        print(result.get("action_plan", "No action plan generated"))
        print()
        
        # Show follow-ups
        follow_ups = coordinator.get_follow_ups("farmer001")
        if follow_ups:
            print("📅 SCHEDULED FOLLOW-UPS:")
            for fu in follow_ups:
                print(f"   - {fu['scheduled_date']}: Check on {fu['disease']}")
        print()
        
    else:
        print(f"⚠️ No sample image found at: {sample_image}")
        print("   Please place a plant leaf image at this location to test.")
        print()
        print("   For testing without an image, you can:")
        print("   1. Download a plant disease image from the internet")
        print("   2. Save it as 'sample_leaf.jpg' in the 'uploads' folder")
        print("   3. Run this script again")
    
    print()
    print("=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
