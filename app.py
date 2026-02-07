import io
from fastapi import FastAPI, HTTPException,UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from service.rag import RagEngine
from service.ingest import Ingest
from service.OCR import OCRService
from service.rawText2json import RawText2JsonService
from service.databaseOperations import DatabaseOperations
from schemas.request_response import QueryRequest, QueryResponse, IngestResponse,ReceiptParseResponse
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()


rag_engine: RagEngine | None = None
ingest_engine: Ingest | None = None
ocr_service: OCRService | None = None
raw_text2json: RawText2JsonService | None = None
database_operations: DatabaseOperations | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_engine, ingest_engine, database_operations, ocr_service, raw_text2json

    rag_engine = RagEngine()

    ingest_engine = Ingest()

    database_operations = DatabaseOperations()

    ocr_service = OCRService()

    raw_text2json = RawText2JsonService()

    yield 

    rag_engine = None
    ingest_engine = None
    database_operations = None
    ocr_service = None
    raw_text2json = None

app = FastAPI(
    title="RAG Customer Support API",
    description="FastAPI wrapper for LangChain + Qdrant RAG",
    version="1.1.0",
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

@app.post("/receipt/parse",response_model=ReceiptParseResponse)
async def parse_receipt(file: UploadFile = File(...)):
    if not database_operations:
        raise HTTPException(status_code=503, detail="Database operations not initialized")

    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")

        ocr_text = ocr_service.extract_text_from_image(image)

        if not ocr_text.strip():
            raise HTTPException(status_code=422, detail="No text detected")

        parsed_receipt = raw_text2json.parse_receipt(ocr_text)

        if not parsed_receipt:
            raise HTTPException(status_code=422, detail="Failed to parse receipt")

        receipt_data = database_operations.save_receipt(parsed_receipt)

        return ReceiptParseResponse(
            status="success",
            data=parsed_receipt,
            receipt_id=receipt_data
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )