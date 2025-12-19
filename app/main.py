
from fastapi import FastAPI, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from app.config import settings
from app.models.schemas import AnalysisResponse, ErrorResponse
from app.services.data_collector import data_collector
from app.services.ai_analyzer import ai_analyzer
from app.services.report_generator import report_generator
from app.utils.cache import cache
from app.utils.validators import sanitize_sector_name, validate_sector_length, is_safe_input
from app.middleware.rate_limiter import rate_limiter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "endpoints": {
            "analyze": "/analyze/{sector}",
            "documentation": "/docs",
        },
        "authentication": "Not required",
        "rate_limit": f"{settings.rate_limit_per_hour} requests per hour per IP address",
        "sectors": "Accepts any sector name (e.g., pharmaceuticals, technology, automotive, real-estate, etc.)"
    }


@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "gemini_configured": bool(settings.gemini_api_key),
    }


@app.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    responses={
        200: {"model": AnalysisResponse},
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Analysis"]
)
async def analyze_sector(
    sector: str,
    request: Request,
    response: Response
):
    """
    Analyze market data and provide trade opportunity insights for a specific sector
    
    **Rate Limit**: 10 requests per hour per IP address
    
    **Sectors**: Accepts any sector name (e.g., pharmaceuticals, technology, agriculture, 
    automotive, real-estate, fintech, etc.). The sector name will be sanitized and validated 
    for security purposes.
    
    **Returns**: Structured markdown report with market analysis and trade opportunities
    
    **Example**:
    ```
    curl http://localhost:8000/analyze/pharmaceuticals
    curl http://localhost:8000/analyze/automotive
    curl http://localhost:8000/analyze/real-estate
    ```
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limiter.check_rate_limit(client_ip)
        
        headers = rate_limiter.get_rate_limit_headers(client_ip)
        for key, value in headers.items():
            response.headers[key] = value
        
        logger.info(f"Analyzing sector: {sector} for IP: {client_ip}")
        
        if not is_safe_input(sector):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sector name - potentially unsafe characters detected"
            )
        
        try:
            sanitized_sector = sanitize_sector_name(sector)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        length_error = validate_sector_length(sanitized_sector)
        if length_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=length_error
            )
        
        # Accept any sector - no whitelist restriction
        # Input validation and sanitization ensure security
        
        cache_key = cache.generate_key("analysis", sanitized_sector)
        cached_report = cache.get(cache_key)
        
        if cached_report:
            logger.info(f"Returning cached report for {sanitized_sector}")
            return AnalysisResponse(
                success=True,
                sector=sanitized_sector,
                report=cached_report,
                generated_at=datetime.utcnow().isoformat(),
                message="Analysis retrieved from cache"
            )
        
        logger.info(f"Step 1: Collecting market data for {sanitized_sector}")
        market_data = await data_collector.collect_market_data(sanitized_sector)
        
        logger.info(f"Step 2: Analyzing data with AI for {sanitized_sector}")
        analysis_result = await ai_analyzer.analyze_market_data(market_data)
        
        logger.info(f"Step 3: Generating markdown report for {sanitized_sector}")
        markdown_report = report_generator.generate_report(analysis_result)
        
        cache.set(cache_key, markdown_report, settings.cache_ttl_seconds)
        
        logger.info(f"Analysis completed successfully for {sanitized_sector}")
        
        return AnalysisResponse(
            success=True,
            sector=sanitized_sector,
            report=markdown_report,
            generated_at=datetime.utcnow().isoformat(),
            message="Analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sector {sector}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the sector: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            detail=None
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
