# JARVIS – Usage Guide

Welcome to the usage guide for JARVIS, your professional voice-assisted AI desktop assistant. This guide will walk you through setup, configuration, usage scenarios, and troubleshooting to help you get the most out of JARVIS.

---

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Running JARVIS](#running-jarvis)
- [Using the Desktop GUI](#using-the-desktop-gui)
- [Voice Commands & Chat](#voice-commands--chat)
- [Data & Privacy](#data--privacy)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Installation
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd JARVIS
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install dependencies:**
   ```sh
   pip install -r Requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and set your API key(s).

---

## Configuration
- Edit `.env` and set `CohereAPIKey=YOUR_COHERE_API_KEY` (or your LLM provider).
- Optional: Adjust module-level settings for audio, timeouts, etc.

---

## Running JARVIS
- Start with:
  ```sh
  python run_jarvis.py
  # or
  start_jarvis.bat
  ```
- The GUI should appear. If not, see Troubleshooting.

---

## Using the Desktop GUI
- **Microphone Control:** Toggle the mic to start/stop listening.
- **Status Indicators:** See when JARVIS is listening, processing, or speaking.
- **Output Area:** View responses and actions.

---

## Voice Commands & Chat
- Speak naturally to ask questions or give commands.
- JARVIS responds via text and optional voice output.
- Example commands:
  - "What’s the weather today?"
  - "Open Notepad."
  - "Summarize this article: ..."

---

## Data & Privacy
- All audio outputs and chat logs are stored locally in `Data/`.
- No data is sent to the cloud except for LLM API calls.
- `.env` and credentials are never committed to Git.

---

## Troubleshooting
- **PowerShell Activation Error:**
  - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- **Missing Dependencies:**
  - Run `pip install -r Requirements.txt` again.
- **No Audio Output:**
  - Check your device, volume, and delete old MP3s in `Data/`.
- **GUI Not Starting:**
  - Ensure you’re running from the project root and dependencies are installed.

---

## Advanced Usage
- **Switch LLM Providers:** Edit `Backend/LLMProvider.py` and update `.env`.
- **Add Custom Automation:** Extend `Backend/Automation.py`.
- **Customize GUI:** Modify `Frontend/GUI.py` and assets in `Frontend/Graphics/`.

---

For more details, see the main `README.md`, or open an issue for help.
