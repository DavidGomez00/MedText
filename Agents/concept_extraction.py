import requests
import os
from rethinker import rethink
import json

# Load the json with the text chunks
with open(os.path.join("json", "NCCN-guide.json"), "r") as f:
    chunks = json.load(f)   

used_chunk = chunks['chunk_10']  # For example, using the 10th chunk

# Read the concept extraction prompt
with open("prompts/concept_extraction.txt", "r") as f:
    prompt = f.read()

# Build the messages for the API call
messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": used_chunk }
]

# Call the Ollama API
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

re_answer =rethink_response = rethink(
    prompt=messages[0]['content'], 
    context=used_chunk, 
    response=answer['message']['content']
)

print("Initial answer:")
print(answer['message']['content'])   

print("\nRethinked answer:")
print(re_answer)