from fastapi import FastAPI, HTTPException
from utils.rag import RagEngine
from utils.ingest import Ingest
from schemas.schemas import QueryRequest, QueryResponse, IngestResponse
import os
from dotenv import load_dotenv

load_dotenv()

dbPath=os.getenv("QDRANT_ENDPOINT")
qdrant_api_key=os.getenv("QDRANT_API_KEY")
collection_name=os.getenv("COLLECTION_NAME")
google_api_key=os.getenv("GOOGLE_API_KEY")
embedding_model=os.getenv("EMBEDDING_MODEL")
llm_model=os.getenv("LLM_MODEL")

app = FastAPI(
    title="RAG Customer Support API",
    description="FastAPI wrapper for LangChain + Qdrant RAG",
    version="1.0.0"
)

rag_engine: RagEngine | None = None
ingest: Ingest | None = None

@app.on_event("startup")
def startup_event():
    global rag_engine
    global ingest

    rag_engine = RagEngine(
        dbPath=os.getenv("QDRANT_ENDPOINT"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        collection_name=os.getenv("COLLECTION_NAME"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        llm_model=os.getenv("LLM_MODEL"),
    )
    ingest = Ingest(
        dbPath=os.getenv("QDRANT_ENDPOINT"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        collection_name=os.getenv("COLLECTION_NAME"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
    )

@app.get("/")
def root():
    return {"message": "Welcome to the RAG Customer Support API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    try:
        answer = rag_engine.get_answer(payload.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest", response_model=IngestResponse)
def ingest_data():
    try:
        ingest.ingest()
        return IngestResponse(status="ok", message="Data ingested successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

