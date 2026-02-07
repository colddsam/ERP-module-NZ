from service.rag import RagEngine
from service.ingest import Ingest

if __name__=="__main__":
    ingest=Ingest()
    ingest.ingest()
    