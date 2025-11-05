import streamlit as st
import requests
import json
import os

# ---------------- CONFIG ----------------
OLLAMA_URL = "https://nonvigilant-rubie-nondynamically.ngrok-free.dev/api/generate"
OLLAMA_MODEL = "codellama:7b"

# Small free model from Hugging Face for online demo
HF_MODEL = "bigcode/starcoderbase"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_TOKEN = os.getenv("HF_API_KEY", "")  # optional
# ----------------------------------------

st.set_page_config(page_title="🤖 AI Script Generator", layout="centered")
st.title("🤖 AI-Powered Script Generator")
st.markdown("Generate **Python** or **PowerShell** scripts from natural language using AI models.")

language = st.selectbox("Select script language:", ["Python", "PowerShell"])
prompt = st.text_area("🧠 Describe your task:", placeholder="e.g. Fetch the last OTP email and save it in a text file...")

# --- HELPER: Detect if Ollama is running ---
def ollama_running():
    try:
        res = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return res.status_code == 200
    except:
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
    resp = requests.post(OLLAMA_URL, json=payload, stream=True)
    text = ""
    for line in resp.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            text += data.get("response", "")
    return text.strip()

# --- HELPER: Generate via Hugging Face ---
def generate_via_hf(prompt, language):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {
        "inputs": f"Generate a {language} automation script for: {prompt}\n"
                  f"Provide structured sections:\n"
                  f"1. Problem\n2. Tech Used\n3. Libraries/Prerequisites\n4. Script Code"
    }
    resp = requests.post(HF_API_URL, headers=headers, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list) and len(data) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)
    return f"⚠️ HF API Error {resp.status_code}: {resp.text}"

# --- Main generation logic ---
if st.button("🚀 Generate Script"):
    if not prompt.strip():
        st.warning("Please enter a task description.")
    else:
        with st.spinner("Generating your script... ⏳"):
            try:
                if ollama_running():
                    st.info("Using local Codellama model via Ollama.")
                    output = generate_via_ollama(prompt, language)
                else:
                    st.info("Using Hugging Face fallback model (online demo mode).")
                    output = generate_via_hf(prompt, language)

                st.markdown("### ✅ Generated Output")
                st.markdown(output)

                st.download_button(
                    label="💾 Download Script",
                    data=output,
                    file_name=f"generated_{language.lower()}.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")
