import dotenv
import os
import ollama # Sólo para pull de modelos
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


# Cargar variables de entorno
dotenv.load_dotenv()

APOLO_URL = os.getenv("APOLO_URL")

def pull_model(model_name):
    """
    Realiza un pull del modelo desde Ollama.
    """
    apolo_url = os.getenv("APOLO_URL")
    client = ollama.Client(host=apolo_url)
    try:
        print(f"Solicitando pull de {model_name}...")
        current_digest = None
        for progress in client.pull(model_name, stream=True):
            status = progress.get('status', '')
            completed = progress.get('completed')
            total = progress.get('total')

            if isinstance(completed, int) and isinstance(total, int) and total > 0:
                percent = (completed / total) * 100
                print(f"{status}: {percent:.2f}% ({completed} / {total})", end="\r")
            else:
                print(f"ℹ️  Estado: {status}" + " " * 30, end='\r')
        print(f"\n✅ Modelo {model_name} listo para usar.\n")

    except Exception as e:
        print(f"Error: {e}")

def main(model_name):

    # 1. Instanciamos el modelo
    llm = ChatOllama(
        base_url=APOLO_URL,
        model=model_name,
        temperature=0.0
    )

    # 2. Definimos los mensajes usando los esquemas de Langchain
    messages = [
        SystemMessage(content="Eres un modelo especializado en tareas de procesamiento de lenguaje natural."),
        HumanMessage(content="¿Cuál es la capital de Francia?")
    ]

    # 3. Invocamos el modelo
    print(f"Consultando {model_name}...")
    response = llm.invoke(messages)

    # 4. Mostramos la respuesta
    print("Respuesta del modelo:", response.content)

if __name__ == "__main__":
    
    model_name = "qwen2.5:7b"
    main(model_name)
    
    #pull_model("qwen2.5:7b")