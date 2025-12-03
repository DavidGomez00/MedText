import json
import os
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Read the PDF file
print("Extracting text from PDF...")
text = ""
pdf_file = os.path.join("pdf", "NCCN-guide.pdf")

print(f"Reading {pdf_file}...")
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        text += page.extract_text() + "\n"

# Use semantic chunking to split the text into manageable pieces
print("Splitting text into chunks...")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_text(text)


print(f"Total chunks created: {len(chunks)}")

# Save chunks in a new JSON file
print("Saving chunks to JSON file...")
output_file = os.path.join("json", "NCCN-guide.json")
with open(output_file, "w") as f:
    json.dump(chunks, f, indent=4)
print("Text extraction and saving completed.")


