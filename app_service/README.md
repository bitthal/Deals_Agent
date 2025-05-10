# Deals Agent API

A FastAPI-based API for deal agent mechanics and database insights.

## Project Structure

```
app_service/
├── api/                    # API package
│   ├── main.py            # Main FastAPI application
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # Pydantic models
│   └── dependencies/      # FastAPI dependencies
├── config/                # Configuration files
├── core/                  # Core functionality
├── logs/                  # Application logs
├── .env.example          # Example environment variables
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python run.py
```

## Docker Setup

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc

## Features

- Database statistics and schema inspection
- AI-powered deal suggestions
- RESTful API endpoints
- Docker support
- Comprehensive logging
- Environment-based configuration

## Development

- The application uses FastAPI for the web framework
- PostgreSQL for the database
- Google's Gemini AI for deal suggestions
- Docker for containerization
- Uvicorn as the ASGI server

## Logging

Logs are stored in the `logs` directory with daily rotation and a 30-day retention period. 