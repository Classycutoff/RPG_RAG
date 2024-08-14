import os
import base64

import chromadb
import fitz
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

import utils._global as _global


def chunk_and_add_pdf_to_chroma(chroma_client: chromadb.HttpClient, file_path: str):
    embedding_function = SentenceTransformerEmbeddings(model_name=_global.embedding_model_name)

    pdf_loader = PyPDFLoader(file_path)
    document = pdf_loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=_global.CHUNK_SIZE,
        chunk_overlap=100
    )

    chunked_documents = text_splitter.split_documents(document)

    Chroma.from_documents(
        documents=chunked_documents,
        embedding=embedding_function,
        collection_name=_global.doc_collection_name,
        client=chroma_client
    )



def add_pdf_from_dir(chroma_client: chromadb.HttpClient, dir_path: str):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        chunk_and_add_pdf_to_chroma(chroma_client, file_path)


def get_pdf_page_image(pdf_path: str, page_num: int):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap()

    img_data = pix.tobytes('png')
    encoded_img = base64.b64encode(img_data).decode('utf-8')

    return f'data:image/png;base64,{encoded_img}'
