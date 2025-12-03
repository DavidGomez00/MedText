'''This file extracts text from a PDF, chunks it, and generates embeddings using Ollama API.
Then, stores the embeddings in a Neo4j database.'''
import os
import requests

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

# Get PDF text and chunk it
pdf_file = os.path.join("/home/david/GitHub/MedText/pdf", "NCCN-guide.pdf")
loader = PyPDFLoader(pdf_file)
documents = loader.load()

print(f"{len(documents)} pages loaded from the PDF.")

# Native Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False
)

naive_chunks = text_splitter.split_documents(documents)

embed_model = FastEmbedEmbeddings(model_name="llama2-7b-embeddings")

semantic_chunker = SemanticChunker(embed_model, breakpoint_threshold_type="percentile")
semantic_chunks = semantic_chunker.create_documents([d.page_content for d in documents])

for semantic_chunk in semantic_chunks:
    if "Effect of Pre-training Tasks" in semantic_chunk.page_content:
        print(semantic_chunk.page_content)
        print(len(semantic_chunk.page_content))




