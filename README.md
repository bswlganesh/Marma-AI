# Marma Therapy Advisor: Retrieval Stage

Keyword search over Marma therapy documents. This is step one of a RAG (Retrieval-Augmented Generation) build: it finds the most relevant passages for a question using BM25. Answer generation is planned for a later stage.

## How it works

```
PDFs (data/raw) → ingest.py → chunks.json → bm25.py → api.py (FastAPI) → page.tsx (Next.js)
```

1. **Ingest:** each PDF is read page by page, cleaned, and split into overlapping chunks of up to 500 words (50-word overlap). Every chunk keeps its `source`, `page` and `chunk` number.
2. **Index:** chunks are lowercased and tokenized, then indexed with BM25 (`rank-bm25`).
3. **Search:** a question is tokenized the same way, every chunk is scored, and the top 5 are returned.
4. **API:** `POST /chat` returns the top chunks with their scores and citations.
5. **UI:** a chat page sends the question to the API and displays the results.

## Project structure

```
.
├── src/
│   ├── ingest.py    # PDF → chunks.json
│   ├── bm25.py      # load chunks, build BM25 index, search
│   └── api.py       # FastAPI app (POST /chat)
├── frontend/        # Next.js chat interface (app/page.tsx)
├── data/
│   ├── raw/         # source PDFs (git-ignored)
│   └── processed/   # chunks.json (git-ignored)
├── main.py          # run command for the API
└── requirements.txt
```

## Setup

Requirements: Python 3 and Node.js 20.9 or newer.

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

## Run

Run everything from the project root, except the frontend commands.

```bash
# 1. Build the chunks (only when the PDFs change)
python src/ingest.py

# 2. Start the API at http://localhost:8000
python -m uvicorn src.api:app --reload --port 8000

# 3. In a second terminal, start the UI at http://localhost:3000
cd frontend
npm run dev
```

Place the source PDFs in `data/raw/` before step 1. Only `.pdf` files are read.

## API

`POST /chat`

Request:

```json
{ "question": "marma therapy knee osteoarthritis" }
```

Response:

```json
{
  "query": "marma therapy knee osteoarthritis",
  "results": [
    {
      "score": 12.43,
      "source": "example.pdf",
      "page": 9,
      "chunk": 0,
      "text": "..."
    }
  ]
}
```

Results are ordered best first. The API allows requests from `http://localhost:3000`.

## Known limitations

- BM25 matches exact words only, so synonyms and spelling variants are not matched.
- Some Sanskrit text in the source PDFs is extracted as garbled characters because of the PDF's font encoding.
- Overlapping pages in the source PDFs can produce duplicate chunks.
- The `.doc` file in `data/raw/` is skipped; only PDFs are read.

## Roadmap

- Improve ingestion (deduplicate chunks, repair hyphenated words, handle Sanskrit text).
- Evaluate retrieval quality on test questions.
- Add answer generation (next semester).