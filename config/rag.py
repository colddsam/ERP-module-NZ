from config.qdrant import get_qdrant_vectorstore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

_RAG_CLIENT=None

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = os.getenv("LLM_MODEL") or "gemini-2.5-flash"

def get_rag_client()->RetrievalQA:
    global _RAG_CLIENT  

    if _RAG_CLIENT is None:

        PROMPT_TEMPLATE = """
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

        vectorstore = get_qdrant_vectorstore()

        model = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.0,
            convert_system_message_to_human=True
            )

        prompt_template = PromptTemplate.from_template(
            template=PROMPT_TEMPLATE,
            )

        _RAG_CLIENT = RetrievalQA.from_chain_type(
            llm=model,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": prompt_template}
            )

    return _RAG_CLIENT