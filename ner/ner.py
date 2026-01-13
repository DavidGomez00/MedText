import ollama
import json
import time

# CONFIGURACIÓN
# Puedes cambiar a 'qwen2.5:7b' si ves que cabe en tu memoria
MODELO = "qwen2.5:3b" 

def procesar_ner(texto):
    """
    Envía texto a Ollama y retorna las entidades en formato diccionario.
    """
    
    # 1. Definimos el Schema que queremos (Prompt del Sistema)
    # Le damos ejemplos claros para guiar al modelo
    system_prompt = """
    Eres un asistente experto en extracción de información clínica. Tu tarea es analizar notas médicas y extraer entidades clínicas en formato JSON.

    Sigue estrictamente estas reglas:
    1. Extrae entidades y clasifícalas SOLO en una de estas categorías: PROBLEM, TREATMENT, TEST, ANATOMY.
    2. Si la entidad no encaja claramente, ignórala.
    3. Detecta el estado de la entidad (Assertion Detection):
    - "absent": Si está negada (ej: "no fiebre").
    - "historical": Si ocurrió en el pasado lejano (ej: "tuvo infarto hace 10 años").
    - "possible": Incertidumbre (ej: "posible fractura").
    - "present": Si está ocurriendo ahora o es un hecho confirmado.
    4. Detecta a quién se refiere (Subject):
    - "patient": Por defecto.
    - "family": Si se refiere a un pariente.

    Salida esperada: ÚNICAMENTE un objeto JSON válido con la clave "clinical_entities".

    Texto:
    {input_text}
    """

    try:
        start_time = time.time()
        
        # 2. Llamada a la API de Ollama
        response = ollama.chat(
            model=MODELO,
            format='json',  #Fuerza la salida JSON válida
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': texto},
            ],
            options={
                'temperature': 0.0
            }
        )
        
        end_time = time.time()
        
        # 3. Procesar respuesta
        contenido = response['message']['content']
        
        # Qwen suele devolver el JSON limpio, lo convertimos a dict de Python
        entidades = json.loads(contenido) # TODO: Check JSON valido
        
        return {
            "status": "success",
            "tiempo_segundos": round(end_time - start_time, 2),
            "modelo_usado": MODELO,
            "data": entidades
        }

    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


if __name__ == "__main__":

    # Ruta a un archivo de texto de ejemplo
    nota_prueba = ".data/cantemist/dev-set1/cantemist-norm/cc_onco2.txt"
    # Leo el archivo de ejemplo
    with open(nota_prueba, "r", encoding="utf-8") as f:
        texto_prueba = f.read()
    
    print(f"🔄 Procesando con {MODELO}...")
    print("-" * 50)
    
    resultado = procesar_ner(texto_prueba)
    
    # Imprimir resultado
    if resultado["status"] == "success":
        print(json.dumps(resultado["data"], indent=2, ensure_ascii=False))
        print("-" * 50)
        print(f"⚡ Tiempo de inferencia: {resultado['tiempo_segundos']} segundos")
    else:
        print("❌ Error:", resultado["mensaje"])