import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# These are the exact models reported as active on your key
candidates = [
    "gemini-flash-latest",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
]

for model_name in candidates:
    print(f"Testing {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'MAX AI is online!' in 5 words."
        )
        print(f"\n[SUCCESS] Connected to {model_name}!")
        print(f"Response: {response.text}\n")
        break
    except Exception as e:
        print(f"Failed with {model_name}: {e}\n")
        time.sleep(1)