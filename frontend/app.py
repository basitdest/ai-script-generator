import streamlit as st
import requests
import json

# ---------- CONFIG ----------
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"  # Ollama local API
MODEL_NAME = "codellama:7b"
# ----------------------------

st.set_page_config(
    page_title="AI Script Generator",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI-Powered Script Generator")
st.markdown("Generate **Python** or **PowerShell** scripts from natural language using local LLMs.")

# Language dropdown
language = st.selectbox("Select script language:", ["Python", "PowerShell"])

# User input area
prompt = st.text_area("🧠 Describe your task:", placeholder="e.g. Fetch the last OTP email and save it in a text file...")

# Button to generate
if st.button("🚀 Generate Script"):
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Generating your script... ⏳"):
            try:
                # Send prompt to Ollama
                payload = {
                    "model": MODEL_NAME,
                    "prompt": f"Generate a {language} script for the following task:\n{prompt}\n"
                              f"Respond with sections:\n"
                              f"1. **Problem**\n2. **Tech Used**\n3. **Libraries/Prerequisites**\n4. **Script Code**\n"
                              f"Format clearly and in Markdown."
                }

                response = requests.post(OLLAMA_URL, json=payload, stream=True)

                output_text = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        output_text += data.get("response", "")

                st.markdown("### ✅ Generated Output")
                st.markdown(output_text)

                # Option to download
                st.download_button(
                    label="💾 Download Script",
                    data=output_text,
                    file_name=f"generated_{language.lower()}.txt",
                    mime="text/plain",
                )

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to Ollama. Please ensure Ollama is running on localhost:11434.")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")
