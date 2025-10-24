import streamlit as st
from model_client import generate_script

st.set_page_config(page_title="AI Script Generator", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered Script Generator")
st.markdown("Turn natural language into working automation scripts instantly.")

st.markdown("### 1️⃣ Describe what you want your script to do")
prompt = st.text_area(
    "Your task:",
    placeholder="Example: Fetch the last OTP email and store it in a text file.",
    height=100,
)

st.markdown("### 2️⃣ Choose output language")
language = st.selectbox("Script language:", ["Python", "PowerShell", "Bash", "JavaScript"])

if st.button("⚡ Generate Script", use_container_width=True):
    if not prompt.strip():
        st.warning("Please enter a task description first.")
    else:
        with st.spinner("Generating your script..."):
            output = generate_script(prompt, language.lower())
        st.markdown("### 🧠 AI-Generated Script")
        st.markdown(output)