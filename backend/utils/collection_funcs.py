import time
import os
import asyncio

from dotenv import load_dotenv
import chromadb
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import multiprocessing as mp
import fitz
import tempfile
import base64
import io
import logging
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from chromadb.utils import embedding_functions
from pymilvus import MilvusClient, model

import utils._global as _global


#Chroma
def get_collection():
    chroma_client = chromadb.HttpClient(
    host=_global.chroma_host,
    port=_global.chroma_port
    )   

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_global.embedding_model_name, 
        device=_global.device
        )
    collection = chroma_client.get_or_create_collection(
        name=_global.doc_collection_name,
        embedding_function=sentence_transformer_ef
    )
    return collection


# Chroma
def add_to_collection(data_list):
    documents, metadatas, ids = data_list
    collection = get_collection()

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )


# def add_to_collection(data_obj):
#     if not check_collection:
#         print("No collection found.")
#         return None

#     client = MilvusClient(_global.doc_collection_name + '.db')

#     res = client.insert(collection_name=_global.doc_collection_name, data=[data_obj])


#     print(res)


# # Milvus
# def check_collection():
    
#     client = MilvusClient(_global.doc_collection_name + '.db')
#     if not client.has_collection(_global.doc_collection_name):
#         client.create_collection(
#             collection_name=_global.doc_collection_name,
#             dimension=768,  # The vectors we will use in this demo has 768 dimensions
#         )
    

#     return True
