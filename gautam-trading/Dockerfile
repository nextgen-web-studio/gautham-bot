FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the backend and bot together, or just the bot.
# Assuming you just want to run the Telegram Bot for now:
CMD ["python", "bot/main.py"]
