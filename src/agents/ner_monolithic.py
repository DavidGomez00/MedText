import os
import json
import time
import dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from core.schemas import ExtractionResult

# Cargar variables de entorno
dotenv.load_dotenv()

class MonolithicNERAgent:
    """
    Agente 'Todo en Uno' que extrae, clasifica y atribuye en un solo paso.
    Estrategia: Single-Shot Learning.
    """
    
    def __init__(self, model_name: str, prompt_path: str):
        self.model_name = model_name
        self.prompt_path = prompt_path
        self.apolo_url = os.getenv("APOLO_URL")
        
        # 1. Cargar Prompt al iniciar (no en cada ejecución)
        self.system_prompt = self._load_prompt()
        
        # 2. Inicializar LLM (Configuración fija para este agente)
        self.llm = ChatOllama(
            base_url=self.apolo_url,
            model=self.model_name,
            temperature=0.0,
            format="json",
            num_ctx=8192,
            keep_alive="5m",
            num_predict=-1
        )
        
        print(f"🤖 Agente NER Monolítico inicializado ({model_name})")

    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"Prompt no encontrado en: {self.prompt_path}")

    def run(self, text: str) -> dict:
        """
        Método público para ejecutar el agente.
        Retorna un diccionario estandarizado.
        """
        start_time = time.time()
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=text)
        ]
        
        try:
            # Inferencia
            response = self.llm.invoke(messages)
            raw_content = response.content.strip()
            
            # Validación
            # Limpieza básica por si el modelo devuelve markdown
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            
            json_obj = json.loads(clean_content)
            validated_data = ExtractionResult(**json_obj)
            
            status = "success"
            data = validated_data.model_dump()
            error_msg = None

        except (json.JSONDecodeError, ValidationError) as e:
            status = "validation_error"
            data = None
            error_msg = str(e)
            
        except Exception as e:
            status = "api_error"
            data = None
            error_msg = str(e)
            raw_content = ""

        end_time = time.time()
        
        # Formato de Retorno Estandarizado para todos tus agentes
        return {
            "agent_name": f"NER_Mono_{self.model_name}",
            "status": status,
            "latency": round(end_time - start_time, 2),
            "data": data,
            "error": error_msg,
            # Guardamos input/output raw para depuración futura
            # "raw_input": text[:100] + "...", 
            # "raw_output": raw_content
        }