import os
import re
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

import openai
openai.api_key = OPENAI_API_KEY

# Safety blacklists (extend as necessary)
DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"Remove-Item\s+-Recurse",
    r"Format-Volume",
    r"shutdown",
    r":~\\",
    r"DeleteFile",
    r"Set-Content\s+-Path\s+C:\\",
]

def check_safety(code_text: str) -> list:
    matches = []
    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, code_text, re.IGNORECASE):
            matches.append(pat)
    return matches

SYSTEM_PROMPT_TEMPLATE = """
You are CodeGen, an assistant that outputs production-quality {language} automation scripts.
Requirements:
- Produce only the script file content inside triple backticks (```)
- Keep dependencies minimal and import-safe
- Add clear logging statements and comments
- Where external credentials are required, annotate using placeholders and DO NOT include secrets
- Output a small JSON block after the code with metadata: {{"filename":"...","runtime":"python3.10"}}
- Avoid destructive commands (no rm -rf, no format drives). If asked to manipulate files, prefer safe read/write within a provided path.

User instruction follows. Be robust to typos and ambiguous phrasing. If the user's request is impossible, respond with an explanation.
"""


def generate_script(prompt: str, language: str = 'python', max_tokens: int = 900) -> dict:
    role_system = SYSTEM_PROMPT_TEMPLATE.format(language=language.upper())
    user_prompt = f"Instruction: {prompt}\nReturn only the script content and metadata as described."

    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": role_system},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    text = resp['choices'][0]['message']['content']

    # Extract code block and optional JSON metadata
    code_block = None
    meta = None

    code_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text)
    if code_match:
        code_block = code_match.group(1).strip()

    # Try to find JSON metadata after code fences
    meta_match = re.search(r"\{\s*\"filename\"[\s\S]*\}", text)
    if meta_match:
        import json
        try:
            meta = json.loads(meta_match.group(0))
        except Exception:
            meta = None

    safety = check_safety(code_block or "")

    return {"raw": text, "code": code_block, "meta": meta, "safety_issues": safety}