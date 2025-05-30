import pickle
import numpy as np

with open("embedding_model.pkl", "rb") as f:
    model_data = pickle.load(f)

chunks = model_data["chunks"]
embeddings = model_data["embeddings"]

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def get_relevant_chunk(query_embedding):
    similarities = [cosine_similarity(query_embedding, emb) for emb in embeddings]
    top_idx = int(np.argmax(similarities))
    return chunks[top_idx]
