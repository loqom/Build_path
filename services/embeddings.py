# Handles all ChromaDB operations. Initializes the ChromaDB client and collection, embeds text using Mistral's embedding model, stores embeddings, and queries for similar content. Called by Clustering Agent.

from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_chroma import Chroma
from config.settings import settings

embeddings=MistralAIEmbeddings(api_key=settings.MISTRAL_API_KEY,model="mistral-embed")

vector_store = Chroma(
    collection_name="buildpath_pain_points",
    embedding_function=embeddings,
    persist_directory=settings.CHROMA_DB_PATH
)

def add_documents(texts: list[str], metadatas: list[dict] = None):
    vector_store.add_texts(texts=texts, metadatas=metadatas)

def query_similar(query: str, k: int = 10) -> list:
    return vector_store.similarity_search(query, k=k)