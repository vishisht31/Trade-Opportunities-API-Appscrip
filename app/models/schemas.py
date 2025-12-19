
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MarketData(BaseModel):
    sector: str
    query: str
    results: List[str] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResult(BaseModel):
    sector: str
    insights: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResponse(BaseModel):
    success: bool = True
    sector: str
    report: str
    generated_at: str
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "sector": "pharmaceuticals",
                "report": "# Market Analysis Report for Pharmaceuticals\n\n## Overview\n...",
                "generated_at": "2025-12-18T19:45:00",
                "message": "Analysis completed successfully"
            }
        }


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid sector",
                "detail": "Sector 'invalid' is not supported. Valid sectors: pharmaceuticals, technology, agriculture"
            }
        }


class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset_at: datetime
