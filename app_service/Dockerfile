FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /app

# Expose the port the app runs on
EXPOSE 8008

# Run the application using Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8008", "--reload"]