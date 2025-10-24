from model_client import generate_script

print("Testing Hugging Face generation...")

res = generate_script(
    "Fetch the last OTP email and write the OTP to /tmp/last_otp.txt",
    language="python"
)

print("RESULT:", res)
