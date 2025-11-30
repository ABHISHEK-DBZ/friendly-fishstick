"""
Research Agent for Treatment and Weather Data
Fetches treatment guidelines, weather information, and pesticide safety data
"""
import json
from typing import Dict, Any
from datetime import datetime
import requests

from agent_framework import Executor, WorkflowContext, handler
from agent_framework import ChatAgent, ChatMessage
from config import Config


class ResearchAgent(Executor):
    """
    Agent responsible for researching treatment options and environmental data.
    
    This agent:
    1. Receives disease diagnosis from Vision Agent
    2. Looks up treatment recommendations from knowledge base
    3. Fetches current weather data for the farmer's location
    4. Compiles pesticide safety guidelines
    5. Provides crop-specific care instructions
    """
    
    agent: ChatAgent
    
    def __init__(self, chat_client, id: str = "research_agent"):
        """
        Initialize the Research Agent.
        
        Args:
            chat_client: Azure OpenAI chat client
            id: Unique identifier for this executor
        """
        self.agent = chat_client.create_agent(
            instructions="""You are an agricultural research specialist with expertise in:
- Plant disease treatment (organic and chemical)
- Integrated Pest Management (IPM)
- Weather-based crop advisory
- Pesticide safety and regulations
- Sustainable farming practices

Your role:
1. Analyze the disease diagnosis provided
2. Research and recommend appropriate treatments
3. Consider weather conditions for treatment timing
4. Provide safety guidelines for pesticide use
5. Suggest preventive measures

Always prioritize:
- Farmer safety
- Environmental sustainability
- Cost-effectiveness
- Practical applicability for small-scale farmers
""",
            model=Config.TEXT_MODEL
        )
        super().__init__(id=id)
    
    @handler
    async def research_treatment(
        self,
        diagnosis_data: Dict[str, Any],
        ctx: WorkflowContext[Dict[str, Any]]
    ) -> None:
        """
        Research treatment options based on diagnosis.
        
        Args:
            diagnosis_data: Contains diagnosis, location, user info
            ctx: Workflow context to send research results
        """
        # Parse diagnosis
        diagnosis_text = diagnosis_data.get("diagnosis", "")
        location = diagnosis_data.get("location", "")
        
        # Extract disease name from diagnosis (simple parsing)
        disease_name = self._extract_disease_name(diagnosis_text)
        
        # Look up treatment from knowledge base
        treatment_info = self._get_treatment_info(disease_name)
        
        # Fetch weather data
        weather_data = await self._get_weather_data(location)
        
        # Build comprehensive research prompt
        research_prompt = f"""Based on the following diagnosis, provide comprehensive treatment recommendations:

DIAGNOSIS:
{diagnosis_text}

AVAILABLE TREATMENT OPTIONS:
{json.dumps(treatment_info, indent=2)}

CURRENT WEATHER:
{json.dumps(weather_data, indent=2)}

Provide:
1. **Recommended Treatment Plan** (prioritize organic first, then chemical if needed)
2. **Application Schedule** (considering weather)
3. **Safety Precautions** (PPE, handling, storage)
4. **Preventive Measures** (to avoid recurrence)
5. **Cost Estimate** (approximate, in INR if possible)
6. **Expected Recovery Timeline**

Format as structured JSON for easy parsing."""
        
        message = ChatMessage(role="user", text=research_prompt)
        response = await self.agent.run([message])
        research_results = response.messages[-1].text
        
        # Package all data for Advisory Agent
        result = {
            "diagnosis": diagnosis_text,
            "research": research_results,
            "treatment_info": treatment_info,
            "weather": weather_data,
            "user_id": diagnosis_data.get("user_id"),
            "location": location,
            "image_path": diagnosis_data.get("image_path")
        }
        
        # Forward to Advisory Agent
        await ctx.send_message(result)
    
    def _extract_disease_name(self, diagnosis_text: str) -> str:
        """
        Extract disease name from diagnosis JSON.
        
        Args:
            diagnosis_text: Raw diagnosis from Vision Agent
            
        Returns:
            Disease name string
        """
        try:
            # Try to parse as JSON
            diagnosis_json = json.loads(diagnosis_text)
            disease = diagnosis_json.get("disease_name", "unknown").lower()
            # Normalize disease name
            return disease.replace(" ", "_")
        except json.JSONDecodeError:
            # Fallback: simple text parsing
            if "early blight" in diagnosis_text.lower():
                return "early_blight"
            elif "late blight" in diagnosis_text.lower():
                return "late_blight"
            elif "powdery mildew" in diagnosis_text.lower():
                return "powdery_mildew"
            elif "bacterial spot" in diagnosis_text.lower():
                return "bacterial_spot"
            return "unknown"
    
    def _get_treatment_info(self, disease_name: str) -> Dict[str, Any]:
        """
        Look up treatment information from knowledge base.
        
        Args:
            disease_name: Normalized disease name
            
        Returns:
            Treatment information dictionary
        """
        # Use the disease knowledge base from config
        disease_db = Config.DISEASE_KNOWLEDGE_BASE
        
        if disease_name in disease_db:
            return disease_db[disease_name]
        else:
            # Return generic treatment if disease not in database
            return {
                "treatment": {
                    "organic": "Consult local agricultural extension officer",
                    "chemical": "Professional diagnosis recommended",
                    "cultural": "Maintain good plant hygiene"
                }
            }
    
    async def _get_weather_data(self, location: str) -> Dict[str, Any]:
        """
        Fetch weather data for the farmer's location using Open-Meteo API.
        
        Args:
            location: Location string (city name)
            
        Returns:
            Weather data dictionary
        """
        if not location:
            return {
                "temperature": "N/A",
                "humidity": "N/A",
                "conditions": "Weather data unavailable",
                "note": "Please provide location"
            }
        
        try:
            # First, geocode the location to get coordinates
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geo_response = requests.get(geocode_url, timeout=5)
            
            if geo_response.status_code != 200:
                return {"error": "Unable to find location"}
            
            geo_data = geo_response.json()
            if not geo_data.get("results"):
                return {"error": f"Location '{location}' not found"}
            
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            
            # Now get weather data from Open-Meteo
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m"
                f"&timezone=auto"
            )
            weather_response = requests.get(weather_url, timeout=5)
            
            if weather_response.status_code == 200:
                data = weather_response.json()
                current = data["current"]
                
                # Determine conditions based on data
                conditions = "Clear"
                if current.get("rain", 0) > 0:
                    conditions = "Rainy"
                elif current.get("precipitation", 0) > 0:
                    conditions = "Light precipitation"
                
                return {
                    "temperature": f"{current['temperature_2m']}°C",
                    "humidity": f"{current['relative_humidity_2m']}%",
                    "conditions": conditions,
                    "wind_speed": f"{current['wind_speed_10m']} km/h",
                    "precipitation": f"{current.get('precipitation', 0)} mm",
                    "forecast_note": "Check conditions before spraying"
                }
            else:
                return {"error": "Unable to fetch weather data"}
                
        except Exception as e:
            return {
                "error": f"Weather API error: {str(e)}",
                "note": "Continue with treatment plan, check local weather manually"
            }
