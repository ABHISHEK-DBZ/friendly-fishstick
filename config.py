"""
Configuration management for AI Krishi Sahayak
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = BASE_DIR / "uploads"
    LOGS_DIR = BASE_DIR / "logs"
    
    # API Keys
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    OPEN_METEO_URL = os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast")
    
    # Model Configuration
    VISION_MODEL = os.getenv("VISION_MODEL", "gemini-2.5-flash")
    TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")
    DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gemini-2.5-flash")
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Disease Database
    DISEASE_KNOWLEDGE_BASE = {
        "early_blight": {
            "crops": ["tomato", "potato"],
            "symptoms": ["dark brown spots", "concentric rings", "yellow halo"],
            "treatment": {
                "organic": "Neem oil spray (2ml/L) every 3 days",
                "chemical": "Chlorothalonil-based fungicide",
                "cultural": "Remove affected leaves, avoid overhead watering"
            }
        },
        "late_blight": {
            "crops": ["tomato", "potato"],
            "symptoms": ["water-soaked spots", "white fungal growth", "rapid spread"],
            "treatment": {
                "organic": "Copper-based fungicide",
                "chemical": "Mancozeb or Metalaxyl",
                "cultural": "Improve air circulation, remove infected plants"
            }
        },
        "powdery_mildew": {
            "crops": ["cucurbits", "grapes", "roses"],
            "symptoms": ["white powdery coating", "leaf distortion"],
            "treatment": {
                "organic": "Baking soda solution (1 tsp/L water)",
                "chemical": "Sulfur-based fungicide",
                "cultural": "Increase sunlight exposure, reduce humidity"
            }
        },
        "bacterial_spot": {
            "crops": ["tomato", "pepper"],
            "symptoms": ["small dark spots", "yellow halo", "leaf drop"],
            "treatment": {
                "organic": "Copper spray",
                "chemical": "Streptomycin sulfate",
                "cultural": "Use disease-free seeds, crop rotation"
            }
        }
    }
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.UPLOADS_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create subdirectories
        (cls.DATA_DIR / "user_sessions").mkdir(exist_ok=True)

# Initialize directories on import
Config.ensure_directories()
