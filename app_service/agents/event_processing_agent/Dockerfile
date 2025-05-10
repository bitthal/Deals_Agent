FROM python:3.10-slim

WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs

# Copy the logger configuration and requirements
COPY requirements.txt .
COPY logger_config.py .

# Copy the agent code
COPY agents/event_processing_agent/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "agent.py"]