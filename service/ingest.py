import os
import tempfile
from typing import List

from fastapi import UploadFile
from langchain_community.document_loaders import (
    PyPDFLoader, CSVLoader, TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.qdrant import get_company_vectorstore


class Ingest:
    def __init__(self):
        pass

    def _load_documents(self, files: list[dict]) -> list:
        documents = []

        for file in files:   
            filename = file["filename"]
            content = file["content"]
            suffix = os.path.splitext(filename)[-1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                if suffix == ".pdf":
                    loader = PyPDFLoader(tmp_path)
                elif suffix == ".csv":
                    loader = CSVLoader(tmp_path)
                elif suffix == ".txt":
                    loader = TextLoader(tmp_path)
                else:
                    continue  

                docs = loader.load()

                for doc in docs:
                    doc.metadata.update({
                        "source": filename,
                        "doc_type": suffix.replace(".", ""),
                    })
                    documents.append(doc)

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        return documents


    def _chunk(self, documents: list) -> list:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

        chunks = splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i

        return chunks

    def ingest_company_data(
    self,
    company_name: str,
    files: list[dict],
) -> int:
        documents = self._load_documents(files)
        chunks = self._chunk(documents)

        vectorstore = get_company_vectorstore(company_name)
        vectorstore.add_documents(chunks)

        return len(chunks)

