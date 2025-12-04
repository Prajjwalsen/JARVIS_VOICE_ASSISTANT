# SpeechToText.py
import os
import time
from pathlib import Path
from dotenv import dotenv_values
import mtranslate as mt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Base/project directories (adjusts to your project layout)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
env_vars = dotenv_values(BASE_DIR / ".env")

# default input language if not provided in .env
InputLanguage = env_vars.get("InputLanguage") or "en-US"

# HTML page used for browser-based speech recognition
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition = null;

        function startRecognition() {{
            const Constructor = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!Constructor) {{
                output.textContent = "ERROR_NO_API";
                return;
            }}
            recognition = new Constructor();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                // set transcript to output element
                output.textContent = transcript;
            }};

            recognition.onerror = function(ev) {{
                output.textContent = "ERROR:" + (ev.error || "unknown");
            }};

            recognition.onend = function() {{
                // do not auto-restart here to avoid loop; Python controls retries
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>'''

# Ensure Data directory exists and write Voice.html
DATA_DIR.mkdir(parents=True, exist_ok=True)
voice_html_path = (DATA_DIR / "Voice.html").resolve()
with open(voice_html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Create file URL correctly for Windows and Unix
if os.name == 'nt':
    Link = voice_html_path.as_uri()
    if not Link.startswith("file:///"):
        Link = 'file:///' + str(voice_html_path).replace('\\', '/')
else:
    Link = f"file://{voice_html_path.as_posix()}"

# Chrome options - don't use headless (Web Speech API often fails headless)
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # auto allow mic access
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-gpu")

# Try to set Chrome binary on Windows for reliability
def try_set_chrome_binary(options: Options):
    if os.name != 'nt':
        return
    possible = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
    ]
    for p in possible:
        if p and os.path.exists(p):
            options.binary_location = p
            print(f"[INFO] Using chrome binary: {p}")
            return
    print("[WARN] Could not detect chrome binary automatically. If driver init fails, set binary path manually.")

try_set_chrome_binary(chrome_options)

driver = None

def get_driver():
    """Get or create a Chrome webdriver instance (robust startup)."""
    global driver
    if driver is not None:
        try:
            _ = driver.current_url  # health check
            return driver
        except Exception:
            try:
                driver.quit()
            except:
                pass
            driver = None

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(20)
        print("[OK] Chrome driver initialized successfully.")
        return driver
    except Exception as e:
        print("[ERROR] Failed to initialize Chrome driver:", e)
        raise

# Helper functions used by main Jarvis code
TempDirPath = BASE_DIR / "Frontend" / "Files"
TempDirPath.mkdir(parents=True, exist_ok=True)

def SetAssistantStatus(Status):
    status_file = TempDirPath / "Status.data"
    with open(status_file, "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query: str) -> str:
    new_query = Query.lower().strip()
    if not new_query:
        return ""
    query_words = new_query.split()
    question_words = ["how","what","who","when","why","which","whose","whom","can you", "what's","where's","how's"]
    last_char = query_words[-1][-1] if query_words and len(query_words[-1])>0 else ""
    if any(qw in new_query for qw in question_words):
        if last_char in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if last_char in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def UniversalTranslator(Text: str) -> str:
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print("[WARN] Translation failed:", e)
        return Text

def SpeechRecognition(max_wait_time: int = 30) -> str:
    """
    Capture voice input using browser-based speech recognition (via an HTML page).
    Returns transformed string (QueryModifier applied). Raises Exception on failure/timeouts.
    """
    try:
        driver_instance = get_driver()

        # open page
        url = Link
        print(f"[INFO] Opening voice page: {url}")
        print(f"[DEBUG] Voice.html exists: {voice_html_path.exists()} -> {voice_html_path}")

        try:
            driver_instance.get(url)
        except Exception as e:
            print("[WARN] Page load failed once, retrying:", e)
            try:
                driver_instance.execute_script("window.stop();")
            except Exception:
                pass
            driver_instance.get(url)

        # Wait until start button is clickable
        wait = WebDriverWait(driver_instance, 10)
        start_btn = wait.until(EC.element_to_be_clickable((By.ID, "start")))
        end_btn = wait.until(EC.presence_of_element_located((By.ID, "end")))

        # Click start
        start_btn.click()
        SetAssistantStatus("Listening...")
        print("[OK] Started recognition (clicked start).")

        # ---- REPLACED LOOP: improved handling for ERROR:... messages ----
        old_text = ""
        start_time = time.time()
        transient_retries = 0
        max_transient_retries = 3

        while True:
            if time.time() - start_time > max_wait_time:
                # try to click end if possible
                try:
                    driver_instance.find_element(By.ID, "end").click()
                except Exception:
                    pass
                SetAssistantStatus("Timeout: No voice input")
                raise Exception("Voice recognition timeout: No input detected within {} seconds".format(max_wait_time))

            try:
                output_el = driver_instance.find_element(By.ID, "output")
                Text = output_el.text.strip()
            except Exception:
                Text = ""

            # Ignore browser-side error tokens coming from the JS page
            if Text:
                if Text.startswith("ERROR:") or Text.startswith("ERROR_NO_API") or Text.lower().startswith("error:"):
                    print(f"[WARN] Browser-side speech error received (ignored): {Text}")
                    transient_retries += 1
                    if transient_retries > max_transient_retries:
                        SetAssistantStatus("Error in voice recognition (browser error)")
                        raise Exception(f"Browser speech error repeated: {Text}")
                    # clear the output element (best-effort) and continue waiting
                    try:
                        driver_instance.execute_script("document.getElementById('output').textContent = '';")
                    except Exception:
                        pass
                    time.sleep(0.3)
                    continue
                # good text -> reset retries
                transient_retries = 0

            if Text and Text != old_text:
                print(f"[VOICE] Raw captured text: {Text}")
                old_text = Text
                # stop recognition if possible
                try:
                    driver_instance.find_element(By.ID, "end").click()
                except Exception:
                    pass
                SetAssistantStatus("Processing...")
                # decide whether to translate
                if InputLanguage and ("en" in InputLanguage.lower()):
                    processed = QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    translated = UniversalTranslator(Text)
                    processed = QueryModifier(translated)
                print(f"[INFO] Returning processed text: {processed}")
                return processed

            # small sleep to avoid busy loop
            time.sleep(0.15)

    except Exception as e:
        error_msg = f"Error in SpeechRecognition: {e}"
        print("[ERROR]", error_msg)
        SetAssistantStatus("Error in voice recognition")
        raise

if __name__ == "__main__":
    print("[INFO] Running SpeechToText module standalone. Press Ctrl+C to stop.")
    while True:
        try:
            txt = SpeechRecognition(max_wait_time=30)
            print("Captured:", txt)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Exiting.")
            break
        except Exception as e:
            print("Runtime error:", e)
            time.sleep(2)
