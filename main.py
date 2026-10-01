import os
import sys
from dotenv import load_dotenv
from google import genai

# 1. Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

# 2. Instantiate the client
client = genai.Client(api_key=api_key)

# 3. Model identifier that is verified working on your key
MODEL_ID = "gemma-4-26b-a4b-it"


def run_assistant() -> None:
    """Runs the primary text conversational loop for the assistant."""
    print("=" * 60)
    print(" MAX AI Assistant (Stage 1: Operational)")
    print(f" Connected Model: {MODEL_ID}")
    print(" Type 'exit', 'quit', or 'q' to end the session.")
    print("=" * 60)

    # Initialize a clean stateful chat session without unsupported system configs
    chat = client.chats.create(model=MODEL_ID)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("MAX: Goodbye, Boss! Shutting down.")
                break

            response = chat.send_message(user_input)
            print(f"\nMAX: {response.text}")

        except KeyboardInterrupt:
            print("\nMAX: Session interrupted. Exiting safely.")
            break
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_assistant()