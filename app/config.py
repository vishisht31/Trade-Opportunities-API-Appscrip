
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    
    gemini_api_key: str = Field(..., description="Google Gemini API key from .env")
    api_keys: str = Field(..., description="API keys for authentication (comma-separated) from .env")
    
    rate_limit_per_hour: int = 10
    

    cache_ttl_seconds: int = 3600
    

    allowed_sectors: str = "pharmaceuticals,technology,agriculture,energy,finance,healthcare,manufacturing,retail"
    
    app_name: str = "Trade Opportunities API"
    app_version: str = "1.0.0"
    app_description: str = "Market analysis and trade opportunity insights for Indian sectors"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_api_keys(self) -> List[str]:
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    def get_allowed_sectors(self) -> List[str]:
        return [sector.strip().lower() for sector in self.allowed_sectors.split(",") if sector.strip()]
    
    def is_valid_api_key(self, api_key: str) -> bool:
        return api_key in self.get_api_keys()
    
    def is_valid_sector(self, sector: str) -> bool:
        return sector.lower() in self.get_allowed_sectors()


settings = Settings()
