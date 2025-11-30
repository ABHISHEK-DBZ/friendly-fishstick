"""
Parallel Weather Agent - Runs concurrently with other agents
Demonstrates: Parallel Agent Execution
"""
import logging
from typing import Dict, Any
import asyncio
import requests
from agent_framework import BaseAgent, handler
from config import Config

logger = logging.getLogger(__name__)


class ParallelWeatherAgent(BaseAgent):
    """
    Weather analysis agent that runs in parallel with other agents.
    Fetches detailed weather and climate data for crop recommendations.
    """
    
    def __init__(self, chat_client):
        super().__init__(name="ParallelWeather")
        self.chat_client = chat_client
        logger.info("Parallel Weather Agent initialized")
    
    async def analyze_weather(self, state: Dict[str, Any]) -> str:
        """
        Analyze weather conditions for crop health assessment.
        Runs in parallel with soil and research agents.
        """
        logger.info("Parallel Weather Agent: Starting weather analysis")
        
        location = state.get("location", "India")
        diagnosis = state.get("diagnosis_summary", {})
        
        try:
            # Get weather data
            weather_data = await self._fetch_weather_data(location)
            
            # Analyze weather impact
            prompt = f"""
Based on the plant diagnosis and current weather conditions, analyze the weather impact:

**Diagnosis**: {diagnosis}

**Current Weather**:
- Temperature: {weather_data.get('temperature', 'N/A')}°C
- Humidity: {weather_data.get('humidity', 'N/A')}%
- Wind Speed: {weather_data.get('wind_speed', 'N/A')} km/h
- Precipitation: {weather_data.get('precipitation', 'N/A')} mm
- Location: {location}

**Provide**:
1. Weather impact on the diagnosed condition (positive/negative)
2. Risk factors from current weather
3. Weather-specific recommendations
4. Optimal weather conditions needed for recovery
5. Climate-based treatment timing

Format as JSON with keys: impact, risks, recommendations, optimal_conditions, timing
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_client.complete(messages=messages)
            
            analysis = response.choices[0].message.content
            logger.info(f"Weather analysis complete: {len(analysis)} chars")
            
            return analysis
        
        except Exception as e:
            logger.error(f"Weather analysis failed: {str(e)}")
            return f'{{"error": "Weather analysis failed: {str(e)}"}}'
    
    async def _fetch_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch weather data from Open-Meteo API."""
        try:
            # Geocoding to get coordinates
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            
            if not geo_data.get("results"):
                logger.warning(f"Location not found: {location}")
                return {"error": "Location not found"}
            
            coords = geo_data["results"][0]
            lat = coords["latitude"]
            lon = coords["longitude"]
            
            # Fetch weather
            weather_url = f"{Config.OPEN_METEO_URL}?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()
            
            current = weather_data.get("current", {})
            
            return {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation"),
                "wind_speed": current.get("wind_speed_10m"),
                "location": location,
                "coordinates": {"latitude": lat, "longitude": lon}
            }
        
        except Exception as e:
            logger.error(f"Weather fetch failed: {str(e)}")
            return {"error": str(e)}
    
    @handler
    async def handle_weather(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather analysis in parallel."""
        logger.info("Parallel Weather Agent: Running")
        
        weather_analysis = await self.analyze_weather(state)
        
        # Update state with weather analysis
        state["weather_analysis"] = weather_analysis
        
        logger.info("Parallel Weather Agent: Completed")
        return state
