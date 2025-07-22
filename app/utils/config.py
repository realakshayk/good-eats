import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application Settings
    MAX_RESTAURANTS: int = int(os.getenv("MAX_RESTAURANTS", "10"))
    MAX_RECOMMENDATIONS: int = int(os.getenv("MAX_RECOMMENDATIONS", "5"))
    SEARCH_RADIUS_METERS: int = int(os.getenv("SEARCH_RADIUS_METERS", "5000"))
    
    # LLM Settings
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Scraping Settings
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", "30"))
    
    def validate(self) -> bool:
        """Validate that required API keys are present."""
        if not self.GOOGLE_MAPS_API_KEY:
            raise ValueError("GOOGLE_MAPS_API_KEY is required")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

settings = Settings() 