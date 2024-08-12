import os
import json

import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch

import utils._global as _global

model_name = _global.model_name


def get_tokenizer_and_model():
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    tokenizer.save_pretrained(f"model/tokenizer/{model_name}")
    model.save_pretrained(f"model/embedding/{model_name}")


def compute_embeddings(text):
    tokenizer = AutoTokenizer.from_pretrained(f"./model/tokenizer/{model_name}") 
    model = AutoModel.from_pretrained(f"./model/embedding/{model_name}")

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True) 
    
    # Generate the embeddings 
    with torch.no_grad():    
        embeddings = model(**inputs).last_hidden_state.mean(dim=1).squeeze()

    return embeddings.tolist()


def create_vector_store(doc_store):
    vector_store_path = _global.vector_store_path
    if os.path.isfile(vector_store_path):
        with open(vector_store_path, 'r') as f:
            vector_store = json.load(f)
        return vector_store

    vector_store = {}
    for doc_id, chunks in doc_store.items():
        doc_vectors = {}
        for chunk_id, chunk_dict in chunks.items():
            # Generate an embedding for each chunk of text
            doc_vectors[chunk_id] = compute_embeddings(chunk_dict.get("text"))
        # Store the document's chunk embeddings mapped by their chunk UUIDs
        vector_store[doc_id] = doc_vectors
    with open(vector_store_path, 'w') as f:
        json.dump(vector_store, f)
    
    return vector_store


def compute_matches(vector_store, query_str, top_k):
    """
    This function takes in a vector store dictionary, a query string, and an int 'top_k'.
    It computes embeddings for the query string and then calculates the cosine similarity against every chunk embedding in the dictionary.
    The top_k matches are returned based on the highest similarity scores.
    """
    # Get the embedding for the query string
    query_str_embedding = np.array(compute_embeddings(query_str))
    scores = {}

    # Calculate the cosine similarity between the query embedding and each chunk's embedding
    for doc_id, chunks in vector_store.items():
        for chunk_id, chunk_embedding in chunks.items():
            chunk_embedding_array = np.array(chunk_embedding)
            # Normalize embeddings to unit vectors for cosine similarity calculation
            norm_query = np.linalg.norm(query_str_embedding)
            norm_chunk = np.linalg.norm(chunk_embedding_array)
            if norm_query == 0 or norm_chunk == 0:
                # Avoid division by zero
                score = 0
            else:
                score = np.dot(chunk_embedding_array, query_str_embedding) / (norm_query * norm_chunk)

            # Store the score along with a reference to both the document and the chunk
            scores[(doc_id, chunk_id)] = score

    # Sort scores and return the top_k results
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    top_results = [(doc_id, chunk_id, score) for ((doc_id, chunk_id), score) in sorted_scores]

    return top_results