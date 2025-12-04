from .LLMProvider import llm_client
from json import load, dump
import datetime
from dotenv import load_dotenv
from pathlib import Path
from .TextToSpeech import TextToSpeech  # Adjust path if needed
import os 

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

print(f"ENV VARS - Using LLM Provider: {llm_client.provider.upper()}")
Username = os.getenv("Username", "User")
Assistantname = os.getenv("Assistantname", "Jarvis")

if llm_client.client is None:
    print(f"ERROR: {llm_client.provider.upper()} API Key not loaded! Check spelling or .env location")
else:
    print(f"OK: Loaded {llm_client.provider.upper()} API client")


messages = []


System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
SystemChatBot = [
    {"role":"system","content": System}
]

DATA_DIR.mkdir(parents=True, exist_ok=True)
chatlog_path = DATA_DIR / "Chatlog.json"
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chatlog_path, "w") as f:
        dump([],f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes : {second} seconds.\n"
    return data

def AnswerModifire(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response. """

    try:
        chatlog_path = DATA_DIR / "Chatlog.json"
        with open(chatlog_path, "r") as f:
            messages = load(f)

        messages.append({"role":"user","content": f"{Query}"})

        completion = llm_client.create_completion(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role":"system","content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                content_piece = chunk.choices[0].delta.content
                print(content_piece, end="", flush=True)  # 👈 Streaming effect
                Answer += content_piece 

        Answer = Answer.replace("</s>","")

        messages.append({"role":"assistant","content":Answer})

        chatlog_path = DATA_DIR / "Chatlog.json"
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)
        TextToSpeech(Answer)
        return AnswerModifire(Answer=Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        chatlog_path = DATA_DIR / "Chatlog.json"
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)
    
if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter Your Question: ")
        except EOFError:
            print("\nNo interactive input available. Exiting Chatbot CLI.")
            break

        if not user_input.strip():
            print("Please enter a valid question.")
            continue

        response = ChatBot(user_input)
        print(response)
