# backend/model_client.py
import os
import re
import json
import logging
from dotenv import load_dotenv
import requests

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "deepseek-ai/DeepSeek-Coder-V2-Instruct")
HF_BASE_URL = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co/models")

if not HF_API_KEY:
    logging.warning("⚠️ HF_API_KEY not set. Please configure your .env file with your Hugging Face token.")

SYSTEM_PROMPT = """
You are CodeGen — an assistant that converts natural language into robust automation scripts.
Return exactly:
1) A single triple-backtick code block containing only the script.
2) Immediately after the code block, a JSON object with metadata:
{
  "filename": "script.py",
  "language": "python",
  "description": "Short summary",
  "dependencies": ["imaplib"]
}
Rules:
- Use placeholders for secrets (DO NOT include real credentials).
- Add logging and helpful comments.
- Avoid dangerous commands (rm -rf, format, shutdown, etc).
- If the request is impossible, return an explanation inside the JSON `description` and an empty code block.
"""

# Simple blacklist of dangerous tokens
DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"Remove-Item\s+-Recurse",
    r"Format-Volume",
    r"shutdown",
    r"Format-Drive",
    r"DeleteFile",
]

def hf_inference(prompt: str, max_new_tokens: int = 800, temperature: float = 0.0):
    """
    Call Hugging Face Inference API for the configured model.
    """
    url = f"{HF_BASE_URL}/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            # you can tweak other model-specific parameters if needed
        },
    }
    # Many HF inference endpoints return a JSON list with a generated_text field.
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # data might be a list like [{"generated_text": "..."}] or plain text
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    # Some models / endpoints return plain dict or string
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    if isinstance(data, str):
        return data
    # try to serialize if unknown structure
    return json.dumps(data)

def parse_code_and_meta(llm_text: str):
    """
    Extract the first triple-backtick code block and the first JSON object after it.
    Returns (code_str, metadata_dict, raw_text)
    """
    code = ""
    meta = {}
    # find code block
    cb = re.search(r"```(?:\w+)?\n([\s\S]*?)```", llm_text)
    if cb:
        code = cb.group(1).strip()
    # find JSON object after code (first {...})
    jb = re.search(r"\{[\s\S]*\}", llm_text)
    if jb:
        try:
            meta = json.loads(jb.group(0))
        except Exception:
            # attempt to fix common python-style quotes etc
            try:
                cleaned = jb.group(0).replace("'", '"')
                meta = json.loads(cleaned)
            except Exception:
                meta = {}
    return code, meta, llm_text

def check_safety(code_text: str):
    matches = []
    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, code_text, re.IGNORECASE):
            matches.append(pat)
    return matches

def generate_script(prompt: str, language: str = "python"):
    """
    Generate a script (Python or PowerShell) using a Hugging Face LLM model.
    """

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }

    # Refined prompt for better structured output
    formatted_prompt = (
        f"Write a {language} script that accomplishes the following task:\n"
        f"Task: {prompt}\n"
        f"Include import statements, necessary libraries, and comments for clarity.\n"
        f"Provide the output in code block format only."
    )

    data = {"inputs": formatted_prompt}

    try:
        resp = requests.post(
            f"{HF_BASE_URL}/{HF_MODEL}",
            headers=headers,
            json=data,
            timeout=90
        )
        resp.raise_for_status()
        result = resp.json()

        # Some models return a list with 'generated_text', others return a dict
        if isinstance(result, list) and "generated_text" in result[0]:
            generated_code = result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            generated_code = result["generated_text"]
        else:
            generated_code = str(result)

        return {
            "ok": True,
            "code": generated_code.strip(),
            "raw": result
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling HF Inference: {e}")
        return {"ok": False, "error": str(e), "raw": None}
