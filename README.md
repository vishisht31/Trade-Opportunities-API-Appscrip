# Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India.

## Features

- 🔍 **Market Analysis**: Collects and analyzes current market data for various sectors
- 🤖 **AI-Powered Insights**: Uses Google Gemini API for intelligent analysis
- 📊 **Structured Reports**: Generates comprehensive markdown reports
- 🔒 **Secure**: API key authentication and rate limiting
- ⚡ **Fast**: In-memory caching for improved performance
- 📝 **Well-Documented**: Interactive API documentation with Swagger UI

## Supported Sectors

The API accepts **any sector name**. Examples include:
- Pharmaceuticals
- Technology
- Agriculture
- Energy
- Finance
- Healthcare
- Manufacturing
- Retail
- Automotive
- Real Estate
- Fintech
- E-commerce
- And any other sector you want to analyze

Sector names are automatically sanitized and validated for security.

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Quick Start

### 1. Clone and Navigate

```bash
cd /Users/apple/Projects/Vishisht
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Required: Your Google Gemini API key
GEMINI_API_KEY=your-actual-gemini-api-key-here

# API keys for authentication (comma-separated)
API_KEYS=demo-key-1,demo-key-2,your-custom-key

# Rate limiting (requests per hour)
RATE_LIMIT_PER_HOUR=10

# Cache TTL in seconds
CACHE_TTL_SECONDS=3600
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Usage

### Authentication

All requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: demo-key-1" http://localhost:8000/analyze/pharmaceuticals
```

### Endpoints

#### GET /

API information and available endpoints

```bash
curl http://localhost:8000/
```

#### GET /health

Health check endpoint

```bash
curl http://localhost:8000/health
```

#### GET /analyze/{sector}

Analyze a specific sector and get trade opportunity insights

**Authentication**: Required

**Parameters**:
- `sector` (path): Any sector name (e.g., pharmaceuticals, technology, agriculture, automotive, real-estate, fintech, etc.)

**Response**: Structured markdown report

**Example**:

```bash
curl -H "X-API-Key: demo-key-1" \
  http://localhost:8000/analyze/pharmaceuticals
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "sector": "pharmaceuticals",
  "report": "# Trade Opportunities Analysis: Pharmaceuticals Sector\n\n...",
  "generated_at": "2025-12-18T14:30:00",
  "message": "Analysis completed successfully"
}
```

**Error Responses**:

- `400 Bad Request`: Invalid sector name
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Save Report to File

You can save the markdown report directly to a file:

```bash
curl -H "X-API-Key: demo-key-1" \
  http://localhost:8000/analyze/technology \
  | jq -r '.report' > technology_report.md
```

## Interactive Documentation

Visit the following URLs when the server is running:

- **Swagger UI**: http://localhost:8000/docs


These provide interactive API documentation where you can test endpoints directly.

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default Limit**: 10 requests per hour per API key
- **Headers**: Rate limit information is included in response headers:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## Caching

Analysis results are cached for 1 hour by default to improve performance and reduce API calls to external services.

## Architecture

The application follows clean architecture principles with clear separation of concerns:

```
app/
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration management
├── dependencies.py      # Dependency injection
├── models/
│   └── schemas.py       # Pydantic data models
├── services/
│   ├── data_collector.py   # Web search and data collection
│   ├── ai_analyzer.py      # Gemini API integration
│   └── report_generator.py # Markdown report generation
├── middleware/
│   ├── auth.py          # API key authentication
│   └── rate_limiter.py  # Rate limiting
└── utils/
    ├── cache.py         # In-memory caching
    └── validators.py    # Input validation
```

## Security Features

1. **API Key Authentication**: All analysis endpoints require valid API keys
2. **Rate Limiting**: Prevents API abuse with configurable limits
3. **Input Validation**: Sanitizes and validates all user inputs
4. **Input Sanitization**: Prevents injection attacks
5. **Error Handling**: Graceful error handling without exposing sensitive data

## Error Handling

The API implements comprehensive error handling:

- **External API Failures**: Falls back to cached data or generic insights
- **Invalid Input**: Clear validation messages
- **Rate Limiting**: Informative error with reset time
- **Authentication Errors**: Clear authentication requirements

## Development

### Project Structure

```
Vishisht/
├── app/                 # Application code
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── .env                # Your environment (not in git)
└── README.md           # This file
```

### Sector Support

The API now accepts **any sector name** automatically. Simply provide the sector name in the URL path, and it will be sanitized and validated for security. No configuration needed!

Examples:
- `/analyze/pharmaceuticals`
- `/analyze/automotive`
- `/analyze/real-estate`
- `/analyze/fintech`
- `/analyze/e-commerce`

### Logging

The application uses Python's built-in logging. Logs include:

- API requests and responses
- Authentication attempts
- Rate limiting events
- Data collection status
- AI analysis progress
- Errors and exceptions

## Testing

### Test Authentication

```bash
# Should fail (no API key)
curl http://localhost:8000/analyze/technology

# Should succeed
curl -H "X-API-Key: demo-key-1" http://localhost:8000/analyze/technology
```

### Test Rate Limiting

Make multiple requests rapidly to test rate limiting:

```bash
for i in {1..12}; do
  echo "Request $i:"
  curl -H "X-API-Key: demo-key-1" http://localhost:8000/analyze/pharmaceuticals
  echo "\n"
done
```

### Test Different Sectors

```bash
# Test each supported sector
for sector in pharmaceuticals technology agriculture energy finance healthcare manufacturing retail; do
  echo "Testing $sector..."
  curl -H "X-API-Key: demo-key-1" http://localhost:8000/analyze/$sector | jq '.success'
done
```

### Test Invalid Input

```bash
# Invalid sector
curl -H "X-API-Key: demo-key-1" http://localhost:8000/analyze/invalid-sector

# Invalid API key
curl -H "X-API-Key: invalid-key" http://localhost:8000/analyze/technology
```

## Troubleshooting

### Gemini API Key Issues

If you see "Gemini API key not configured":

1. Ensure you have a valid API key from Google AI Studio
2. Check that `GEMINI_API_KEY` is set in your `.env` file
3. Restart the server after updating `.env`

### DuckDuckGo Search Issues

If web search fails, the application will use fallback data. This is normal and the API will still function.

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Production Deployment

For production deployment:

1. **Use a production ASGI server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Set strong API keys**: Use secure, randomly generated keys

3. **Configure environment variables** securely (don't use .env in production)

4. **Enable HTTPS**: Use a reverse proxy (nginx, Caddy) with SSL

5. **Monitor logs**: Set up proper logging and monitoring

6. **Adjust rate limits**: Based on your requirements

## License

This project is created as a developer task demonstration.

## Support

For issues or questions:

1. Check the interactive documentation at `/docs`
2. Review the logs for error details
3. Ensure environment variables are correctly configured
4. Verify API keys are valid

---

**Built with FastAPI, Google Gemini AI, and modern Python best practices.**
