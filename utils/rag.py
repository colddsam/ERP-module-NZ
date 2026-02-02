from langchain_chroma import Chroma
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RagEngine:
    def __init__(self,qdrant_api_key:str="PLACE YOUR API KEY HERE",google_api_key:str="PLACE YOUR API KEY HERE",dbPath:str="./db/qdrant",embedding_model:str="sentence-transformers/all-MiniLM-L6-v2",collection_name:str="rag",llm_model:str="gemini-2.0-flash-exp"):
        self.PROMPT_TEMPLATE = """
            You are a customer support assistant for a business.

            Use ONLY the information provided in the context below to answer the question.
            If the answer is NOT present in the context, say exactly:
            "I don't have that information in our documents."

            Always include the source of the information.

            Context:
            {context}

            Question:
            {question}

            Answer (with source):
            """
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
            )

        self.client = QdrantClient(
            url=dbPath,
            api_key=qdrant_api_key
            )
        self.vectorstore = QdrantVectorStore(
            client=self.client, 
            collection_name=collection_name, 
            embedding=self.embeddings
            )
        self.model = ChatGoogleGenerativeAI(
            model=llm_model,
            google_api_key=google_api_key,
            temperature=0.0,
            max_output_tokens=512,
            convert_system_message_to_human=True
            )
        self.prompt_template = PromptTemplate.from_template(
            template=self.PROMPT_TEMPLATE,
            )
        self.retrieval_qa = RetrievalQA.from_chain_type(
            llm=self.model,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": self.prompt_template}
            )
    
    def get_answer(self,question):
        response = self.retrieval_qa.invoke({
            "query": question
        })
        answer = response['result']
        return answer

