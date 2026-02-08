import io
from fastapi import FastAPI, HTTPException,UploadFile, File,Form,BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
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
async def ask_question(payload: QueryRequest):
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    try:
        result = await rag_engine.get_answer(
            company_name=payload.company_name,
            question=payload.query,
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/ingest/company", response_model=IngestResponse)
async def ingest_company_documents(
    company_name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    if not ingest_engine:
        raise HTTPException(status_code=503, detail="Ingest engine not initialized")

    try:
        files_data = [
            {
                "filename": f.filename,
                "content": await f.read()
            }
            for f in files
        ]

        num_chunks = ingest_engine.ingest_company_data(
            company_name,
            files_data,
        )

        return IngestResponse(
            status="success",
            message=f"Ingestion complete for company '{company_name}'. Processed {num_chunks} chunks."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/receipt/parse", response_model=ReceiptParseResponse)
async def parse_receipt(files: List[UploadFile] = File(...)):
    if not all([ocr_service, raw_text2json, database_operations]):
        raise HTTPException(status_code=503, detail="Services not initialized")

    parsed_results = []

    try:
        for file in files:
            content = await file.read()

            try:
                ocr_text = ocr_service.extract_text(
                    file_bytes=content,
                    content_type=file.content_type
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )

            if not ocr_text.strip():
                continue

            parsed_receipt = raw_text2json.parse_receipt(ocr_text)

            if not parsed_receipt:
                continue

            receipt_id = database_operations.save_receipt(parsed_receipt)

            parsed_results.append({
                "filename": file.filename,
                "receipt_id": receipt_id,
                "data": parsed_receipt
            })

        if not parsed_results:
            raise HTTPException(
                status_code=422,
                detail="No valid receipts found in uploaded files"
            )

        return ReceiptParseResponse(
            status="success",
            data=parsed_results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )