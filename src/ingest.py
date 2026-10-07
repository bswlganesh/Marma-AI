from pathlib import Path
from pypdf import PdfReader
import json


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def clean_text(text):
    return " ".join(text.split())


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    list_of_chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk:
            list_of_chunks.append(chunk)

        start += chunk_size - overlap
    return list_of_chunks


def process_pdfs():
    documents = []
    pdf_files = list(RAW_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs")
    for i in pdf_files:
        print(f"Processing: {i.name}")
        reader = PdfReader(i)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            text = clean_text(text)
            if not text:
                continue
            chunks = chunk_text(text)

            for chunk_number, chunk in enumerate(chunks):
                documents.append({
                    "source": i.name,
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