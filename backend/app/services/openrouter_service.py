"""
OpenRouter AI Service - unified access to GPT-4o, Claude, Gemini via openrouter.ai
Used for drawer image analysis in the calculator
"""
import os
import json
import base64
import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Default vision model — free tier with vision support
VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "google/gemini-2.0-flash-exp:free")

SYSTEM_PROMPT = """Ти — досвідчений технолог меблевого виробництва.
Клієнт або менеджер надсилає тобі фото або ескіз шухляди / корпусу з шухлядами.

Твоє завдання — проаналізувати зображення та повернути ТІЛЬКИ валідний JSON без жодного тексту навколо.

Формат відповіді:
{
  "drawer_count": <ціле число кількості шухляд, від 1 до 8>,
  "direction": <"vertical" якщо шухляди одна під одною, "horizontal" якщо поряд>,
  "facade_type": <"overlay" якщо фасад накладний, "inset" якщо врізний, "none" якщо без фасаду>,
  "approx_width": <приблизна ширина корпусу в мм, наприклад 600>,
  "approx_height": <приблизна висота корпусу в мм, наприклад 720>,
  "approx_depth": <приблизна глибина корпусу в мм, наприклад 500>,
  "drawer_depth": <приблизна глибина шухляди в мм, наприклад 450>,
  "confidence": <"high" або "low" — наскільки ти впевнений у своєму аналізі>,
  "notes": <короткий коментар що ти побачив, 1 речення українською>
}

Якщо не можеш визначити — використовуй стандартні значення: 1 шухляда, vertical, overlay, 600x720x500, depth 450."""


async def analyze_drawer_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Send image to OpenRouter for furniture analysis.
    Returns parsed JSON with drawer configuration.
    """
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set, returning default values")
        return _default_response("API ключ не налаштовано")

    # Encode image to base64
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{b64_image}"

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": "Проаналізуй це зображення меблів з шухлядами та поверни JSON."
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://erp.local",
        "X-Title": "Drawer Calculator"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            raw_text = data["choices"][0]["message"]["content"].strip()

            # Extract JSON from response (model sometimes wraps in markdown)
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            result = json.loads(raw_text)
            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
        return _default_response(f"Помилка API: {e.response.status_code}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return _default_response("Не вдалось розпізнати відповідь AI")
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return _default_response(str(e))


def _default_response(notes: str) -> dict:
    return {
        "drawer_count": 1,
        "direction": "vertical",
        "facade_type": "overlay",
        "approx_width": 600,
        "approx_height": 720,
        "approx_depth": 500,
        "drawer_depth": 450,
        "confidence": "low",
        "notes": notes
    }
