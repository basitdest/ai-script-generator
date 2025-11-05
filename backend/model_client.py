import requests, json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Ollama backend running successfully"}

@app.post("/generate")
async def generate_script(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    language = body.get("language", "python")

    payload = {
        "model": "codellama:7b",
        "prompt": f"Write a {language} script for this task: {prompt}",
    }

    try:
        response = requests.post("http://127.0.0.1:11434/api/generate", json=payload, stream=True)
        result = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                result += data.get("response", "")
        return {"ok": True, "result": result.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}