import os
import base64
import multiprocessing as mp
import time
import requests
import asyncio

import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from linetimer import CodeTimer
from sentence_transformers import SentenceTransformer

import utils._global as _global
# from utils.multiprocessing_funcs import *
from utils.collection_funcs import get_collection, add_to_collection
from utils.multiprocessing_funcs import get_chunks_and_consume

# embedding_model_name = "all-MiniLM-L6-v2"
# embedding_model_name = "paraphrase-albert-small-v2"
embedding_model_name = "paraphrase-MiniLM-L3-v2"


class CustomSentenceTransformerEmbeddingFunction:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input):
        return self.model.encode(input)


#Chroma
def get_collection():
    chroma_client = chromadb.HttpClient(
    host="127.0.0.1",
    port=_global.chroma_port
    )   

    # sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    #     model_name=embedding_model_name, 
    #     device=_global.device
    #     )

    sentence_transformer_ef = CustomSentenceTransformerEmbeddingFunction(embedding_model_name)
    collection = chroma_client.get_or_create_collection(
        name=_global.doc_collection_name,
        embedding_function=sentence_transformer_ef
    )
    return collection

# # Milvus
# def check_collection():
    
#     client = MilvusClient(_global.doc_collection_name + '.db')
#     if not client.has_collection(_global.doc_collection_name):
#         client.create_collection(
#             collection_name=_global.doc_collection_name,
#             dimension=768,  # The vectors we will use in this demo has 768 dimensions
#         )
    

#     return True


def delete_collection():
    chroma_client = chromadb.HttpClient(
    host="127.0.0.1",
    port=_global.chroma_port
    )   

    chroma_client.delete_collection(_global.doc_collection_name)

# Chroma
def add_to_collection(data_list):
    with CodeTimer('Get Collection'):
        documents, metadatas, ids = data_list
        collection = get_collection()
    
    with CodeTimer('Embedding'):
        embedding_model= SentenceTransformer(
        embedding_model_name, 
        )

        embeddings = embedding_model.encode(documents).tolist()


    with CodeTimer('Add to collection'):
        collection.add(
            # documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )



def produce_pdf_chunks(file_path: str):
    pdf_loader = PyPDFLoader(file_path)
    document = pdf_loader.load()
    # print(document)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=_global.CHUNK_SIZE,
        chunk_overlap=100
    )

    chunked_documents = []

    documents = []
    metadatas = []
    ids = []

    page = 0
    page_index = 0

    for page_chunk in text_splitter.split_documents(document):
        if page > page_chunk.metadata['page']:
            page = page_chunk.metadata['page']
            page_index = 0
        
        documents.append(page_chunk.page_content)
        metadatas.append(page_chunk.metadata)
        ids.append(f"{page_chunk.metadata['source']}-{page_chunk.metadata['page']}-{page_index}")    

        page_index += 1

        if len(ids) >= _global.BATCH_SIZE:
            chunked_documents.append((documents, metadatas, ids))
            documents = []
            metadatas = []
            ids = []


    if len(ids) > 0:
        chunked_documents.append((documents, metadatas, ids))

    return chunked_documents


async def consume_pdf_chunks(data_list: list[list,list,list]):
    add_to_collection(data_list)

    return f"Data Added."


async def get_chunks_and_consume(filepath: str):
    with CodeTimer('Produce Chunks'):
        chunked_documents = produce_pdf_chunks(filepath)
        print('chunked documents made')

    with CodeTimer('Tasks'):
        results = []
        # for chunk in chunked_documents:
        #     results.append(add_to_collection(chunk))
        tasks = [consume_pdf_chunks(chunk_data) for chunk_data in chunked_documents]
        results = await asyncio.gather(*tasks)
        return results



def main():

    try:
        file_path = '/Users/elieltaskinen/Projects/RPG_RAG/backend/data/Lost Omens - Gods & Magic (1).pdf'
        chunk_results = asyncio.run(get_chunks_and_consume(file_path))
        # print(results)

        collection = get_collection()
        query_text = "What are the outer gods?"
        results = collection.query(
            query_texts=[query_text],
            n_results=5
        )
    except Exception as err:
        delete_collection()
        raise err


if __name__ == '__main__':
    main()