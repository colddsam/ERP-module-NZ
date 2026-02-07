import os
from langchain_community.document_loaders import (
    PyPDFLoader, CSVLoader, TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance
from dotenv import load_dotenv
from config.ingest import *
from config.qdrant import get_qdrant_vectorstore

load_dotenv()


class Ingest:
    def __init__(
        self,
    ):
        self.dataPath = DATA_PATH
        self.vectorstore = get_qdrant_vectorstore()

    def __document_loader(self) -> list:
        if not os.path.exists(self.dataPath):
            print(f"Directory not found: {self.dataPath}")
            return []

        documents = []

        for root, _, files in os.walk(self.dataPath):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.dataPath)
                path_parts = relative_path.split(os.sep)

                category = path_parts[0] if len(path_parts) > 0 else "general"
                sub_category = path_parts[1] if len(path_parts) > 1 else "general"

                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                elif file.endswith(".csv"):
                    loader = CSVLoader(file_path)
                elif file.endswith(".txt"):
                    loader = TextLoader(file_path)
                else:
                    continue

                docs = loader.load()
                for doc in docs:
                    doc.metadata.update({
                        "source": file_path,
                        "doc_type": file.split(".")[-1],
                        "category": category,
                        "sub_category": sub_category,
                        "document_name": file,
                    })
                    documents.append(doc)

        return documents

    def __chunking(self, documents: list) -> list:
        if not documents:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

        chunks = splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i

        return chunks

    def __embedding(self, chunks: list) -> None:
        if not chunks:
            print("No chunks to ingest")
            return

        BATCH_SIZE = 64

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            self.vectorstore.add_documents(batch)
            print(f"Ingested batch {i // BATCH_SIZE + 1}")

    def ingest(self) -> None:
        print(f"Ingesting documents from {self.dataPath}")

        docs = self.__document_loader()
        print(f"Loaded {len(docs)} documents")

        chunks = self.__chunking(docs)
        print(f"Created {len(chunks)} chunks")

        self.__embedding(chunks)

        print("Ingestion completed successfully")
