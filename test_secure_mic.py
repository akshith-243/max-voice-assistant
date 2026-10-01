import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_when_prompted():
    print("\n" + "=" * 50)
    input("🔒 Mic is OFF. Press [ENTER] when you are ready to speak...")
    
    with sr.Microphone() as source:
        print("🎤 [MIC ACTIVE] Adjusting for room noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        print("🗣️ Listening now... Speak your prompt!")
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🔒 [MIC CLOSED] Processing speech...")
            
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⚠️ No speech detected within the time limit. Mic closed.")
        except sr.UnknownValueError:
            print("⚠️ Could not understand the audio.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    listen_when_prompted()