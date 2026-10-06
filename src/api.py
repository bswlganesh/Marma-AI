from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from bm25 import load_chunks, build_bm25, search
from src.bm25 import load_chunks, build_bm25, search

app = FastAPI()

app.add_middleware( #let it
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


documents = load_chunks()
bm25 = build_bm25(documents)


@app.post("/chat")
def chat(data: dict):

    question = data["question"]

    results = search(
        bm25,
        documents,
        question,
        top_k=5 #top kitna
    )

    formatted_results = []

    for result in results:

        doc = result["document"]

        formatted_results.append({
            "score": result["score"],
            "source": doc["source"],
            "page": doc["page"],
            "chunk": doc["chunk"],
            "text": doc["text"],
        })

    return {
        "query": question,
        "results": formatted_results,
    }

























    # 1 return {
    #     "answer": results[0]["document"]["text"]
    #     if results
    #     else "No relevant information found."
    # }
    
2#     return {
#   "query": "What is Marma?",
#   "results": [
#     {
#       "score": 12.43,
#       "source": "Dr_Alka_Exploring_the_Science_of_Marma.pdf",
#       "page": 41,
#       "chunk": 3,
#       "text": "Marma..."
#     }
#   ]
# }
