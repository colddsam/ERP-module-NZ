import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

_QDRANT_CLIENT = None

_QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT") or "./db/qdrant"
_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
_COMPANY_NAME = os.getenv("COLLECTION_NAME") or "aeeris"

_EMBEDDINGS = None

def get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name=_EMBEDDING_MODEL)
    return _EMBEDDINGS

def get_qdrant_client() -> QdrantClient:
    global _QDRANT_CLIENT

    if _QDRANT_CLIENT is None:
        if _QDRANT_ENDPOINT.startswith("http") and _QDRANT_API_KEY:
            _QDRANT_CLIENT = QdrantClient(
                url=_QDRANT_ENDPOINT,
                api_key=_QDRANT_API_KEY,
                timeout=60,
            )
        else:
            _QDRANT_CLIENT = QdrantClient(path=_QDRANT_ENDPOINT,timeout=60)

    return _QDRANT_CLIENT


def get_company_vectorstore(company_name: str = _COMPANY_NAME) -> QdrantVectorStore:
    client = get_qdrant_client()

    collection_name = company_name.lower().replace(" ", "_")

    embeddings = get_embeddings()

    existing = [c.name for c in client.get_collections().collections]

    if collection_name not in existing:
        vector_size = len(embeddings.embed_query("dimension-check"))

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
