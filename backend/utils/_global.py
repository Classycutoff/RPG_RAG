import chromadb
from chromadb.utils import embedding_functions
# model_name = "BAAI/bge-small-en-v1.5"
embedding_model_name = "all-MiniLM-L6-v2"
pdf_data_path = '/pdf_data'
doc_collection_name = 'docs_store'
# doc_store_path = "data/docs_store.json"
# vector_store_path = "data/vector_store.json"
# chroma_path = 'chroma_data'

MIN_WORDS_PER_PAGE = 20
CHUNK_SIZE = 1024
BATCH_SIZE = 100


page_count = 0
current_page_num = 0

chroma_host = 'chromadb'
chroma_port = 8000
device = 'cpu'


# chroma_client = chromadb.HttpClient(
#     host="chromadb",
#     port=8000
# )

# embedding_function = SentenceTransformerEmbeddings(model_name=_global.embedding_model_name)
# sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name, device=device)
# collection = chroma_client.get_or_create_collection(
#     doc_collection_name, 
#     embedding_function=sentence_transformer_ef
# )

