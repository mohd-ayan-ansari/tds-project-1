
import pandas as pd
import numpy as np
import faiss
import requests
import pickle

# CONFIG
CSV_PATH = "cleaned_qa_tafree.csv"
EMBEDDING_MODEL = "text-embedding-3-small"
AIPROXY_EMBEDDING_URL = "https://aipipe.org/openai/v1/embeddings"
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

def main():
    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)

    print("Generating embeddings...")
    embeddings = np.vstack([get_embedding(q) for q in df["question"]])

    print("Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("Saving FAISS index and metadata...")
    faiss.write_index(index, "faiss_index.bin")
    with open("faiss_metadata.pkl", "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print("🎉 Done! Index and metadata saved.")

if __name__ == "__main__":
    main()
