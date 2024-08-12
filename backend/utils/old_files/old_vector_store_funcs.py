import chromadb

import utils._global as _global

def add_to_chroma_store(collection: chromadb.Collection, docs_input: dict):
    documents = []
    ids = []
    metadata = []


    for filename, file_data in docs_input.items():
        i_count = 0

        for chunk in file_data:
            documents.append(chunk['text'])
            ids.append(f'{chunk['metadata']['file_name']}-{i_count}')
            metadata.append(chunk['metadata'])
            i_count += 1

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadata
    )



def query_collection(collection: chromadb.Collection, query_lst: list[str], result_count=3):
    results = collection.query(
        query_texts=query_lst,
        n_results=result_count
    )

    return results

