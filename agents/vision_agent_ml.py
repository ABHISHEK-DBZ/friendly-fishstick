"""
Vision Agent with Local ML Model Support
Can use either API-based vision or local trained model
"""
import base64
from io import BytesIO
from typing import Dict, Any, Optional
from PIL import Image
from pathlib import Path

from agent_framework import Executor, WorkflowContext, handler
from agent_framework import ChatMessage, ChatAgent
from config import Config


class VisionAgentML(Executor):
    """
    Vision Agent that uses local trained model for plant disease detection
    No API calls required - runs completely offline
    """
    
    def __init__(self, model_path: Optional[str] = None, id: str = "vision_agent_ml"):
        """
        Initialize Vision Agent with local ML model
        
        Args:
            model_path: Path to trained model checkpoint
            id: Unique identifier for this executor
        """
        super().__init__(id=id)
        
        # Import inference module
        try:
            from ml_model.inference import get_inference_model
            
            if model_path is None:
                # Try default paths
                default_paths = [
                    Path("ml_model/checkpoints/best_model.pth"),
                    Path(__file__).parent.parent / "ml_model" / "checkpoints" / "best_model.pth"
                ]
                
                for path in default_paths:
                    if path.exists():
                        model_path = str(path)
                        break
            
            self.model = get_inference_model(model_path)
            self.use_local_model = True
            print("✅ Using local trained model for disease detection")
            
        except (ImportError, FileNotFoundError) as e:
            print(f"⚠️ Could not load local model: {e}")
            print("Please train a model first or download pre-trained weights")
            raise
    
    @handler
    async def process(self, ctx: WorkflowContext) -> Dict[str, Any]:
        """
        Process plant image using local ML model
        
        Args:
            ctx: Workflow context containing image_path and other data
            
        Returns:
            Disease diagnosis with confidence scores
        """
        # Get image path from context
        image_path = ctx.get_message_data().get("image_path")
        
        if not image_path:
            raise ValueError("No image_path provided in context")
        
        print(f"\n🔬 Analyzing image with local ML model...")
        print(f"📸 Image: {image_path}")
        
        # Run inference
        prediction = self.model.predict(image_path, top_k=3)
        
        # Format output for workflow
        primary = prediction['primary_prediction']
        
        # Create detailed analysis
        diagnosis = {
            "plant_type": primary['plant'],
            "disease_name": primary['disease'],
            "confidence_score": int(primary['confidence'] * 100),
            "severity_level": self._determine_severity(primary['confidence']),
            "visual_symptoms": self._generate_symptoms(primary['plant'], primary['disease']),
            "alternative_diagnoses": [
                {
                    "disease": pred['disease'],
                    "plant": pred['plant'],
                    "confidence": int(pred['confidence'] * 100)
                }
                for pred in prediction['alternative_predictions']
            ],
            "model_info": {
                "type": "Local CNN (ResNet50)",
                "device": prediction['model_info']['device'],
                "inference_mode": "offline"
            }
        }
        
        print(f"✅ Detection complete!")
        print(f"🌱 Plant: {diagnosis['plant_type']}")
        print(f"🦠 Disease: {diagnosis['disease_name']}")
        print(f"📊 Confidence: {diagnosis['confidence_score']}%")
        
        return {
            "vision_analysis": diagnosis,
            "image_path": image_path,
            "user_id": ctx.get_message_data().get("user_id"),
            "location": ctx.get_message_data().get("location", ""),
            "additional_context": ctx.get_message_data().get("additional_context", ""),
            "language": ctx.get_message_data().get("language", "en"),
            "timestamp": ctx.get_message_data().get("timestamp")
        }
    
    def _determine_severity(self, confidence: float) -> str:
        """Determine severity level based on confidence"""
        if confidence > 0.9:
            return "high"
        elif confidence > 0.7:
            return "moderate"
        else:
            return "low"
    
    def _generate_symptoms(self, plant: str, disease: str) -> list:
        """
        Generate typical symptoms for the disease
        In production, this would query a knowledge base
        """
        # Basic symptom mapping - can be enhanced with disease database
        symptoms_db = {
            "Early Blight": [
                "Dark brown spots with concentric rings on leaves",
                "Yellowing of leaves around spots",
                "Progressive defoliation from bottom to top"
            ],
            "Late Blight": [
                "Water-soaked lesions on leaves",
                "White fuzzy growth on undersides",
                "Rapid spread in humid conditions"
            ],
            "Leaf Spot": [
                "Small circular spots on leaves",
                "Brown or dark centers",
                "Yellow halos around spots"
            ],
            "Bacterial Blight": [
                "Water-soaked lesions",
                "Yellowing of affected areas",
                "Bacterial ooze in severe cases"
            ],
            "Powdery Mildew": [
                "White powdery coating on leaves",
                "Leaf distortion and curling",
                "Reduced photosynthesis"
            ],
            "Rust": [
                "Orange or reddish-brown pustules",
                "Usually on undersides of leaves",
                "Premature leaf drop"
            ]
        }
        
        # Find matching symptoms
        for key in symptoms_db:
            if key.lower() in disease.lower():
                return symptoms_db[key]
        
        # Default symptoms if not found
        return [
            "Visual abnormalities detected",
            "Leaf discoloration observed",
            "Potential disease symptoms present"
        ]


