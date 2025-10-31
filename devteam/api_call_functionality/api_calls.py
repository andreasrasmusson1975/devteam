import aiohttp
import asyncio
import requests
import json

async def get_chat_response(
    system_prompt: str,
    user_prompt: str,
    which_model: int,
    model_name: str,
    temperature: float = 0.7,
    top_p: float = 0.8,
    max_tokens: int = 16384,
    base_url: str = "http://127.0.0.1",
    timeout: int = 960,
) -> str:
    base = base_url.rstrip("/")
    url = f"{base}:18000/v1/chat/completions"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens,
        "top_p": top_p,
    }

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            async with session.post(url, json=payload) as resp:
                text = await resp.text()
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}: {text}")

                try:
                    data = json.loads(text)
                    return data["choices"][0]["message"]["content"]
                except (KeyError, ValueError, json.JSONDecodeError):
                    raise RuntimeError(f"Bad response format: {text}")

    except aiohttp.ClientError as e:
        raise RuntimeError(f"Request error: {e}") from e