import os
import base64
import multiprocessing as mp
import time

import chromadb
import fitz
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from linetimer import CodeTimer

import utils._global as _global
# from utils.multiprocessing_funcs import *


chroma_client = chromadb.PersistentClient('./chroma')

device = 'cpu'
# embedding_function = SentenceTransformerEmbeddings(model_name=_global.embedding_model_name)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=_global.embedding_model_name, device=device)
collection = chroma_client.get_or_create_collection(
    _global.doc_collection_name, 
    embedding_function=sentence_transformer_ef
)



def produce_pdf_chunks_to_queue(queue: mp.Queue, file_path: str):
    pdf_loader = PyPDFLoader(file_path)
    document = pdf_loader.load()
    # print(document)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=_global.CHUNK_SIZE,
        chunk_overlap=100
    )

    documents = []
    metadatas = []
    ids = []

    _global.page_count = len(document)

    for page in document:
        word_count = len(page.page_content.split())
        # print(f'Word count: {word_count}')
        if word_count <= _global.MIN_WORDS_PER_PAGE:
            continue


        chunked_page = text_splitter.split_text(page.page_content)

        for i, chunk in enumerate(chunked_page):
            documents.append(chunk)
            metadatas.append(page.metadata)
            ids.append(f"{page.metadata['source']}-{page.metadata['page']}-{i}")

        if len(ids) >= _global.BATCH_SIZE:
            print('Added to queue')
            queue.put((documents, metadatas, ids))
            documents = []
            metadatas = []
            ids = []


    if len(ids) > 0:
        queue.put((documents, metadatas, ids))


def consume_chunks_to_chromadb(queue: mp.Queue, use_cuda: bool):
    while True:
        batch = queue.get()

        if batch is None:
            break

        collection.add(
            documents=batch[0],
            metadatas=batch[1],
            ids=batch[2]
        )
        print('Consumed')
    


def main():
    with CodeTimer():
        print('Starting multiprocessing...')

        file_path = "/Users/elieltaskinen/Projects/RPG_RAG/databases/pdf_data/PF 2E - Conversion Guide from PF1E.pdf"

        produce_and_consume_queue = mp.Queue()
        produce_chunks_process = mp.Process(target=produce_pdf_chunks_to_queue, args=(produce_and_consume_queue, file_path))
        consume_chunks_process = mp.Process(target=consume_chunks_to_chromadb, args=(produce_and_consume_queue, True))

        start_time = time.time()

        # Start processes
        produce_chunks_process.start()
        consume_chunks_process.start()

        # Wait for producer to finish producing
        produce_chunks_process.join()

        # Signal consumer to stop consuming by putting None into the queue. Need 2 None's to stop 2 consumers.    
        produce_and_consume_queue.put(None)

        # Wait for consumer to finish consuming
        consume_chunks_process.join()

        print(f"Elapsed seconds: {time.time()-start_time:.0f} Record count: {collection.count()}")

        results = collection.query(
            query_texts=['How to convert to pf2e?'],
            n_results=5
        )
        
        print(results)


if __name__ == '__main__':
    main()