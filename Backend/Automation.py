from pathlib import Path
from AppOpener  import close, open as appopen 
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print 
from .LLMProvider import llm_client
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
env_vars = dotenv_values(BASE_DIR / ".env")

classes = ["zCubwf","hgKElc","LTKOO sY7ric","Z0LcW","gsrt vk_bk FzWSb YwPhnf","pclqee","tw-Data-text tw-text-small tw-ta",
           "IZ6rdc","O5uR6d LTKOO","vlzY6d","webanswers-webanswers_table_webanswers-table","dDoNo ikb4Bb gsrt","sXLaOe",
           "LWkfKe","VQF4g","qv3Wpe","kno-rdesc","SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.6 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role":"system","content": f"Hello, I am {os.environ['Username']},You're a content writer. You have to write content like letters, codes, application, essays, notes, songs, poem etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role":"user","content":f"{prompt}"})

        if llm_client.client is None:
            provider = llm_client.provider.upper()
            return (f"[{provider} API key missing] Unable to generate content automatically. "
                    f"Please set the appropriate API key in the .env file. "
                    f"Current provider: {provider}")

        try:
            completion = llm_client.create_completion(
                model="llama-3.1-8b-instant",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answers = ""

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answers += chunk.choices[0].delta.content

            Answers = Answers.replace("</s>","")
            messages.append({"role":"assistant","content":Answers})

            return Answers
        except Exception as e:
            return f"[Error] Failed to generate content: {str(e)}" 

    Topic: str = Topic.replace("Content ","")
    ContentByAI = ContentWriterAI(Topic)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{Topic.lower().replace(' ','')}.txt"
    file_path = DATA_DIR / filename

    with open(file_path,"w", encoding="utf-8") as file:
        if ContentByAI:
            file.write(ContentByAI)
            file.close()

    OpenNotepad(str(file_path))
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):

    try:
        appopen(app, match_closest=True, output=True)
        return True
    except:
        print(f"Unable to open app directly. Trying with browser fallback: {app}")

        def extract_links(html):
            if html is None:
                return[]
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a',{'jsname':'UWckNb'})
            return [link.get('href') for link in links]
        
        def search_google(query):
            url = f"https://www.google.com/search?q=download+{query}+for+windows"
            headers = {"User-Agent":useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrive search results.")
            return None
        
        html = search_google(app)

        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
            else:
                print("No links found in search result.")


        return True
    
def CloseApp(app):

    if "chrome" in app:
            pass
    else:
        try:
            close(app, match_closest=True, throw_error=True)
            return True
        except:
            return False
        
def System(command):

    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute") 

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume_up":
        volume_up()
    elif command == "volume_down":
        volume_down()

    return True

async def TranslateAndExecute(commands: list[str]):

    funcs = []

    for command in commands:

        if command.startswith("open "):
            
            if "open it" in command:
                pass

            if "open file" == command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search"))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found. For{command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass

    return True

if __name__ == "__main__":
    import asyncio
    # Example commands to test
    commands = ["open chrome","content write a application for sick leave", "open microsoft edge" ,"open linkedin", "open telegram" ,"open whatsapp"]
    asyncio.run(Automation(commands))



            