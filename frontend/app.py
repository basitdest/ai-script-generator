import streamlit as st
import requests
import json
import os

from dotenv import load_dotenv
from pathlib import Path

# Load .env file from one directory up (repo root)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ---------------- CONFIG ----------------
OLLAMA_URL = "https://nonvigilant-rubie-nondynamically.ngrok-free.dev/api/generate"
OLLAMA_MODEL = "codellama:7b"

# Small free model from Hugging Face for online demo
HF_MODEL = os.getenv("HF_MODEL", "")
HF_BASE_URL = os.getenv("HF_BASE_URL", "")
HF_TOKEN = os.getenv("HF_API_KEY", "")
# ----------------------------------------

st.set_page_config(page_title="🤖 AI Script Generator", layout="centered")
st.title("🤖 AI-Powered Script Generator")
st.markdown("Generate **Python** or **PowerShell** scripts from natural language using AI models.")

language = st.selectbox("Select script language:", ["Python", "PowerShell"])
prompt = st.text_area("🧠 Describe your task:", placeholder="e.g. Fetch the last OTP email and save it in a text file...")


HF_API_URL = f"{HF_BASE_URL.rstrip('/')}/{HF_MODEL}"

# --- HELPER: Detect if Ollama (via ngrok) is live ---
def ollama_running():
    try:
        res = requests.get(OLLAMA_URL.replace("/api/generate", "/api/tags"), timeout=3)
        return res.status_code == 200
    except Exception:
        return False

# --- HELPER: Generate via Ollama ---
def generate_via_ollama(prompt, language):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Generate a {language} script for this task:\n{prompt}\n"
                  f"Respond with sections:\n"
                  f"1. Problem\n2. Tech Used\n3. Libraries/Prerequisites\n4. Script Code\n"
                  f"Format cleanly in Markdown."
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=90)
        text = ""
        for line in resp.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                text += data.get("response", "")
        return text.strip() or "⚠️ No response received from Ollama."
    except Exception as e:
        return f"❌ Ollama error: {e}"

# --- HELPER: Generate via Hugging Face (fallback) ---
def generate_via_hf(prompt, language):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {
        "inputs": f"Generate a {language} automation script for: {prompt}\n"
                  f"Provide structured sections:\n"
                  f"1. Problem\n2. Tech Used\n3. Libraries/Prerequisites\n4. Script Code"
    }
    try:
        resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            return str(data)
        return f"⚠️ HF API Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"❌ Hugging Face error: {e}"

# --- Streamlit UI ---
st.title("🤖 AI Script Generator")
st.caption("Generate automation scripts using your local Ollama or fallback model online.")

prompt = st.text_area("💬 Describe the task:", placeholder="e.g., Automate file renaming in a folder")
language = st.selectbox("💻 Select script language:", ["Python", "Bash", "JavaScript"])

if st.button("🚀 Generate Script"):
    if not prompt.strip():
        st.warning("Please enter a task description.")
    else:
        with st.spinner("Generating your script... ⏳"):
            if ollama_running():
                st.info("Using local Codellama model via Ollama (ngrok tunnel).")
                output = generate_via_ollama(prompt, language)
            else:
                st.warning("Ollama not detected. Using Hugging Face fallback.")
                output = generate_via_hf(prompt, language)

            st.markdown("### ✅ Generated Output")
            st.markdown(output)

            st.download_button(
                label="💾 Download Script",
                data=output,
                file_name=f"generated_{language.lower()}.txt",
                mime="text/plain",
            )
```
