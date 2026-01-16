import requests
import os

def rethink(prompt, context, response):
    # Read the rethink prompt
    with open("prompts/rethink.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("<PROMPT>", prompt).replace("<CONTEXT>", context)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Initial response: " + response}
    ]

    answer = requests.post(
        url=os.getenv("OLLAMA_API_URL") + "/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "model": "llama3.1:8b",
            "messages": messages,
            "stream": False,
            "options": {
                "max_tokens": 1000,
                "temperature": 0
            }
        }
    ).json()

    return answer['message']['content']
