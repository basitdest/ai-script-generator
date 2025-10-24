import os
import requests
import logging

# Toggle between local Ollama or Hugging Face API
USE_OLLAMA = True

# Hugging Face config (optional)
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_BASE_URL = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co/models")

# Ollama endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_script(prompt: str, language: str = "python") -> str:
    """
    Generate a structured AI response with:
    - Problem statement
    - Libraries required
    - Script code
    - Explanation
    """

    system_prompt = f"""
You are an expert automation engineer. When asked to generate a script, always respond in this exact structured format:

**Problem:** <2-3 lines summary of the task>
**Tech Used:** <language + libraries>
**Script:**
```{language}
# code here
