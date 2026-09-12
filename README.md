# NextGen AI Assistant Bot

A production-ready Telegram AI assistant bot built with aiogram 3.x, FastAPI, and PostgreSQL.

## Features
- Ask AI questions
- Summarize text
- Rewrite text
- Correct grammar
- Generate content
- Translate text
- Change writing tone

## Installation
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in your variables.
3. Run `docker-compose up -d --build`.

## Deployment
Supports Webhook mode when `WEBHOOK_URL` is set, otherwise falls back to polling for local development.
