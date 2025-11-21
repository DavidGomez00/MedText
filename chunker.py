'''This file extracts text from a PDF, chunks it, and generates embeddings using Ollama API.
Then, stores the embeddings in a Neo4j database.'''

import pdfplumber
from utils import chunk_text
import os
from neo4j import GraphDatabase
import requests

# Get PDF text and chunk it
text = ""
pdf_file = os.path.join("pdf", "CBIS.pdf")
print(f"Reading {pdf_file}...")
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        text += page.extract_text() + "\n"

print(f"Creating chunks from text of length {len(text)}...")
chunks = chunk_text(text, chunk_size=2000, overlap=200)
print("Number of chunks created:", len(chunks))

print("Generating embeddings using Ollama API...")
answer = requests.post(
    url=os.getenv("OLLAMA_API_URL") + "/v1/embeddings",
    headers={"Content-Type": "application/json"},
    json={
        "model": "llama2-7b-embeddings",
        "input": chunks[0]
    }
).json()

embeddings = answer['data']
print("Number of embeddings received:", len(embeddings))

driver = GraphDatabase.driver(
    os.environ.get("NEO4J_URI"), 
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)
driver.execute_query('''CREATE VECTOR INDEX pdf IF NOT EXISTS
                     FOR (c:Chunk)
                     ON c.embedding''')



