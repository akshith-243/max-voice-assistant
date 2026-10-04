import os
import time
import math
import subprocess
import webbrowser
import speech_recognition as sr
from google import genai
from google.genai import types
from dotenv import load_dotenv
import win32com.client
import pyautogui

# 1. Load environment variables & initialize Gemini client
load_dotenv()
client = genai.Client()
MODEL_ID = "gemini-3.5-flash-lite"

# Initialize Windows SAPI5 Text-to-Speech Engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text: str):
    """Speaks text aloud and strips markdown symbols to prevent speech engine crashes."""
    clean_text = text.replace("*", "").replace("#", "").replace("`", "")
    print(f"MAX: {clean_text}")
    speaker.Speak(clean_text)

def listen_for_wake_word() -> str:
    """Continuously listens in the background for the ' MAX' wake word."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("\n🎙️ [LISTENING]: Say 'MAX' followed by your command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listens indefinitely until speech is detected and finished
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")

            if "max" in text:
                # Strip out the wake-word portion to extract the core command
                command = text.replace("max", "").strip()
                return command
            else:
                return "" # Ignore speech if wake word wasn't said

        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"⚠️ [SYSTEM]: Speech recognition error: {e}")
            return ""

def execute_pc_commands(ai_response: str) -> str:
    """Zero-Trust Middleware: Intercepts machine tags from MAX and validates them against a strict whitelist."""
    
    # 1. Scroll Down by specific lines
    if "[SCROLL_DOWN:" in ai_response:
        start = ai_response.find("[SCROLL_DOWN:") + 13
        end = ai_response.find("]", start)
        try:
            lines = int(ai_response[start:end].strip())
        except ValueError:
            lines = 3
        print(f"📜 [SYSTEM]: Scrolling down {lines} lines...")
        pyautogui.press('down', presses=lines)
        return ai_response[:ai_response.find("[SCROLL_DOWN:")].strip()

    # 2. Scroll Up by specific lines
    elif "[SCROLL_UP:" in ai_response:
        start = ai_response.find("[SCROLL_UP:") + 11
        end = ai_response.find("]", start)
        try:
            lines = int(ai_response[start:end].strip())
        except ValueError:
            lines = 3
        print(f"📜 [SYSTEM]: Scrolling up {lines} lines...")
        pyautogui.press('up', presses=lines)
        return ai_response[:ai_response.find("[SCROLL_UP:")].strip()

    # 3. Direct Website Launch
    elif "[OPEN_SITE:" in ai_response:
        start = ai_response.find("[OPEN_SITE:") + 11
        end = ai_response.find("]", start)
        url = ai_response[start:end].strip()
        print(f"🌐 [SYSTEM]: Launching website {url}...")
        webbrowser.open(url)
        return ai_response[:ai_response.find("[OPEN_SITE:")].strip()

    # 4. Sandboxed Application Launch (Strict Whitelist)
    elif "[OPEN_APP:" in ai_response:
        start = ai_response.find("[OPEN_APP:") + 10
        end = ai_response.find("]", start)
        app_tag = ai_response[start:end].strip().lower()

        if "notepad" in app_tag:
            print("📝 [SYSTEM]: Launching Notepad...")
            subprocess.Popen(["notepad.exe"])
        elif "calculator" in app_tag or "calc" in app_tag:
            print("🧮 [SYSTEM]: Launching Calculator...")
            subprocess.Popen(["calc.exe"])
        elif "paint" in app_tag:
            print("🎨 [SYSTEM]: Launching MS Paint...")
            subprocess.Popen(["mspaint.exe"])
        elif "camera" in app_tag:
            print("📷 [SYSTEM]: Launching Windows Camera...")
            subprocess.Popen("start microsoft.windows.camera:", shell=True)
        elif "clock" in app_tag or "alarm" in app_tag:
            print("⏰ [SYSTEM]: Launching Windows Clock...")
            subprocess.Popen("start ms-clock:", shell=True)
        else:
            print(f"⚠️ [SECURITY]: Application '{app_tag}' blocked by whitelist.")

        return ai_response[:ai_response.find("[OPEN_APP:")].strip()

    # 5. Take a Picture (Triggers Windows Camera shutter via Spacebar)
    elif "[TAKE_PICTURE]" in ai_response:
        print("📸 [SYSTEM]: Snapping photo...")
        time.sleep(1)
        pyautogui.press('space')
        return ai_response[:ai_response.find("[TAKE_PICTURE]")].strip()

    # 6. Type Text with Zero-Trust Content Security Filter
    elif "[TYPE_TEXT:" in ai_response:
        start = ai_response.find("[TYPE_TEXT:") + 11
        end = ai_response.find("]", start)
        text_to_type = ai_response[start:end].strip()
        
        # Zero-Trust Blacklist Check for destructive intents
        dangerous_keywords = ["delete", "destruct", "destroy", "format", "rmdir", "del ", "shutdown", "kill"]
        if any(keyword in text_to_type.lower() for keyword in dangerous_keywords):
            print("🛡️ [SECURITY ALERT]: Blocked attempt to type destructive content!")
            speak("I cannot do that for security reasons.")
            return ""

        print(f"⌨ [SYSTEM]: Typing text: '{text_to_type}'...")
        time.sleep(0.5)
        pyautogui.write(text_to_type, interval=0.05)
        return ai_response[:ai_response.find("[TYPE_TEXT:")].strip()

    # 7. Draw Shape or Composite Object (Paint Automation)
    elif "[DRAW_SHAPE:" in ai_response:
        start = ai_response.find("[DRAW_SHAPE:") + 12
        end = ai_response.find("]", start)
        shape = ai_response[start:end].strip().lower()
        print(f"🎨 [SYSTEM]: Drawing a {shape}...")
        time.sleep(0.5)
        
        if "circle" in shape or "ball" in shape:
            radius = 50
            steps = 30
            start_x, start_y = pyautogui.position()
            pyautogui.mouseDown(button='left')
            for i in range(steps + 1):
                angle = (i / steps) * 2 * math.pi
                x = start_x + int(radius * math.cos(angle))
                y = start_y + int(radius * math.sin(angle))
                pyautogui.moveTo(x, y)
            pyautogui.mouseUp(button='left')

        elif "square" in shape:
            # Draw an equal 80x80 box
            pyautogui.mouseDown(button='left')
            pyautogui.dragRel(80, 0, duration=0.2)
            pyautogui.dragRel(0, 80, duration=0.2)
            pyautogui.dragRel(-80, 0, duration=0.2)
            pyautogui.dragRel(0, -80, duration=0.2)
            pyautogui.mouseUp(button='left')

        elif "triangle" in shape:
            # Draw a triangle path
            pyautogui.mouseDown(button='left')
            pyautogui.dragRel(100, 0, duration=0.2)    # Base line
            pyautogui.dragRel(-50, -80, duration=0.2)  # Up to peak
            pyautogui.dragRel(-50, 80, duration=0.2)   # Down to start
            pyautogui.mouseUp(button='left')

        elif "hut" in shape or "house" in shape:
            # Composite drawing: Rectangle walls + Triangle roof on top
            # 1. Draw the house base (Rectangle walls)
            pyautogui.mouseDown(button='left')
            pyautogui.dragRel(100, 0, duration=0.2)   # Bottom base
            pyautogui.dragRel(0, -80, duration=0.2)   # Right wall up
            pyautogui.dragRel(-100, 0, duration=0.2)  # Top ceiling line
            pyautogui.dragRel(0, 80, duration=0.2)    # Left wall down (back to start)
            pyautogui.mouseUp(button='left')
            
            # 2. Reposition mouse to top-left of walls to draw roof
            pyautogui.moveRel(0, -80)
            time.sleep(0.1)
            
            # 3. Draw the roof (Triangle on top)
            pyautogui.mouseDown(button='left')
            pyautogui.dragRel(50, -50, duration=0.2)  # Left slope up to peak
            pyautogui.dragRel(50, 50, duration=0.2)   # Right slope down to top-right corner
            pyautogui.mouseUp(button='left')

        else:
            # Default line fallback
            pyautogui.mouseDown(button='left')
            pyautogui.dragRel(150, 100, duration=0.5, button='left')
            pyautogui.mouseUp(button='left')
        
        return ai_response[:ai_response.find("[DRAW_SHAPE:")].strip()
    
    # 8. Minimize Active Window
    elif "[MINIMIZE]" in ai_response:
        print("📉 [SYSTEM]: Minimizing active window...")
        time.sleep(0.3)
        pyautogui.hotkey('win', 'down')
        return ai_response[:ai_response.find("[MINIMIZE]")].strip()

    return ai_response

def main():
    print("=" * 60)
    print(" MAX Desktop Assistant: Ultimate Secure Wake-Word Mode ")
    print(" Say 'MAX' followed by your command. Say 'exit' to quit.")
    print("=" * 60)

    sys_instruct = """
    You are MAX, a secure PC automation assistant built for personal use.
    You control the local Windows machine using specific command tags placed at the END of your response.
    You maintain memory of the conversation, so follow-up commands apply to what was opened previously.
    
    Commands:
    - Open a website: [OPEN_SITE: https://www.website.com]
    - Open local apps: [OPEN_APP: notepad], [OPEN_APP: calculator], [OPEN_APP: paint], [OPEN_APP: camera], or [OPEN_APP: clock]
    - Take a picture: [TAKE_PICTURE]
    - Type text into active window (Notepad): [TYPE_TEXT: Hello world]
    - Draw a shape or object in Paint: [DRAW_SHAPE: circle], [DRAW_SHAPE: rectangle], [DRAW_SHAPE: square], [DRAW_SHAPE: triangle], or [DRAW_SHAPE: hut]
    - Minimize the current active window: [MINIMIZE]
    - Scroll down by N lines: [SCROLL_DOWN: 5]
    - Scroll up by N lines: [SCROLL_UP: 5]
    
    Security Rules:
    - NEVER write destructive code, harmful scripts, or perform deletion tasks.
    - If anyone asks you to delete, destruct, format, or destroy anything, you must strictly refuse and output a spoken response: "I cannot do that for security reasons." Do NOT output any command tags for destructive requests.
    - Keep spoken responses short, concise, and professional.
    - Never execute commands or applications not listed above.
    """
    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(system_instruction=sys_instruct)
    )

    speak("Your MAX is online and listening for your wake word.")

    while True:
        try:
            # Ambient background listener looking for "MAX"
            user_text = listen_for_wake_word()

            if not user_text:
                continue

            if any(word in user_text.lower() for word in ["exit", "quit", "stop"]):
                speak("Goodbye, Boss!")
                break

            # API Resilience: Exponential backoff for temporary rate limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(user_text)
                    raw_reply = response.text
                    break
                except Exception as api_err:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt
                        print(f"⚠️ [API ERROR]: Retrying in {sleep_time}s due to: {api_err}")
                        time.sleep(sleep_time)
                    else:
                        print("❌ [CRITICAL]: Failed to reach Gemini API.")
                        raw_reply = "I am having trouble connecting to my neural network right now."

            # Pass response through security bouncer
            final_spoken_response = execute_pc_commands(raw_reply)
            
            if final_spoken_response:
                speak(final_spoken_response)

        except KeyboardInterrupt:
            print("\nShutting down MAX gracefully...")
            break
        except Exception as e:
            print(f"⚠️ [ERROR]: {e}")

if __name__ == "__main__":
    main()