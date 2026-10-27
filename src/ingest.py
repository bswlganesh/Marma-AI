from pathlib import Path
from pypdf import PdfReader
import fitz
import re
import json

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

MAPPING_SCAN_PAGES = 50
HEADER_THRESHOLD = 0.15
FOOTER_THRESHOLD = 0.85

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "he", "her", "hers", "him", "his", "how", "i", "if",
    "in", "into", "is", "it", "its", "me", "my", "of", "on", "or", "our",
    "ours", "she", "that", "the", "their", "theirs", "them", "there", "these",
    "they", "this", "those", "to", "was", "we", "were", "what", "when", "where",
    "which", "who", "whom", "why", "will", "with", "you", "your", "yours"
}


def clean_text(text):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    return " ".join(filtered_words)


def find_book_page(page):
    page_height = page.rect.height
    blocks = page.get_text("blocks")
    candidates = []

    for block in blocks:
        x0, y0, x1, y1, text, *_ = block
        text = text.strip()

        if not re.fullmatch(r"\d{1,4}", text):
            continue

        is_header = y0 <= page_height * HEADER_THRESHOLD
        is_footer = y0 >= page_height * FOOTER_THRESHOLD

        if not (is_header or is_footer):
            continue

        candidates.append(int(text))

    if not candidates:
        return None

    return candidates[0]


def find_base_mapping(doc):
    scan_limit = min(MAPPING_SCAN_PAGES, len(doc))
    detected = []

    print()
    print("Searching first pages for book-page numbering...")
    print("=" * 70)

    for pdf_page in range(1, scan_limit + 1):
        page = doc[pdf_page - 1]
        book_page = find_book_page(page)

        if book_page is not None:
            print(f"PDF page {pdf_page:4d} -> Book page {book_page:4d}")
            detected.append((pdf_page, book_page))

    if len(detected) < 2:
        raise ValueError("Could not find enough book-page numbers to establish a mapping.")

    for i in range(len(detected) - 1):
        pdf1, book1 = detected[i]
        pdf2, book2 = detected[i + 1]

        if pdf2 == pdf1 + 1 and book2 == book1 + 1:
            offset = book1 - pdf1

            print()
            print("Base mapping found.")
            print(f"PDF page {pdf1} -> Book page {book1}")
            print(f"PDF page {pdf2} -> Book page {book2}")
            print(f"Offset = {offset}")

            return offset

    raise ValueError(
        "Found page numbers, but could not find two consecutive pages with consecutive book-page numbers."
    )


def process_pdfs():
    documents = []
    pdf_files = list(RAW_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDFs")

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        reader = PdfReader(pdf_file)
        doc = fitz.open(pdf_file)

        offset = find_base_mapping(doc)

        print()
        print(f"Using mapping: book_page = pdf_page + ({offset})")

        for pdf_page, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = clean_text(text)

            if not text:
                continue

            book_page = pdf_page + offset

            documents.append({
                "source": pdf_file.name,
                "pdf_page": pdf_page,
                "book_page": book_page,
                "text": text
            })

        doc.close()

    return documents


if __name__ == "__main__":
    documents = process_pdfs()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / "chunks.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print()
    print(f"Created {len(documents)} pages")
    print(f"Saved to: {output_file}")
