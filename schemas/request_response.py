from pydantic import BaseModel
from typing import List, Optional

class Citation(BaseModel):
    source: str          
    page: Optional[int]  
    snippet: str         
    score: float         

class QueryRequest(BaseModel):
    company_name: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[Citation]

class IngestResponse(BaseModel):
    status: str
    message: str

class ReceiptParseResponse(BaseModel):
    status: str
    data: dict
    receipt_id: int