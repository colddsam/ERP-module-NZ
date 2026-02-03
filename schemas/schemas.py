from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

class IngestResponse(BaseModel):
    status: str
    message: str

