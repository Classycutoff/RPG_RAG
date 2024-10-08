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

import utils._global as _global
from utils.pdf_funcs import add_pdf_from_dir, get_pdf_page_image, chunk_and_add_pdf_to_chroma
from utils.print_results import print_results
from utils.multiprocessing_funcs import (
    produce_pdf_chunks,
    consume_pdf_chunks,
    get_chunks_and_consume
)
from utils.collection_funcs import get_collection

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def query():
    def sort_processed_results(e):
        return e['distance']
    
    app.logger.info('Query endpoint called.')
    try:
        ## TODO!
        collection = get_collection()
        query_text = request.json['query']
        results = collection.query(
            query_texts=[query_text],
            n_results=5
        )

        processed_results = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            pdf_path = metadata.get('source')
            page_num = metadata.get('page', 0)
            distance = round(results['distances'][0][i], 2)

            image_data = get_pdf_page_image(pdf_path, page_num)

            processed_results.append({
                'text': doc,
                'metadata': metadata,
                'image': image_data,
                'distance': distance
            })
        
        processed_results.sort(key=sort_processed_results)
    
        app.logger.info(f'Returning {len(processed_results)} results')
        return jsonify(processed_results)
    except Exception as e:
        app.logger.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500



@app.route('/api/add-file', methods=['POST'])
def add_files():
    app.logger.info(request.files['file'])

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    elif not file:
        return jsonify({'message': 'The object uploaded wasn\'t a file, try again'}), 404
    

    file_path = os.path.join(_global.pdf_data_path, file.filename)
    if os.path.isfile(file_path):
        return jsonify({'message': 'File already exists.', 'file_path': file_path}), 404
    file.save(file_path)

    print('Starting multiprocessing...')

    test_collection = get_collection()

    results = asyncio.run(get_chunks_and_consume(file_path))
    print('Execution Done.')

    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200


@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    start = time.time()
    app.run(host="0.0.0.0", port=5001)
    # main()
    print(f'Function took {round(time.time() - start, 2)}')

