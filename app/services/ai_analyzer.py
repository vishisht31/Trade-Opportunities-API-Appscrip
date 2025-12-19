
import logging
from typing import Optional
from datetime import datetime

import google.generativeai as genai

from app.config import settings
from app.models.schemas import MarketData, AnalysisResult

logger = logging.getLogger(__name__)


class AIAnalyzer:
    
    def __init__(self):
        # Try newer model first, fallback to gemini-pro
        self.model_name = "gemini-1.5-flash"  # Faster and more capable
        self._configure_api()
    
    def _configure_api(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            logger.info("Gemini API configured successfully")
        else:
            logger.warning("Gemini API key not configured")
    
    async def analyze_market_data(self, market_data: MarketData) -> AnalysisResult:
        logger.info(f"Analyzing market data for sector: {market_data.sector}")
        
        try:
            prompt = self._build_analysis_prompt(market_data)
            
            insights = await self._generate_insights(prompt)
            
            result = AnalysisResult(
                sector=market_data.sector,
                insights=insights,
                analyzed_at=datetime.utcnow()
            )
            
            logger.info(f"Analysis completed for {market_data.sector}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            return AnalysisResult(
                sector=market_data.sector,
                insights=self._get_fallback_analysis(market_data.sector),
                analyzed_at=datetime.utcnow()
            )
    
    def _build_analysis_prompt(self, market_data: MarketData) -> str:
        data_summary = "\n\n".join(market_data.results[:10])  # Use more data points
        
        prompt = f"""You are an expert financial analyst and market researcher specializing in Indian markets and trade opportunities. Your task is to analyze the {market_data.sector} sector in India and provide a comprehensive, detailed trade opportunity analysis.

**Market Data Collected:**
{data_summary}

**Instructions:**
Provide a detailed, professional market analysis report in markdown format. Be specific, data-driven, and actionable. Include concrete examples, numbers, and insights from the provided data.

**Required Report Structure:**

## Market Overview
Provide a detailed overview of the current state of the {market_data.sector} sector in India. Include:
- Market size and growth metrics (if available in the data)
- Current market dynamics
- Key market segments
- Recent developments and news

## Key Market Trends
Identify and explain 4-6 major trends affecting this sector:
- Emerging trends with specific examples
- Technology adoption trends
- Consumer behavior changes
- Regulatory trends
- Market consolidation or fragmentation

## Trade Opportunities
List specific, actionable trade opportunities:
- Export opportunities (target markets, products/services)
- Import substitution opportunities
- Investment opportunities (specific areas/segments)
- Partnership/collaboration opportunities
- Value chain opportunities

## Growth Drivers
Explain 4-6 key factors driving growth:
- Economic factors
- Demographic factors
- Policy/regulatory support
- Infrastructure development
- Technology adoption
- Market demand factors

## Risks & Challenges
Identify potential risks and challenges:
- Regulatory risks
- Market competition
- Economic volatility
- Supply chain risks
- Technology disruption risks
- Other sector-specific challenges

## Investment Recommendations
Provide actionable recommendations:
- Best entry strategies
- Key companies/segments to watch
- Timing considerations
- Risk mitigation strategies
- Due diligence focus areas

**Important Guidelines:**
- Use specific details from the provided market data
- Include numbers, percentages, and concrete examples where available
- Write in a professional, analytical tone
- Focus on actionable insights
- Be realistic about opportunities and risks
- Format using proper markdown headers (## for main sections, ### for subsections)
- Minimum 800-1000 words for comprehensive analysis
- Do NOT include generic placeholder text - use actual insights from the data

**Output Format:**
Provide ONLY the analysis content in markdown format. Do not include any introductory text or meta-commentary. Start directly with the Market Overview section."""

        return prompt
    
    async def _generate_insights(self, prompt: str) -> str:
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not available, using fallback")
            return "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        try:
            # Try to use the configured model, fallback to gemini-pro if needed
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 4096,
                    }
                )
            except Exception as model_error:
                logger.warning(f"Model {self.model_name} not available, trying gemini-pro: {model_error}")
                # Fallback to gemini-pro
                model = genai.GenerativeModel(
                    model_name="gemini-pro",
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 4096,
                    }
                )
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                insights = response.text.strip()
                # Ensure we got actual content, not just empty or error message
                if len(insights) > 100 and not insights.startswith("I'm sorry") and not insights.startswith("Error"):
                    logger.info(f"Generated {len(insights)} characters of analysis")
                    return insights
                else:
                    logger.warning(f"Gemini API returned insufficient content: {insights[:100]}")
                    raise Exception("Insufficient content from Gemini API")
            else:
                logger.warning("Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            # Re-raise to trigger fallback
            raise
    
    def _get_fallback_analysis(self, sector: str) -> str:
        return f"""# Market Analysis - {sector.title()} Sector

        ## Market Overview
        The {sector} sector in India represents a significant opportunity for investors and traders. This sector has been experiencing steady growth driven by various macroeconomic factors.

        ## Key Trends
        - Increasing domestic demand
        - Government policy support
        - Digital transformation
        - Focus on quality and innovation

        ## Trade Opportunities
        - Export potential to emerging markets
        - Import substitution opportunities
        - Value chain integration
        - Technology adoption

        ## Growth Drivers
        - Rising middle class
        - Infrastructure development
        - Favorable demographics
        - Policy reforms

        ## Risks & Challenges
        - Regulatory changes
        - Competition intensity
        - Global market volatility
        - Supply chain dependencies

        ## Recommendations
        - Conduct thorough due diligence
        - Monitor regulatory developments
        - Diversify portfolio exposure
        - Focus on quality companies

        *Note: This is a generic analysis. For detailed, real-time insights, please ensure Gemini API is properly configured.*
        """

ai_analyzer = AIAnalyzer()
