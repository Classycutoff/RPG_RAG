import os
import base64
import multiprocessing as mp
import asyncio

import chromadb
import fitz
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from alive_progress import alive_bar

import utils._global as _global


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

        _global.collection.add(
            documents=batch[0],
            metadatas=batch[1],
            ids=batch[2]
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
            chunked_documents.append((documents, metadatas, ids))
            documents = []
            metadatas = []
            ids = []


    if len(ids) > 0:
        chunked_documents.append((documents, metadatas, ids))

    return chunked_documents


async def consume_pdf_chunks(batch_data: list[list,list,list]):
    documents, metadatas, ids = batch_data

    chroma_client = chromadb.HttpClient(
        host=_global.chroma_host,
        port=_global.chroma_port
    )

    collection = chroma_client.get_collection(
        name=_global.doc_collection_name,
    )

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    return f"Metadatas {len(metadatas)} added."


async def get_chunks_and_consume(filepath: str):
    chunked_documents = produce_pdf_chunks(filepath)

    tasks = [consume_pdf_chunks(chunk) for chunk in chunked_documents]
    results = await asyncio.gather(*tasks)
    return results

