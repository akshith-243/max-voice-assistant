# MAX: Zero-Trust Voice Assistant

MAX is a Python-based, voice-controlled AI assistant powered by the Google Gemini API. Built with a focus on privacy and system security, MAX uses a strict Push-to-Talk architecture and a sandboxed PC automation layer to interact with the local operating system.

## 🚀 Core Features

- **Push-to-Talk Audio:** Bypasses always-on listening vulnerabilities by explicitly requiring a physical trigger before opening the microphone stream.
- **Resilient AI Pipeline:** Integrates with Google's Flash models and features built-in exponential backoff to automatically recover from 429 (Rate Limit) and 503 (Server Unavailable) API errors.
- **Zero-Trust PC Automation:** Instead of giving the LLM terminal access, MAX outputs machine-readable tags (e.g., `[OPEN_APP: notepad]`). A Python middleware layer intercepts these tags against a strict whitelist before executing local Windows processes.
- **Native Windows TTS:** Utilizes the rock-solid `win32com.client` (SAPI5) for seamless text-to-speech output, automatically stripping markdown to prevent voice engine crashes.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **AI/LLM:** Google Gemini API (`google-genai`)
- **Audio Capture:** `sounddevice` & `scipy`
- **Speech-to-Text:** `SpeechRecognition`
- **OS Control:** `subprocess` & `webbrowser`

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/akshith-243/max-voice-assistant.git](https://github.com/akshith-243/max-voice-assistant.git)
   cd max-voice-assistant