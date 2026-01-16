import os
import json
import glob
import dotenv
from agents.ner_monolithic import MonolithicNERAgent

dotenv.load_dotenv()

def run_experiment():
    # 1. Configuración del Experimento
    MODEL_NAME = "qwen2.5:7b"
    PROMPT_PATH = "prompts/ner_mono_qwen7b.txt"
    INPUT_DIR = ".data/Cantemist/dev-set1/cantemist-norm/"
    OUTPUT_BASE = ".data/results/experiment_mono_001/"
    
    # 2. Instanciar el Agente
    agent = MonolithicNERAgent(model_name=MODEL_NAME, prompt_path=PROMPT_PATH)
    
    # 3. Preparar datos (Ejemplo con glob para coger todos, o tu lista fija)
    # files = glob.glob(os.path.join(INPUT_DIR, "*.txt"))[:5] 
    # Usamos tu lista manual para probar:
    files = [
        ".data/Cantemist/dev-set1/cantemist-norm/cc_onco2.txt",
        # ".data/Cantemist/dev-set1/cantemist-norm/cc_onco46.txt",
        # ".data/Cantemist/dev-set2/cantemist-norm/cc_onco874.txt",
        # ".data/Cantemist/dev-set2/cantemist-norm/cc_onco1500.txt",
        # ".data/Cantemist/dev-set1/cantemist-norm/cc_onco76.txt"
    ]

    total_time = 0
    success_count = 0

    print(f"🚀 Iniciando experimento con {len(files)} documentos...")

    for file_path in files:
        filename = os.path.basename(file_path)
        
        # Leer
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # --- LA LLAMADA MÁGICA ---
        # El código aquí es agnóstico. Podrías cambiar 'agent' por 'MultiAgentSystem' 
        # y el resto del código no cambiaría.
        result = agent.run(text)
        # -------------------------
        
        if result["status"] == "success":
            success_count += 1
            total_time += result["latency"]
            print(f"✅ {filename} procesado en {result['latency']}s")
            
            # Guardar
            output_dir = os.path.join(OUTPUT_BASE, MODEL_NAME)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename.replace(".txt", ".json"))
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result["data"], f, indent=4, ensure_ascii=False)
        else:
            print(f"❌ Error en {filename}: {result['error']}")

    # Resumen
    avg_time = total_time / success_count if success_count > 0 else 0
    print("-" * 50)
    print(f"📊 Resumen del Experimento:")
    print(f"Total procesados: {success_count}/{len(files)}")
    print(f"Tiempo medio: {round(avg_time, 2)} segundos/doc")
    print(f"Resultados guardados en: {OUTPUT_BASE}")

if __name__ == "__main__":
    run_experiment()