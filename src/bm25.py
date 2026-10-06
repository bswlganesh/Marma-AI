import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

CHUNKS_FILE = Path("data/processed/chunks.json")

def tokenize(text): #lowecase and split
    return re.findall(r"\b\w+\b", text.lower())

def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_bm25(documents): #main stuff
    tokenized_corpus = [
        tokenize(doc["text"])
        for doc in documents
    ]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25


# def search(bm25, documents, query, top_k=5):
#     """
#     Search the BM25 index.
#     """
#     tokenized_query = tokenize(query)

#     results = bm25.get_top_n(
#         tokenized_query,
#         documents,
#         n=top_k
#     )

#     return results
def search(bm25, documents, query, top_k=5):#keep top 5
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    ranked_indices = scores.argsort()[::-1][:top_k]
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

    # query = "marma therapy knee osteoarthritis"

    # results = search(
    #     bm25,
    #     documents,
    #     query,
    #     top_k=5
    # )

    # print()
    # print(f"Query: {query}")
    # print("=" * 80)

    # for i, result in enumerate(results, start=1):

    #     print(f"\nRESULT {i}")
    #     print(f"Source : {result['source']}")
    #     print(f"Page   : {result['page']}")
    #     print(f"Chunk  : {result['chunk']}")
    #     print(f"Text   : {result['text'][:500]}")

    for i, result in enumerate(results, start=1):

        doc = result["document"]

        print(f"\nRESULT {i}")
        print(f"Score  : {result['score']:.4f}")
        print(f"Source : {doc['source']}")
        print(f"Page   : {doc['page']}")
        print(f"Chunk  : {doc['chunk']}")
        print(f"Text   : {doc['text'][:500]}")
        print("-" * 80)