import os
from langchain_community.document_loaders import PyPDFLoader,CSVLoader,TextLoader,DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance
from dotenv import load_dotenv

load_dotenv()

class Ingest:
    def __init__(self,dataPath:str="./datasource",dbPath:str="./db/qdrant",collection_name:str="rag",embedding_model:str="sentence-transformers/all-MiniLM-L6-v2",qdrant_api_key:str="PLACE YOUR API KEY HERE"):
        
        self.dataPath=dataPath
        self.dbPath=dbPath
        self.embedding_model=embedding_model
        self.collection_name=collection_name
        self.client=QdrantClient(
            url=self.dbPath,
            api_key=qdrant_api_key
        )

    def __document_loader(self)->list:

        if not os.path.exists(self.dataPath):
            print(f"Directory not found: '{self.dataPath}'")
            return []

        documents=[]

        for root,_,files in os.walk(self.dataPath):
            for file in files:
                filePath=os.path.join(root,file)
                relativePath=os.path.relpath(filePath,self.dataPath)
                pathParts=relativePath.split(os.sep)

                category=pathParts[0] if len(pathParts)>0 else "general"
                sub_category=pathParts[1] if len(pathParts)>1 else "general"

                loader=None

                if(pathParts[-1].endswith(".pdf")):
                    loader=PyPDFLoader(filePath)
                elif(pathParts[-1].endswith(".csv")):
                    loader=CSVLoader(filePath)
                elif(pathParts[-1].endswith(".txt")):
                    loader=TextLoader(filePath)

                if loader is None:
                    print(f"Unsupported file type: '{filePath}'")
                    continue
                
                docs=loader.load()
                for doc in docs:
                    doc.metadata.update(
                        {
                        "source": filePath,
                        "doc_type": file.split(".")[-1],
                        "category": category,
                        "sub_category": sub_category,
                        "document_name": file
                        }
                    )
                    documents.append(doc)
        return documents

    def __chunking(self,documents:list=[])->list:
        if(len(documents)==0):
            print("No documents to ingest")
            return

        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n","\n"," ",""]
        )
        chunks=text_splitter.split_documents(documents)

        for i,chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "chunk_id": i,
                    "token_count": len(chunk.page_content.split())
                }
            )

        return chunks

    def __embedding(self,chunks:list=[])->None:
        if(len(chunks)==0):
            print("No chunks to ingest")
            return

        embeddings=HuggingFaceEmbeddings(model_name=self.embedding_model)

        collections = [c.name for c in self.client.get_collections().collections]

        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=len(embeddings.embed_query("test")),
                    distance=Distance.COSINE,
            ),
        )

        vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=embeddings,
        )

        vectorstore.add_documents(chunks)



    def ingest(self)->None:
        print(f"Ingesting documents from {self.dataPath}...")
        docs=self.__document_loader()
        print(f"Loaded {len(docs)} documents.")
        chunks=self.__chunking(docs)
        print(f"Split {len(chunks)} chunks.")
        self.__embedding(chunks)
        print(f"Ingested {len(chunks)} chunks into {self.dbPath}.")
        self.client.close()
