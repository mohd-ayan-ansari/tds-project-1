import numpy as np
import faiss
import pickle
import requests

# CONFIG
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4"
AIPROXY_EMBEDDING_URL = "https://aipipe.org/openai/v1/embeddings"
AIPROXY_CHAT_URL = "https://aipipe.org/openai/v1/chat/completions"
API_KEY = ""
def get_embedding(text, model=EMBEDDING_MODEL):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text.replace("\n", " "),
        "model": model
    }
    response = requests.post(AIPROXY_EMBEDDING_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.status_code}, {response.text}")
    return np.array(response.json()["data"][0]["embedding"], dtype=np.float32)

def get_rag_response(prompt, model=CHAT_MODEL):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    response = requests.post(AIPROXY_CHAT_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Chat completion failed: {response.status_code}, {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()

def search_with_rag(query, k=5):
    index = faiss.read_index("faiss_index.bin")
    with open("faiss_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    query_vec = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_vec, k)

    context_blocks = []
    answers_with_links = []
    for i in indices[0]:
        item = metadata[i]
        context_blocks.append(f"Q: {item['question']}\nA: {item['answer']}")
        answers_with_links.append({
            "answer": item['answer'],
            "url": item.get('_actual_url', 'N/A')
        })

    context_text = "\n\n".join(context_blocks)
    prompt = f"""You are a helpful assistant answering questions using the following Q&A database:

{context_text}

Now, respond to the user's question: "{query}"
"""
    rag_answer = get_rag_response(prompt)
    return rag_answer, answers_with_links

def main():
    query = input("Enter your question: ")
    rag_reply, thread_answers = search_with_rag(query)

    print("\n💬 RAG Answer:\n")
    print(rag_reply)

    print("\n📄 Related Thread Answers:\n")
    for i, item in enumerate(thread_answers, 1):
        print(f"Answer {i}: {item['answer']}")
        print(f"URL: {item['url']}\n")

if __name__ == "__main__":
    main()
