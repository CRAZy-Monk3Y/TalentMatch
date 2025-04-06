import re

from ollama import Client


def ask_llama(prompt):
    client = Client()
    response = client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": "You are a AI Job Recruiter working for Organisation Accenture Public Limited Company.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    chat_raw = response["message"]["content"]
    # print("Chat RAW",chat_raw)
    try:
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, chat_raw, re.DOTALL)
        chat_raw = matches[0]
    except:
        pass
    return chat_raw


def ask_llama_json(prompt):
    client = Client()
    response = client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": "You are a AI Job Recruiter working for Organisation Accenture Public Limited Company.",
            },
            {"role": "user", "content": prompt},
        ],
        format="json",
    )
    chat_raw = response["message"]["content"]
    # print("Chat RAW",chat_raw)
    return chat_raw