# Hybrid agent that can use both API and local model
class VisionAgentHybrid(Executor):
    """
    Hybrid Vision Agent - tries local model first, falls back to API
    """
    
    def __init__(self, chat_client=None, model_path: Optional[str] = None, 
                 id: str = "vision_agent_hybrid"):
        """
        Initialize hybrid vision agent
        
        Args:
            chat_client: Optional API chat client for fallback
            model_path: Path to local model
            id: Executor ID
        """
        super().__init__(id=id)
        
        # Try to load local model
        self.local_model = None
        try:
            from ml_model.inference import get_inference_model
            self.local_model = get_inference_model(model_path)
            print("✅ Local model loaded - will use for primary detection")
        except Exception as e:
            print(f"⚠️ Local model not available: {e}")
        
        # Setup API fallback
        self.api_agent = None
        if chat_client:
            self.api_agent = chat_client.create_agent(
                instructions="You are a plant disease expert. Analyze images and identify diseases."
            )
            print("✅ API fallback configured")
    
    @handler
    async def process(self, ctx: WorkflowContext) -> Dict[str, Any]:
        """Process with local model first, API as fallback"""
        
        # Try local model first
        if self.local_model:
            try:
                print("🔬 Attempting local model inference...")
                image_path = ctx.get_message_data().get("image_path")
                prediction = self.local_model.predict(image_path, top_k=3)
                
                primary = prediction['primary_prediction']
                
                # If confidence is good, use local model result
                if primary['confidence'] > 0.6:
                    print(f"✅ Local model confident ({primary['confidence']*100:.1f}%)")
                    return self._format_local_result(prediction, ctx)
                else:
                    print(f"⚠️ Low confidence ({primary['confidence']*100:.1f}%) - trying API fallback")
            
            except Exception as e:
                print(f"❌ Local model error: {e}")
        
        # Fallback to API
        if self.api_agent:
            print("🌐 Using API fallback...")
            return await self._api_fallback(ctx)
        
        raise RuntimeError("Neither local model nor API available")
    
    def _format_local_result(self, prediction: Dict, ctx: WorkflowContext) -> Dict:
        """Format local model result for workflow"""
        primary = prediction['primary_prediction']
        
        return {
            "vision_analysis": {
                "plant_type": primary['plant'],
                "disease_name": primary['disease'],
                "confidence_score": int(primary['confidence'] * 100),
                "severity_level": "moderate",
                "detection_method": "local_model"
            },
            "image_path": ctx.get_message_data().get("image_path"),
            "user_id": ctx.get_message_data().get("user_id"),
            "location": ctx.get_message_data().get("location", ""),
            "language": ctx.get_message_data().get("language", "en")
        }
    
    async def _api_fallback(self, ctx: WorkflowContext) -> Dict:
        """Use API as fallback"""
        # Import original vision agent logic here
        # For now, return error
        raise NotImplementedError("API fallback not yet implemented")
