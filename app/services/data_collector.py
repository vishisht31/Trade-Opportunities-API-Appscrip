
from typing import List, Optional
import logging
from datetime import datetime

from app.models.schemas import MarketData


logger = logging.getLogger(__name__)


class DataCollector:
    
    def __init__(self):
        self.max_results = 15  # Get more results for better analysis
    
    async def collect_market_data(self, sector: str) -> MarketData:
        logger.info(f"Collecting market data for sector: {sector}")
        
        try:
            results = await self._search_web(sector)
            
            market_data = MarketData(
                sector=sector,
                query=self._build_query(sector),
                results=results,
                collected_at=datetime.utcnow()
            )
            
            logger.info(f"Collected {len(results)} data points for {sector}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error collecting data for {sector}: {str(e)}")
            return MarketData(
                sector=sector,
                query=self._build_query(sector),
                results=[f"Unable to fetch real-time data. Error: {str(e)}"],
                collected_at=datetime.utcnow()
            )
    
    def _build_query(self, sector: str) -> str:
        # More specific queries for better results
        return f"{sector} sector India market analysis trends opportunities investment 2024 2025 trade export import"
    
    async def _search_web(self, sector: str) -> List[str]:
        try:
            from duckduckgo_search import DDGS
            
            query = self._build_query(sector)
            results = []
            
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    max_results=self.max_results
                )
                
                for result in search_results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    url = result.get('href', '')
                    
                    # Format results with more context
                    if title and body:
                        formatted_result = f"**{title}**\n{body}"
                        if url:
                            formatted_result += f"\nSource: {url}"
                        results.append(formatted_result)
                    elif title:
                        results.append(f"**{title}**")
                    elif body:
                        results.append(body)
            
            return results if results else self._get_fallback_data(sector)
            
        except ImportError:
            logger.warning("DuckDuckGo search not available, using fallback data")
            return self._get_fallback_data(sector)
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return self._get_fallback_data(sector)
    
    def _get_fallback_data(self, sector: str) -> List[str]:
        return [
            f"The {sector} sector in India has shown significant growth potential.",
            f"Recent market trends indicate increasing investment in {sector}.",
            f"Government initiatives are supporting {sector} development.",
            f"Export opportunities exist for {sector} products and services.",
            f"Digital transformation is reshaping the {sector} industry.",
        ]


data_collector = DataCollector()
