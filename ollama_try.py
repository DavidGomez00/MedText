import os
''''Try Ollama API.'''
import requests

messages = [
    {"role": "system", "content": "Eres un asistente especializado en dar los buenos días."},
    {"role": "user", "content": "Buenos días."}
]

answer = requests.post(
    url=f"{os.environ.get('OLLAMA_API_URL')}/api/chat",
    json={
        "model": "llama3.1:8b",
        "messages": messages,
        "stream": False
    }
).json()

print(answer)