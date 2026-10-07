import json
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
import shutil
CHUNKS_FILE = Path("data/processed/chunks.json")

def tokenize(text):
    lower_text = text.lower()
    return re.findall(r"\b\w+\b", lower_text)

def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_bm25(documents):
    tokenized_corpus = []
    for doc in documents:
        words = tokenize(doc["text"])
        tokenized_corpus.append(words)

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25

def search(bm25, documents, query, top_k=5):
    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    where_would_it_be = scores.argsort()

    order_high_to_low = where_would_it_be[::-1]
    ranked_indices = order_high_to_low[:top_k]

    results = []

    for index in ranked_indices:
        results.append({
            "score": float(scores[index]),
            "document": documents[index]
        })
    return results


if __name__ == "__main__":

    documents = load_chunks()

    print(f"Loaded {len(documents)} chunks")

    bm25 = build_bm25(documents)

    query = "marma therapy knee osteoarthritis"

    results = search(
        bm25,
        documents,
        query,
        top_k=5
    )

    print()
    print(f"Query: {query}")
    print("=" * 80)

    for i, result in enumerate(results, start=1):
        doc = result["document"]
        print(f"\nRESULT NUMBER {i}")
        print(f"Score  : {result['score']:.4f}")
        print(f"Source : {doc['source'][:50]}")
        print(f"Page   : {doc['page']}")
        print(f"Chunk  : {doc['chunk']}")
        print(f"Text   : {doc['text'][:500]}")

        width = shutil.get_terminal_size().columns
        print("-" * width)