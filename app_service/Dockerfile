FROM python:3.10-slim

WORKDIR /app

# Create logs directory and set permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose the port the app runs on
EXPOSE 8008

# Run the application using Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8008", "--reload"]