"""
Enhanced Main Coordinator with Advanced Features
Demonstrates: Parallel Agents, Observability, Long-running Operations
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

from agent_framework import WorkflowBuilder, ConcurrentBuilder, FanOutEdgeGroup, FanInEdgeGroup
from agent_framework.openai import OpenAIChatClient
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from agents.vision_agent import VisionAgent
from agents.research_agent import ResearchAgent
from agents.advisory_agent import AdvisoryAgent
from agents.memory_agent import MemoryAgent
from agents.parallel_weather_agent import ParallelWeatherAgent
from agents.parallel_soil_agent import ParallelSoilAgent
from agents.evaluation_agent import EvaluationAgent
from config import Config

# Setup Observability (OpenTelemetry)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Custom Metrics
diagnosis_counter = meter.create_counter(
    "krishi_sahayak.diagnoses.total",
    description="Total number of plant diagnoses performed"
)

diagnosis_duration = meter.create_histogram(
    "krishi_sahayak.diagnosis.duration",
    description="Duration of diagnosis operations in seconds"
)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / 'agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedKrishiSahayakCoordinator:
    """
    Enhanced coordinator demonstrating:
    1. Parallel Agent Execution (Weather + Soil Analysis in parallel)
    2. Observability (OpenTelemetry tracing & metrics)
    3. Long-running Operations (pause/resume capability)
    4. Advanced State Management
    5. Agent Evaluation
    """
    
    def __init__(self):
        """Initialize the enhanced coordinator with all agents."""
        logger.info("Initializing Enhanced Krishi Sahayak Coordinator")
        
        # Initialize chat client
        if Config.GEMINI_API_KEY:
            self.chat_client = self._init_gemini_client()
            logger.info("Using Gemini AI client")
        elif Config.GITHUB_TOKEN:
            self.chat_client = self._init_github_client()
            logger.info("Using GitHub Models client")
        elif Config.AZURE_OPENAI_KEY:
            self.chat_client = self._init_azure_client()
            logger.info("Using Azure OpenAI client")
        else:
            raise ValueError("No API credentials found in .env")
        
        # Initialize agents
        self.vision_agent = VisionAgent(self.chat_client)
        self.research_agent = ResearchAgent(self.chat_client)
        self.advisory_agent = AdvisoryAgent(self.chat_client)
        self.memory_agent = MemoryAgent()
        
        # New parallel agents for enhanced analysis
        self.weather_agent = ParallelWeatherAgent(self.chat_client)
        self.soil_agent = ParallelSoilAgent(self.chat_client)
        
        # Evaluation agent for quality assessment
        self.evaluation_agent = EvaluationAgent(self.chat_client)
        
        # Build enhanced workflow with parallel execution
        self.workflow = self._build_enhanced_workflow()
        
        # State management for pause/resume
        self.workflow_state: Dict[str, Any] = {}
        self.paused = False
        
        logger.info("Enhanced coordinator initialized successfully")
    
    def _init_gemini_client(self) -> OpenAIChatClient:
        """Initialize Gemini client."""
        return OpenAIChatClient(
            api_key=Config.GEMINI_API_KEY,
            model_id=Config.VISION_MODEL,
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
    
    def _build_enhanced_workflow(self):
        """
        Build enhanced multi-agent workflow with parallel execution.
        
        Flow:
        1. Vision Agent (analyzes image)
        2. PARALLEL: Weather Agent + Soil Agent + Research Agent
        3. Advisory Agent (consolidates all inputs)
        4. Evaluation Agent (quality check)
        """
        workflow = (
            WorkflowBuilder()
            .set_start_executor(self.vision_agent)
            # After vision, run 3 agents in parallel
            .add_edge(
                self.vision_agent,
                FanOutEdgeGroup([
                    self.weather_agent,
                    self.soil_agent,
                    self.research_agent
                ])
            )
            # Collect parallel results and send to advisory
            .add_edge(
                FanInEdgeGroup([
                    self.weather_agent,
                    self.soil_agent,
                    self.research_agent
                ]),
                self.advisory_agent
            )
            # Final evaluation
            .add_edge(self.advisory_agent, self.evaluation_agent)
            .build()
        )
        
        logger.info("Enhanced workflow built with parallel execution")
        return workflow
    
    async def diagnose_plant_with_observability(
        self,
        image_path: str,
        user_id: str,
        location: str = "",
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Diagnose plant with full observability and metrics.
        
        Features:
        - OpenTelemetry tracing
        - Custom metrics
        - Structured logging
        - Pause/resume capability
        """
        start_time = datetime.now()
        
        # Start OpenTelemetry span for tracing
        with tracer.start_as_current_span("plant_diagnosis") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("location", location)
            span.set_attribute("image_path", image_path)
            
            logger.info(f"Starting diagnosis for user {user_id}")
            
            try:
                # Prepare input context
                input_context = {
                    "image_path": image_path,
                    "user_id": user_id,
                    "location": location,
                    "additional_context": additional_context,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Input context prepared: {input_context}")
                
                # Check if paused
                if self.paused:
                    logger.warning("Workflow is paused")
                    return {
                        "status": "paused",
                        "message": "Workflow is currently paused",
                        "state": self.workflow_state
                    }
                
                # Execute workflow
                with tracer.start_as_current_span("workflow_execution"):
                    logger.info("Executing enhanced workflow")
                    result = await self.workflow.run(input_context)
                    logger.info("Workflow execution completed")
                
                # Save to memory
                with tracer.start_as_current_span("save_to_memory"):
                    await self._save_to_memory(result)
                
                # Record metrics
                duration = (datetime.now() - start_time).total_seconds()
                diagnosis_counter.add(1, {"status": "success"})
                diagnosis_duration.record(duration)
                
                span.set_attribute("diagnosis_status", "success")
                span.set_attribute("duration_seconds", duration)
                
                logger.info(f"Diagnosis completed successfully in {duration:.2f}s")
                
                return {
                    "status": "success",
                    "result": result,
                    "duration_seconds": duration,
                    "metrics": {
                        "total_diagnoses": diagnosis_counter,
                        "duration": duration
                    }
                }
                
            except Exception as e:
                logger.error(f"Diagnosis failed: {str(e)}", exc_info=True)
                span.set_attribute("error", True)
                span.set_attribute("error_message", str(e))
                
                diagnosis_counter.add(1, {"status": "error"})
                
                return {
                    "status": "error",
                    "error": str(e),
                    "traceback": str(e)
                }
    
    def pause_workflow(self):
        """Pause the workflow - demonstrates long-running operation control."""
        logger.info("Pausing workflow")
        self.paused = True
        self.workflow_state = {
            "paused_at": datetime.now().isoformat(),
            "status": "paused"
        }
        return self.workflow_state
    
    def resume_workflow(self):
        """Resume the workflow."""
        logger.info("Resuming workflow")
        self.paused = False
        self.workflow_state["resumed_at"] = datetime.now().isoformat()
        self.workflow_state["status"] = "active"
        return self.workflow_state
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return {
            "paused": self.paused,
            "state": self.workflow_state,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _save_to_memory(self, output: Dict[str, Any]):
        """Save diagnosis results to memory."""
        try:
            diagnosis_text = output.get("diagnosis_summary", "")
            
            if diagnosis_text:
                try:
                    diagnosis_json = json.loads(diagnosis_text)
                except json.JSONDecodeError:
                    diagnosis_json = {"diagnosis": diagnosis_text}
                
                session_id = self.memory_agent.save_session(
                    user_id=output.get("user_id"),
                    image_path=output.get("image_path"),
                    location=output.get("location", ""),
                    diagnosis_json=diagnosis_text,
                    action_plan=output.get("action_plan", "")
                )
                
                logger.info(f"Saved to memory with session_id: {session_id}")
                
                # Schedule follow-up if needed
                if session_id and output.get("follow_up_required"):
                    follow_up_days = output.get("follow_up_days", 2)
                    self.memory_agent.schedule_follow_up(
                        user_id=output.get("user_id"),
                        session_id=session_id,
                        follow_up_days=follow_up_days
                    )
                    logger.info(f"Follow-up scheduled for {follow_up_days} days")
        
        except Exception as e:
            logger.error(f"Error saving to memory: {str(e)}")


# Convenience function for backward compatibility
async def diagnose_plant(image_path: str, user_id: str, location: str = "", additional_context: str = ""):
    """Wrapper function for enhanced diagnosis."""
    coordinator = EnhancedKrishiSahayakCoordinator()
    return await coordinator.diagnose_plant_with_observability(
        image_path=image_path,
        user_id=user_id,
        location=location,
        additional_context=additional_context
    )


if __name__ == "__main__":
    # Demo of enhanced features
    async def demo():
        coordinator = EnhancedKrishiSahayakCoordinator()
        
        # Test observability
        logger.info("=== Testing Enhanced Features ===")
        
        # Get workflow state
        state = coordinator.get_workflow_state()
        logger.info(f"Initial state: {state}")
        
        # Pause workflow
        coordinator.pause_workflow()
        logger.info("Workflow paused")
        
        # Resume workflow
        coordinator.resume_workflow()
        logger.info("Workflow resumed")
        
        logger.info("=== Demo Complete ===")
    
    asyncio.run(demo())
