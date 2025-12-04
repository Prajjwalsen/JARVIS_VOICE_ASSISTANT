# Backend – Core AI Services

The backend powers JARVIS with model access, speech processing, and optional real-time search. This document explains each module, how they interact, and how to configure them.

---

## Modules

- `LLMProvider.py`
  - Purpose: Unified interface to your LLM provider(s)
  - Responsibilities: API calls, error handling, retries, response normalization
  - Configuration: reads `CohereAPIKey` from `.env`

- `Chatbot.py`
  - Purpose: Orchestrates conversation flow
  - Responsibilities: message history, tool usage (like search), response composition
  - Interfaces: calls `LLMProvider` and optionally `RealtimeSearchEngine`

- `SpeechToText.py`
  - Purpose: Transcribe microphone input to text
  - Responsibilities: audio capture, streaming, transcription
  - Notes: Ensure microphone permissions and device are correctly set

- `TextToSpeech.py`
  - Purpose: Convert text responses to voice
  - Responsibilities: synthesis, audio saving to `Data/`
  - Output: MP3 files stored locally (ignored by Git)

- `RealtimeSearchEngine.py`
  - Purpose: Augment answers with current web information
  - Responsibilities: query execution, result filtering, aggregation
  - Usage: called from `Chatbot` when live context is needed

- `Automation.py`
  - Purpose: Optional execution of tasks (open files, run scripts, etc.)
  - Responsibilities: safe wrappers around OS-level actions
  - Security: validate any user input before executing actions

- `Model.py`
  - Purpose: Shared types, utilities, and constants
  - Responsibilities: schema definitions and helper functions

---

## Data Flow

1. Audio captured by `SpeechToText` → text
2. `Chatbot` receives text and context
3. `Chatbot` optionally queries `RealtimeSearchEngine`
4. `LLMProvider` returns a response
5. `TextToSpeech` synthesizes voice → saves MP3 to `Data/`
6. GUI displays response and status

---

## Configuration

- Environment variables in `.env` (never commit your real file):
  - `CohereAPIKey` – required for LLM calls
- Example file: `.env.example` provides placeholders
- Optional: configure timeouts, audio settings inside module-level constants

---

## Running the Backend

- Standard entry points
  - `python run_jarvis.py` (recommended)
  - `python main.py`

- Audio permissions
  - On Windows, ensure microphone access is enabled

---

## Logging & Artifacts

- Audio outputs and logs are stored under `Data/`
- Artifacts are ignored by Git via `.gitignore`

---

## Extending the Backend

- Adding a provider
  - Implement a new adapter in `LLMProvider.py`
  - Wire feature flags for switching providers

- Adding tools
  - Introduce a module (e.g., `WebSearch.py`) and integrate via `Chatbot`

---

## Testing & Troubleshooting

- Validate environment values before running
- If STT/TTS fails, check your device and permissions
- If LLM calls fail, rotate API keys and check network