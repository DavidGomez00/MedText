''''Try Ollama API.'''

import time
import os
import requests

messages = [
    {"role": "system", "content": "Eres un asistente especializado en dar los buenos días."},
    {"role": "user", "content": "Buenos días. ¿Cómo estás? Hoy es un día soleado. ¿Puedes darme \
     un consejo para aprovechar el día? Creo que me gustaría salir a caminar y disfrutar del buen \
     clima. Nos olvides incluir una recomendación de un lugar bonito para visitar. Gracias."},
]

times = []
for _ in range(1):
    start_time = time.time()
    answer = requests.post(
        url=f"{os.environ.get('OLLAMA_API_URL')}/api/chat",
        json={
            "model": "llama3.2",
            "messages": messages,
            "stream": False
        }
    ).json()
    end_time = time.time()
    times.append(end_time - start_time)

print(f"Average response time: {sum(times) / len(times)} seconds")