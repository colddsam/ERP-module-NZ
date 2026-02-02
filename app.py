from fastapi import FastAPI, HTTPException
from utils.rag import RagEngine
from schemas.schemas import QueryRequest, QueryResponse
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


@app.on_event("startup")
def startup_event():
    global rag_engine

    rag_engine = RagEngine(
        dbPath=os.getenv("QDRANT_ENDPOINT"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        collection_name=os.getenv("COLLECTION_NAME"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        llm_model=os.getenv("LLM_MODEL"),
    )


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
