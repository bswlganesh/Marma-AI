from pathlib import Path
from pypdf import PdfReader
import json
import re


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")



def clean_text(text):
    """Clean extracted PDF text."""
    text = re.sub(r"\s+", " ", text) #many spaces and /n into sinlge space
    return text.strip()


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping word chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks



def process_pdfs():
    documents = []
    pdf_files = list(RAW_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs")
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        reader = PdfReader(pdf_path)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = clean_text(text)
            if not text:
                continue
            chunks = chunk_text(text)
            for chunk_number, chunk in enumerate(chunks):
                documents.append({
                    "source": pdf_path.name,
                    "page": page_number,
                    "chunk": chunk_number,
                    "text": chunk
                })
    return documents


if __name__ == "__main__":

    documents = process_pdfs()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / "chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print()
    print(f"Created {len(documents)} chunks")
    print(f"Saved to: {output_file}")