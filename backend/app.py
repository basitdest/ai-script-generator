from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.model_client import generate_script
from sandbox_runner import run_python_script, run_powershell_script
import os

app = FastAPI()

class GenRequest(BaseModel):
    prompt: str
    language: str = 'python'  # or 'powershell'
    run: bool = False

@app.post('/generate')
async def generate(req: GenRequest):
    if not req.prompt or len(req.prompt) < 3:
        raise HTTPException(400, 'Prompt is too short')
    res = generate_script(req.prompt, language=req.language)
    if res['safety_issues']:
        return {"ok": False, "error": "Safety checks failed", "safety_issues": res['safety_issues'], "raw": res['raw']}

    run_output = None
    if req.run:
        # Only allow local run if environment variable enabled
        if os.getenv('ALLOW_LOCAL_RUN', 'false').lower() != 'true':
            return {"ok": False, "error": "Local run disabled on server (security)."}
        if req.language.lower().startswith('py'):
            run_output = run_python_script(res['code'])
        else:
            run_output = run_powershell_script(res['code'])

    return {"ok": True, "code": res['code'], "meta": res['meta'], "run_output": run_output}