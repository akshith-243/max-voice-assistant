import os
from dotenv import load_dotenv
from google import genai

# Load your API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("🔍 Searching your account for available Flash models...\n")

try:
    for model in client.models.list():
        if "flash" in model.name.lower():
            print(f"✅ {model.name}")
except Exception as e:
    print(f"Error fetching models: {e}")