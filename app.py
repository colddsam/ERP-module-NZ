from fastapi import FastAPI, HTTPException
from utils.rag import RagEngine
from utils.ingest import Ingest
from schemas.schemas import QueryRequest, QueryResponse, IngestResponse
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH") or "./datasource"
DB_PATH = os.getenv("QDRANT_ENDPOINT") or "./db/qdrant"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME") or "rag"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = os.getenv("LLM_MODEL") or "gemini-2.5-flash"

rag_engine: RagEngine | None = None
ingest_engine: Ingest | None = None
qdrant_client: QdrantClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_engine, ingest_engine, qdrant_client

    if DB_PATH.startswith("http") and QDRANT_API_KEY is not None:
        qdrant_client = QdrantClient(
            url=DB_PATH,
            api_key=QDRANT_API_KEY,
        )
    else:
        qdrant_client = QdrantClient(path=DB_PATH)

    rag_engine = RagEngine(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        google_api_key=GOOGLE_API_KEY,
        embedding_model=EMBEDDING_MODEL,
        llm_model=LLM_MODEL,
    )

    ingest_engine = Ingest(
        dataPath=DATA_PATH,
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        embedding_model=EMBEDDING_MODEL,
    )

    yield 

    rag_engine = None
    ingest_engine = None
    qdrant_client = None

app = FastAPI(
    title="RAG Customer Support API",
    description="FastAPI wrapper for LangChain + Qdrant RAG",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def root():
    return {"message": "Welcome to the RAG Customer Support API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    try:
        answer = rag_engine.get_answer(payload.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
def ingest_data():
    if not ingest_engine:
        raise HTTPException(status_code=503, detail="Ingest engine not initialized")

    try:
        ingest_engine.ingest()
        return IngestResponse(status="ok", message="Data ingested successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
