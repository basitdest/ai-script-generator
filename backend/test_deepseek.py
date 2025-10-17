from model_client import generate_script

if __name__ == "__main__":
    print("Testing DeepSeek generation...")
    prompt = "Create a Python script that checks if a website is up and logs the result every minute."
    print(generate_script(prompt, language="python"))
