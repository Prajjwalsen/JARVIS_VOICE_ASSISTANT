#!/usr/bin/env python3
"""
JARVIS Voice-Controlled Assistant - Complete Integration
Brain that coordinates all backend modules with Frontend GUI
"""

import sys
import os
import threading
import time
import asyncio
from pathlib import Path

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent / "Backend"))

# Import backend modules
from Backend.SpeechToText import SpeechRecognition, SetAssistantStatus
from Backend.TextToSpeech import TextToSpeech
from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation

# Import frontend GUI functions
from Frontend.GUI import (
    GraphicalUserInterface,
    ShowTextToScreen,
    GetMicrophoneStatus,
    SetMicrophoneStatus
)

# Import SetAssistantStatus from GUI (it's defined in GUI.py)
import Frontend.GUI as gui_module

class JarvisBrain:
    """Main brain that coordinates all modules"""

    def __init__(self):
        self.running = True
        self.processing = False
        self.setup_directories()
        self.last_mic_status = "False"

        print("=" * 60)
        print("JARVIS Voice-Controlled Assistant - Brain Initialized")
        print("=" * 60)
        print("\n[OK] All modules loaded successfully")
        print("[INFO] Starting GUI...")
        print("[INFO] Click the microphone button to start voice commands\n")

    def setup_directories(self):
        """Create necessary directories"""
        directories = ["Data", "Frontend/Files", "Frontend/Graphics"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Initialize status files
        status_file = Path("Frontend/Files/Status.data")
        mic_file = Path("Frontend/Files/Mic.data")
        responses_file = Path("Frontend/Files/Responses.data")

        if not status_file.exists():
            status_file.write_text("Ready", encoding='utf-8')
        if not mic_file.exists():
            mic_file.write_text("False", encoding='utf-8')
        if not responses_file.exists():
            responses_file.write_text("", encoding='utf-8')

    def process_command(self, user_input: str):
        """Process user input and route to appropriate handler"""
        if not user_input or not user_input.strip():
            return

        user_input = user_input.strip()
        self.processing = True

        # Display user query in GUI
        ShowTextToScreen(f"You: {user_input}")
        gui_module.SetAssistantStatus("Thinking...")

        print(f"\n[YOU] {user_input}")
        print("[BRAIN] Processing command...\n")

        try:
            # Use decision-making model to determine command type
            gui_module.SetAssistantStatus("Analyzing command...")
            stream = FirstLayerDMM(user_input)

            # Parse the decision model response
            response = ""
            for event in stream:
                if event.event_type == "text-generation":
                    response += event.text

            # Clean and parse response
            response = response.replace("\n,", "").strip()
            commands = [cmd.strip() for cmd in response.split(",") if cmd.strip()]

            # Filter valid commands
            valid_commands = []
            funcs = ["exit", "general", "realtime", "open", "close", "play",
                     "system", "content", "google search",
                     "youtube search", "reminder"]

            for cmd in commands:
                for func in funcs:
                    if cmd.startswith(func):
                        valid_commands.append(cmd)
                        break

            if not valid_commands:
                # Default to general query if no valid command found
                valid_commands = [f"general {user_input}"]

            # Execute commands
            asyncio.run(self.execute_commands(valid_commands, user_input))

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(f"[ERROR] {error_msg}")
            ShowTextToScreen(f"JARVIS: Sorry, I encountered an error. Please try again.")
            TextToSpeech("Sorry, I encountered an error. Please try again.")
            gui_module.SetAssistantStatus("Error")
            self.processing = False
        finally:
            gui_module.SetAssistantStatus("Ready")

    async def execute_commands(self, commands: list, original_query: str):
        """Execute the parsed commands"""
        automation_commands = []
        general_query = None
        realtime_query = None

        for command in commands:
            command_lower = command.lower()

            if command_lower.startswith("exit"):
                self.running = False
                ShowTextToScreen("JARVIS: Goodbye! Have a great day!")
                TextToSpeech("Goodbye! Have a great day!")
                return

            elif command_lower.startswith("general"):
                # Extract the query part
                query = command.replace("general", "").strip()
                if query.startswith("(") and query.endswith(")"):
                    query = query[1:-1].strip()
                general_query = query if query else original_query

            elif command_lower.startswith("realtime"):
                # Extract the query part
                query = command.replace("realtime", "").strip()
                if query.startswith("(") and query.endswith(")"):
                    query = query[1:-1].strip()
                realtime_query = query if query else original_query

            else:
                # Automation commands (open, close, play, content, system, etc.)
                automation_commands.append(command)

        # Execute automation commands first
        if automation_commands:
            gui_module.SetAssistantStatus("Executing automation...")
            print("[AUTO] Executing automation commands...")
            ShowTextToScreen("JARVIS: Executing your automation commands...")
            try:
                await Automation(automation_commands)
                print("[OK] Automation completed!")
                ShowTextToScreen("JARVIS: Automation completed successfully!")
            except Exception as e:
                print(f"[ERROR] Automation error: {e}")
                ShowTextToScreen(f"JARVIS: Automation error: {str(e)}")

        # Handle real-time queries
        if realtime_query:
            gui_module.SetAssistantStatus("Searching real-time information...")
            print(f"[SEARCH] Searching for: {realtime_query}")
            ShowTextToScreen(f"JARVIS: Searching for real-time information about '{realtime_query}'...")
            try:
                response = RealtimeSearchEngine(realtime_query)
                print(f"[RESPONSE] {response}\n")
                ShowTextToScreen(f"JARVIS: {response}")
                TextToSpeech(response)
            except Exception as e:
                print(f"[ERROR] Real-time search error: {e}")
                error_msg = "Sorry, I couldn't find that information."
                ShowTextToScreen(f"JARVIS: {error_msg}")
                TextToSpeech(error_msg)

        # Handle general queries
        if general_query:
            gui_module.SetAssistantStatus("Thinking...")
            print(f"[THINKING] Processing your question...\n")
            ShowTextToScreen(f"JARVIS: Let me think about that...")
            try:
                # ChatBot already calls TextToSpeech internally
                response = ChatBot(general_query)
                print(f"[RESPONSE] {response}\n")
                ShowTextToScreen(f"JARVIS: {response}")
            except Exception as e:
                print(f"[ERROR] Chatbot error: {e}")
                error_msg = "Sorry, I couldn't process that question."
                ShowTextToScreen(f"JARVIS: {error_msg}")
                TextToSpeech(error_msg)

        gui_module.SetAssistantStatus("Ready")
        self.processing = False

    def listen_with_retries(self, attempts: int = 2, max_wait_time: int = 30):
        """
        Wrapper around SpeechRecognition to retry transient errors.
        Returns captured text string or None if not successful.
        """
        last_exception = None
        for attempt in range(attempts + 1):
            try:
                print(f"[LISTEN] Attempt {attempt+1} to capture voice...")
                text = SpeechRecognition(max_wait_time=max_wait_time)
                # SpeechRecognition now raises on real errors and returns valid text only.
                if text and text.strip():
                    return text.strip()
                # If empty, treat as None and retry
                last_exception = None
            except Exception as e:
                last_exception = e
                print(f"[LISTEN] Attempt {attempt+1} failed: {e}")
                # short pause between retries
                time.sleep(0.8)
                # If it's a serious driver/init error, break early
                err_str = str(e).lower()
                if "failed to initialize chrome driver" in err_str or ("driver" in err_str and "install" in err_str):
                    break
        # All attempts exhausted
        if last_exception:
            print(f"[LISTEN] Final error after retries: {last_exception}")
        return None

    def voice_control_loop(self):
        """Main voice control loop that monitors microphone status"""
        print("[BRAIN] Voice control loop started")

        while self.running:
            try:
                # Check microphone status
                current_mic_status = GetMicrophoneStatus()

                # If microphone was just activated and we're not processing
                if current_mic_status == "True" and self.last_mic_status == "False" and not self.processing:
                    print("[BRAIN] Microphone activated - listening...")
                    gui_module.SetAssistantStatus("Listening...")

                    try:
                        # Use wrapper with retries instead of direct call
                        user_input = self.listen_with_retries(attempts=2, max_wait_time=30)

                        if user_input and user_input.strip():
                            # ================= DEBUG ECHO SNIPPET START =================
                            # This snippet immediately echoes the captured text via TTS
                            # to confirm the pipeline from STT -> main -> TTS is working.
                            print(f"[DEBUG] Captured user_input -> {user_input!r}")
                            ShowTextToScreen(f"You: {user_input}")
                            # Immediately speak what was heard (simple echo) to confirm TTS works
                            try:
                                TextToSpeech(f"You said: {user_input}")
                            except Exception as tts_exc:
                                print(f"[DEBUG] TextToSpeech failed: {tts_exc}")
                                ShowTextToScreen("JARVIS: TTS failed, see console.")
                            # Now call the real processor and log if it raises
                            try:
                                self.process_command(user_input)
                            except Exception as e:
                                print(f"[DEBUG] process_command raised: {e}")
                                ShowTextToScreen("JARVIS: Error while processing command. See console.")
                            # ================= DEBUG ECHO SNIPPET END =================

                            # Reset microphone status
                            SetMicrophoneStatus("False")
                            self.last_mic_status = "False"
                        else:
                            print("[WARNING] No voice input detected (or attempts exhausted)")
                            ShowTextToScreen("JARVIS: No voice input detected. Please try again.")
                            gui_module.SetAssistantStatus("No input detected")
                            SetMicrophoneStatus("False")
                            self.last_mic_status = "False"

                    except Exception as e:
                        error_msg = str(e)
                        print(f"[ERROR] Error in voice recognition: {error_msg}")

                        # Show user-friendly error message
                        if "timeout" in error_msg.lower():
                            user_msg = "Voice recognition timeout. Please speak clearly and try again."
                        elif "chrome" in error_msg.lower() or "driver" in error_msg.lower():
                            user_msg = "Browser error. Please ensure Chrome is installed and try again."
                        else:
                            user_msg = "Error in voice recognition. Please check your microphone and try again."

                        ShowTextToScreen(f"JARVIS: {user_msg}")
                        gui_module.SetAssistantStatus("Error in voice recognition")
                        SetMicrophoneStatus("False")
                        self.last_mic_status = "False"

                        # Wait a bit before allowing next attempt
                        time.sleep(2)

                # Update last status
                self.last_mic_status = current_mic_status

                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)

            except KeyboardInterrupt:
                print("\n[WARNING] Interrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR] Error in voice control loop: {e}")
                time.sleep(1)

    def start_gui(self):
        """Start the GUI in the main thread"""
        try:
            print("[GUI] Starting graphical interface...")
            GraphicalUserInterface()
        except Exception as e:
            print(f"[ERROR] GUI error: {e}")
            import traceback
            traceback.print_exc()

    def start(self):
        """Start JARVIS brain - coordinates GUI and voice control"""
        try:
            # Start voice control in a separate thread
            voice_thread = threading.Thread(target=self.voice_control_loop, daemon=True)
            voice_thread.start()
            print("[OK] Voice control thread started")

            # Start GUI in main thread (GUI must run in main thread)
            print("[OK] Starting GUI...")
            self.start_gui()

        except Exception as e:
            print(f"[FATAL ERROR] Failed to start JARVIS: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            print("\n[BYE] JARVIS shutting down...")

def main():
    """Main entry point"""
    try:
        # Set UTF-8 encoding for Windows console
        if sys.platform == "win32":
            os.system("chcp 65001 >nul 2>&1")

        # Create and start JARVIS brain
        jarvis = JarvisBrain()
        jarvis.start()

    except KeyboardInterrupt:
        print("\n[BYE] Shutting down JARVIS...")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
