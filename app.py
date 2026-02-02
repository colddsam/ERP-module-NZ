from fastapi import FastAPI, HTTPException
from utils.rag import RagEngine
from schemas.schemas import QueryRequest, QueryResponse

app = FastAPI(
    title="RAG Customer Support API",
    description="FastAPI wrapper for LangChain + Chroma RAG",
    version="1.0.0"
)

rag_engine = RagEngine(dbPath="db/chroma")

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
