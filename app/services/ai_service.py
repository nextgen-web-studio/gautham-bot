from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.ai_api_key, base_url=settings.ai_base_url)
# Default model, you can override depending on the provider
MODEL = "gemini-3.5-flash" # Or compatible

async def _call_ai(system_prompt: str, user_prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        import logging
        logging.error(f"AI API Error: {e}")
        return "⚠️ Something went wrong while processing your request. Please try again."

async def ask_ai(question: str) -> str:
    return await _call_ai("You are NextGen AI Assistant, a helpful, professional, and concise assistant.", question)

async def summarize_text(text: str) -> str:
    prompt = "Summarize the following text, providing the main point, important details, and key conclusions."
    return await _call_ai(prompt, text)

async def rewrite_text(text: str, style: str) -> str:
    prompt = f"Rewrite the following text in a {style} style while preserving its original meaning, names, numbers, and facts."
    return await _call_ai(prompt, text)

async def correct_grammar(text: str) -> str:
    prompt = "Correct grammar, spelling, punctuation, and clarity of the following text. Output ONLY the corrected text, followed by a brief '### Changes' section explaining major corrections."
    return await _call_ai(prompt, text)

async def generate_content(instructions: str) -> str:
    prompt = "You are a creative content generator. Generate useful content based on the following instructions."
    return await _call_ai(prompt, instructions)

async def translate_text(text: str, target_language: str) -> str:
    prompt = f"Translate the following text to {target_language}. Preserve the meaning and formatting of the original text."
    return await _call_ai(prompt, text)

async def change_tone(text: str, tone: str) -> str:
    prompt = f"Rewrite the following text using a {tone} tone."
    return await _call_ai(prompt, text)
