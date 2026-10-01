FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the FastAPI backend, which will now automatically start the Telegram Bot in the background!
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
