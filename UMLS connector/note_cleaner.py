import os
import requests
from dotenv import load_dotenv

load_dotenv()


def clean_note(note):
    prompt = """Eres un sistema experto en notas clínicas. El siguiente texto pertenece a una nota clínica que puede contener
    errores tipográficos, delimitadores o espacios mal colocados u omitidos. Tu objetivo es corregir estos errores sin modificar
    la información original de la nota clínica. 
    Debes retornar únicamente el texto corregido, sin añadir elementos conversacionales.
    
    Texto de la nota clínica:"""
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": note }
    ]
    answer = requests.post(
        url=os.getenv('OLLAMA_API_URL') + "/api/chat",
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


if __name__ == "__main__":
    sample_note = "CICLO 21 T-DM1Carcinoma inflamatorio bilateral de mama (G3) diagnosticado en 2007. T4N2M0 (Estadio IIIB). Triple positivo.*QT- ACT, trastuzumab y hormonoterapia. Mastectomía bilateral +LA. RT pared torácica derecha e izquierda, áreas ganglionares axilares bilaterales y cérvico claviculares. Tamoxifeno oct 2007 – noviembre 2012.- Recaída hepatica y ganglionar (oct 2014). Ca mama estadio IV HER2+ en Octubre del 2014.*El 30.10.2014 inicia Taxol semanal + trastuzumab + pertuzumab trisemanal x 7 ciclos (05.03.2015), continuando con pertuzumab + herceptin con buena respuesta.*El 24/11/2015 se realiza segmentectomía hepática VII + subsegmentectomía VI de metástasis hepática y sección de vena suprahepática derecha.*Desde entonces, pertuzumab-herceptín-enero 2017*TAC enero 2017: adenopatía anterosup mediastinica*PERTU -TRASTU + LETROZOL*Progresión a nivel abdominal con masa pancreática con confirmación histológica.*SBRT sobre la lesión pancreatica entre el 6 y el 16/12/2019.*TDM1 desde el 26/7/2019Sospecha de ocupacion a nivel de la protesis biliar .Se ha retrasado la administraciond e qt ya mas de un mes ultima dosis administrada el 10 de Dic, mantienen BIl estable y tiene citado TAC en 2 dias .Administro tto , y cito en 1 semana para ver resultados del TAC y valorar."
    cleaned_sample_note = clean_note(sample_note)
    print("Original note:")
    print(sample_note)
    print("\nCleaned note:")
    print(cleaned_sample_note)