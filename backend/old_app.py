import time
import os

from dotenv import load_dotenv
import chromadb
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import fitz
import tempfile
import base64
import io
import logging

import utils._global as _global
from utils.pdf_funcs import add_pdf_from_dir, get_pdf_page_image, chunk_and_add_pdf_to_chroma
from utils.print_results import print_results

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

chroma_client = chromadb.HttpClient(
    host="chromadb",
    port=8000
)

collection = chroma_client.get_or_create_collection(_global.doc_collection_name)

# Who is Nhimbaloth?

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def query():
    def sort_processed_results(e):
        return e['distance']
    
    app.logger.info('Query endpoint called.')
    try:
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

    elif file:
        file_path = os.path.join(_global.pdf_data_path, file.filename)
        if os.path.isfile(file_path):
            return jsonify({'message': 'File already exists.', 'file_path': file_path}), 404
        file.save(file_path)
    
    chunk_and_add_pdf_to_chroma(chroma_client, file_path)
    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200


@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


# def main():
#     load_dotenv()

#     # chroma_client = chromadb.HttpClient(host='localhost', port=8000)
#     chroma_client = chromadb.PersistentClient(path='chroma_data')
#     dir_path = _global.pdf_data_path
#     add_pdf_from_dir(chroma_client, dir_path) 

#     query_str = "Who is Nhimbaloth?"

#     collection = chroma_client.get_collection(_global.doc_collection_name)
#     results = collection.query(
#         query_texts=[query_str],
#         n_results=5
#     )
#     print_results(results)



if __name__ == '__main__':
    start = time.time()
    app.run(host="0.0.0.0", port=5001)
    # main()
    print(f'Function took {round(time.time() - start, 2)}')

