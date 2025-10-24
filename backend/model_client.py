import requests, json

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "codellama:7b"

def generate_script(prompt, language="Python"):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"Generate a {language} script for:\n{prompt}"
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            output += data.get("response", "")
    return output
