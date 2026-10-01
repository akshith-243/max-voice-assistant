import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Fetching available models for your API key...\n")
try:
    for model in client.models.list():
        # Filter for models that support text/content generation
        if "generateContent" in (model.supported_actions or []):
            # Print just the clean model identifier
            print(f"- {model.name}")
except Exception as e:
    print(f"Error fetching models: {e}")