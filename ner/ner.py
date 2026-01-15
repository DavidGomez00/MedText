import json
import time
import os
import dotenv

from typing import List, Literal
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field, ValidationError

# Cargar variables de entorno
dotenv.load_dotenv()


class ClinicalEntity(BaseModel):
    text: str = Field(description="El texto exacto extraído de la nota clínica.")
    label: Literal["PROBLEM", "TREATMENT", "TEST", "ANATOMY"] = Field(description="Categoría de la entidad.")
    status: Literal["present", "absent", "possible", "conditional", "historical"] = Field(description="Estado de la afirmación.")
    subject: Literal["patient", "family_member", "other"] = Field(description="Sujeto al que se refiere la entidad.")

class ExtractionResult(BaseModel):
    clinical_entities: List[ClinicalEntity]


APOLO_URL = os.getenv("APOLO_URL")

def ner(model_name, text):
    """ Ejecuta NER a través de langchain y valida estrictamente 
    la salida usando Pydantic.
    """

    # Configuración del parser
    parser = PydanticOutputParser(pydantic_object=ExtractionResult)
    
    # Lee el prompt del archivo con el mismo nombre
    try:
        with open(f"agents/prompts/{model_name}_ner.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()
    except FileNotFoundError as e:
        print(f'Error en la lectura del prompt para {model_name}: {e}')
        return {"status": "error", "mensaje": "Prompt file not found"}
    

    # Inyecto instrucciones de formato del parser al modelo
    # format_instructions = parser.get_format_instructions()
    # final_system_prompt = f"{base_prompt}\n\n{format_instructions}"
    # final_system_prompt = base_prompt

    llm = ChatOllama(
        base_url=APOLO_URL,
        model=model_name,
        temperature=0.0,
        format="json",
        num_ctx=8192, # Aumento a 8k tokens
        keep_alive="5m",
        num_predict=-1 # Asegura espacio para la respuesta
    )

    messages = [ 
        SystemMessage(content=final_system_prompt),
        HumanMessage(content=text),
    ]

    print(f"🧠 Consultando {model_name}...")
    start_time = time.time()
    
    try:
        response = llm.invoke(messages)
        content = response.content.strip()

        # Validación con Pydantic        
        try: 
            json_content = json.loads(content)
            validated_data = ExtractionResult(**json_content)  # TODO: Entender esto
        
            status = "succes"
            data = validated_data.model_dump() # Convierte a dict estándar
            error_msg = None
        
        except (json.JSONDecodeError, ValidationError) as e:
            status = "validation_error"
            data = None
            error_msg = str(e)
            print(f"⚠️ Error de validación: {e}")
    
    except Exception as e:
        status = "api_error"
        data = None
        error_msg = str(e)
        content = ""
    
    end_time = time.time()

    return {
        "status": status,
        "tiempo": round(end_time - start_time, 2),
        "data": data,
        "error": error_msg,
        "raw_response": content
    }


def main():

    # Escojo 5 notas de ejemplo
    notas_prueba = [
        ".data/Cantemist/dev-set1/cantemist-norm/cc_onco2.txt",
        ".data/Cantemist/dev-set1/cantemist-norm/cc_onco46.txt",
        ".data/Cantemist/dev-set2/cantemist-norm/cc_onco874.txt",
        ".data/Cantemist/dev-set2/cantemist-norm/cc_onco1500.txt",
        ".data/Cantemist/dev-set1/cantemist-norm/cc_onco76.txt"
    ]


    # Seleccionamos modelo inicial
    model_name = "qwen2.5:7b"

    times = []

    if len(notas_prueba) == 0:
        print("No hay notas que procesar.")
        return -1

    for nota in notas_prueba:
        print(f"{nota.split("/")[-1]}")
        print("-" * 50)
        
        # Leo el archivo de ejemplo
        with open(nota, "r", encoding="utf-8") as f:
            texto_prueba = f.read()

        resultado = ner(model_name, texto_prueba)
        times.append(resultado['tiempo'])
        
        # Procesar respuesta
        if resultado["status"] == "succes":
            print("✅ ÉXITO. Datos validados.")

            # Guardar el JSON preservando estructura de carpetas.
            # nota: .data/Cantemist/.../file.txt -> .data/ner_results/<model>/Cantemist/.../file.json
            relative_path = os.path.relpath(nota, ".data")
            output_dir = os.path.join(".data", "ner_results", model_name, os.path.dirname(relative_path))
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            file_name = os.path.splitext(os.path.basename(nota))[0] + ".json"
            output_path = os.path.join(output_dir, file_name)

            with open(output_path, 'w', encoding="utf8") as f:
                json.dump(resultado["data"], f, ensure_ascii=False, indent=4)

            print(f'Saved: {output_path}')
            
            # entidades = resultado["data"]["clinical_entities"]
            # problemas = [e['text'] for e in entidades if e['label'] == 'PROBLEM']
            # print(f"\nProblemas detectados: {problemas}")
            print(f"⚡ Tiempo de inferencia: {resultado['tiempo']}")
            

        else:
            print(f"❌ FALLO ({resultado['status']}):")
            print(resultado["error"])
            print(f"⚡ Tiempo de inferencia: {resultado['tiempo']}")
        
    if len(times) != 0:
        total_time = sum(times) / len(times)
        print(f"⚡ Tiempo de inferencia total : {round(total_time, 2)}.")


if __name__ == "__main__":
    main()