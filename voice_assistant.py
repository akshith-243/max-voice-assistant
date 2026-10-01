import os
import sys
import time
import webbrowser
import subprocess
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from google import genai
from google.genai import types
import win32com.client

# 1. Initialize environment & API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] GEMINI_API_KEY missing from .env file.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-3.5-flash-lite"  # Change this to whatever model name you are currently using

# 2. Configure Windows Native TTS Engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text: str):
    """Outputs text through the local system speakers."""
    print(f"\nMAX: {text}")
    clean_text = text.replace("*", "").replace("#", "").replace("_", "")
    try:
        speaker.Speak(clean_text)
    except Exception as e:
        print(f"⚠️ [Voice Error]: {e}")

# 3. Configure Speech Recognizer
recognizer = sr.Recognizer()

def push_to_talk() -> str:
    """Records 3 seconds of audio using sounddevice."""
    print("\n" + "-" * 50)
    input("🔒 [MIC LOCKED] Press [ENTER] to talk to MAX...")
    
    fs = 44100
    seconds = 3
    
    print("🎤 [MIC ACTIVE] Listening for 3 seconds... Speak now!")
    
    try:
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("🔒 [MIC CLOSED] Processing audio...")
        
        temp_file = "temp_mic.wav"
        write(temp_file, fs, recording)
        
        with sr.AudioFile(temp_file) as source:
            audio_data = recognizer.record(source)
            query = recognizer.recognize_google(audio_data)
            print(f"You (Voice): {query}")
            
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return query
        
    except sr.UnknownValueError:
        speak("Sorry, I could not understand the audio.")
        return ""
    except Exception as e:
        print(f"⚠️ Audio capture error: {e}")
        return ""

# 4. PC Automation Interceptor
def execute_pc_commands(ai_response: str) -> str:
    """Intercepts secret command tags from MAX and controls Windows."""
    
    # Check for Website Commands
    if "[OPEN_SITE:" in ai_response:
        start = ai_response.find("[OPEN_SITE:") + 11
        end = ai_response.find("]", start)
        url = ai_response[start:end].strip()
        
        print(f"🌐 [SYSTEM]: Launching browser to {url}...")
        webbrowser.open(url)
        
        # Remove tag before speaking
        return ai_response[:ai_response.find("[OPEN_SITE:")]
        
    # Check for App Commands
    elif "[OPEN_APP:" in ai_response:
        app_tag = ai_response[ai_response.find("[OPEN_APP:") + 10 : ai_response.find("]", ai_response.find("[OPEN_APP:"))].strip().lower()
        
        if "notepad" in app_tag:
            print("📝 [SYSTEM]: Opening Notepad...")
            subprocess.Popen(["notepad.exe"])
        elif "calculator" in app_tag or "calc" in app_tag:
            print("🧮 [SYSTEM]: Opening Calculator...")
            subprocess.Popen(["calc.exe"])
            
        # Remove tag before speaking
        return ai_response[:ai_response.find("[OPEN_APP:")]
        
    return ai_response

def main():
    print("=" * 60)
    print(" MAX Desktop Assistant: PC Automation Mode")
    print(" Press ENTER to speak for 3 seconds. Type 'exit' to quit.")
    print("=" * 60)

    # 5. Give MAX his automation rules
    sys_instruct = """
    You are MAX, a voice assistant built for the Smart India Hackathon.
    You have the ability to control the user's Windows PC.
    - If the user asks you to open a website (like YouTube, Google, or a demo site), you MUST include the exact tag [OPEN_SITE: https://www.website.com] at the end of your response.
    - If the user asks you to open Notepad or Calculator, you MUST include the exact tag [OPEN_APP: notepad] or [OPEN_APP: calculator] at the end of your response.
    Keep your spoken responses very short, cool, and professional.
    """
    
    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(system_instruction=sys_instruct)
    )
    
    speak(" MAX is online with PC automation enabled to help you, user. ")

    while True:
        try:
            user_text = push_to_talk()

            if not user_text:
                continue

            if user_text.lower() in ["exit", "quit", "stop"]:
                speak("Goodbye, Boss!")
                break

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(user_text)
                    
                    # Intercept any PC commands before speaking!
                    clean_response = execute_pc_commands(response.text)
                    speak(clean_response)
                    
                    break  # Success! Exit the retry loop
                
                except Exception as e:
                    error_msg = str(e)
                    
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        print("\n⚠️ [RATE LIMIT]: Free tier limit hit. Cooldown required.")
                        speak("I am hitting my free tier limits. Please give me a minute to cool down.")
                        break
                        
                    elif "503" in error_msg and attempt < max_retries - 1:
                        print(f"⚠️ Google server busy. Retrying... ({attempt + 1}/{max_retries})")
                        time.sleep(2)
                        
                    else:
                        print(f"\n[API ERROR]: {e}")
                        speak("I am having trouble connecting to the server right now.")
                        break

        except KeyboardInterrupt:
            print("\nSession stopped.")
            break
        except Exception as e:
            print(f"[ERROR]: {e}")

if __name__ == "__main__":
    main()