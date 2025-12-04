import edge_tts
import asyncio
import pygame
import os
import tempfile
import uuid
import threading

DATA_DIR = os.path.join("Data")
os.makedirs(DATA_DIR, exist_ok=True)

async def _generate_and_play(text: str, voice: str = "en-CA-LiamNeural"):
    try:
        # Generate speech into a temporary file to avoid conflicts
        temp_filename = os.path.join(DATA_DIR, f"speech_{uuid.uuid4().hex}.mp3")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_filename)

        # Play with pygame
        try:
            pygame.mixer.init()
        except Exception:
            # Already initialized or cannot init, continue to attempt loading
            pass
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Cleanup temporary file after playback
        try:
            os.remove(temp_filename)
        except Exception:
            pass

    except Exception as e:
        print(f"Error in TextToSpeech: {e}")


def TextToSpeech(text: str, voice: str = "en-CA-LiamNeural"):
    """Convert text to speech and play it."""
    try:
        # If there's already an event loop running (e.g., in GUI), run TTS in a separate thread
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except Exception:
            pass

        if loop and loop.is_running():
            def _runner():
                try:
                    asyncio.run(_generate_and_play(text, voice))
                except Exception as e:
                    print(f"Error playing TTS in thread: {e}")

            t = threading.Thread(target=_runner, daemon=True)
            t.start()
        else:
            asyncio.run(_generate_and_play(text, voice))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_generate_and_play(text, voice))
