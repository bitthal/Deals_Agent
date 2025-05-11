FROM python:3.10-slim

WORKDIR /app

# Install curl for debugging
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /app/logs

# Copy the logger configuration and requirements
COPY requirements.txt .
COPY logger_config.py .

# Copy the agent code
COPY agents/event_processing_agent/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "event_processing_agent.py"]