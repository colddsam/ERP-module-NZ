from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
load_dotenv()

_QDRANT_CLIENT = None
_QDRANT_VECTORSTORE = None

_QDRANT_COLLECTION_NAME = os.getenv("COLLECTION_NAME") or "rag"
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
_QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT") or "./db/qdrant"
_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def get_qdrant_client()->QdrantClient:
    global _QDRANT_CLIENT

    if _QDRANT_CLIENT is None:
        path = _QDRANT_ENDPOINT
        api_key = _QDRANT_API_KEY

        if path.startswith("http") and api_key:
            _QDRANT_CLIENT = QdrantClient(
                url=path,
                api_key=api_key,
            )
        else:
            _QDRANT_CLIENT = QdrantClient(path=path)

    return _QDRANT_CLIENT

def get_qdrant_vectorstore()->QdrantVectorStore:
    global _QDRANT_VECTORSTORE

    if _QDRANT_VECTORSTORE is None:
        existing = [c.name for c in get_qdrant_client().get_collections().collections]

        if _QDRANT_COLLECTION_NAME not in existing:
            vector_size = len(HuggingFaceEmbeddings(
                model_name=_EMBEDDING_MODEL
            ).embed_query("dimension-check"))
            get_qdrant_client().create_collection(
                collection_name=_QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

        _QDRANT_VECTORSTORE = QdrantVectorStore(
            client=get_qdrant_client(),
            collection_name=_QDRANT_COLLECTION_NAME,
            embedding=HuggingFaceEmbeddings(
                model_name=_EMBEDDING_MODEL
            ),
        )

    return _QDRANT_VECTORSTORE

