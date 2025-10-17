import os
import requests
import logging

# -------------------------------------------------------------------
# DeepSeek-compatible API wrapper
# -------------------------------------------------------------------

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

if not DEEPSEEK_API_KEY:
    logging.warning("⚠️ DEEPSEEK_API_KEY not set. Please configure your .env file.")

SYSTEM_PROMPT_TEMPLATE = """
You are CodeGen — an AI assistant that converts natural language into working automation scripts.

You must always reply in the following structure:
1️⃣ A single code block containing only the script.
2️⃣ Immediately after, a JSON object describing metadata:
{
  "filename": "example.py",
  "language": "python",
  "description": "Short summary",
  "dependencies": ["requests","os"]
}

Rules:
- Only output code + metadata JSON (no extra explanation).
- Add clear logging statements inside the script.
- Use placeholders for credentials.
- Avoid destructive commands.
- Follow Python or PowerShell syntax depending on the language.
"""

def call_deepseek_api(messages, model="deepseek-chat", temperature=0.0, max_tokens=900):
    """
    Calls the DeepSeek chat API (OpenAI-compatible)
    """
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def generate_script(prompt: str, language: str = "python") -> str:
    """
    Generates a script (Python or PowerShell) using DeepSeek API.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
        {
            "role": "user",
            "content": f"Language: {language}\nInstruction: {prompt}\nReturn code + metadata JSON only.",
        },
    ]

    try:
        result = call_deepseek_api(messages)
        return result
    except Exception as e:
        logging.error(f"Error calling DeepSeek API: {e}")
        return f"Error: {e}"
