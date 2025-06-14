from fastapi import FastAPI, Query
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
import requests


API_KEY = "AI_PROXY_KEY"
AIPROXY_EMBEDDING_URL = "https://aipipe.org/openai/v1/embeddings"
AIPROXY_CHAT_URL = "https://aipipe.org/openai/v1/chat/completions"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4"
INDEX_PATH = "faiss_index.bin"
METADATA_PATH = "faiss_metadata.pkl"
TOP_K = 5
# ------------------------------------------------

app = FastAPI(title="TDS RAG Replier API")


index = faiss.read_index(INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)


def get_embedding(text: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text.replace("\n", " "),
        "model": EMBEDDING_MODEL
    }
    res = requests.post(AIPROXY_EMBEDDING_URL, headers=headers, json=payload)
    res.raise_for_status()
    return np.array(res.json()["data"][0]["embedding"], dtype=np.float32)


def get_rag_response(prompt: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    res = requests.post(AIPROXY_CHAT_URL, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()


def search_with_rag(query: str):
    query_vec = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_vec, TOP_K)

    context = []
    related = []
    for i in indices[0]:
        item = metadata[i]
        context.append(f"Q: {item['question']}\nA: {item['answer']}")
        related.append({
            "answer": item['answer'],
            "url": item.get("url", "N/A")
        })

    context_text = "\n\n".join(context)
    prompt = f"""You are a helpful assistant answering student questions using the following context:

{context_text}

Now answer this: {query}
"""

    rag_answer = get_rag_response(prompt)
    return rag_answer, related


class RAGResponse(BaseModel):
    rag_answer: str
    thread_answers: list

@app.get("/query", response_model=RAGResponse)
def query_api(text: str = Query(..., description="User question")):
    try:
        rag, answers = search_with_rag(text)
        return {
            "rag_answer": rag,
            "thread_answers": answers
        }
    except Exception as e:
        return {"error": str(e)}
