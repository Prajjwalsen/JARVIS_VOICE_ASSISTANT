from googlesearch import search
from .LLMProvider import llm_client
from json import load, dump
import datetime
from dotenv import dotenv_values
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
env_vars = dotenv_values(BASE_DIR / ".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

DATA_DIR.mkdir(parents=True, exist_ok=True)
chatlog_path = DATA_DIR / "Chatlog.json"
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except:
    with open(chatlog_path, "w") as f:
        dump([], f)

def GoogleSearch(Query):
    results = list(search(Query, advanced=True, num_results=5))
    Answer = f"The search results for '{Query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system","content":System},
    {"role":"user", "content": "Hi"},
    {"role":"assistant","content":"Hello Sir, how can i help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date:{date}\n"
    date += f"Month: {month}\n"
    data += f"Year:{year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    chatlog_path = DATA_DIR / "Chatlog.json"
    with open(chatlog_path, "r") as f:
        messages = load(f)
    messages.append({"role":"user","content": f"{prompt}"})

    SystemChatBot.append({"role":"system","content":GoogleSearch(prompt)})

    completion = llm_client.create_completion(
        model="llama-3.3-70b-versatile",
        messages=SystemChatBot + [{"role":"system","content": Information()}] + messages,
        temperature = 0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>","")
    messages.append({"role":"assistant","content":Answer})

    chatlog_path = DATA_DIR / "Chatlog.json"
    with open(chatlog_path, "w") as f:
        dump(messages, f , indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))