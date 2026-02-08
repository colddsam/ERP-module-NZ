import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate

from config.qdrant import get_company_vectorstore

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""
LLM_MODEL = os.getenv("LLM_MODEL") or "gemini-2.5-flash"

_RAG_CLIENTS: dict[str, RetrievalQA] = {}


def get_rag_client(company_name: str) -> RetrievalQA:
    if company_name in _RAG_CLIENTS:
        return _RAG_CLIENTS[company_name]

    PROMPT_TEMPLATE = """
You are a customer support assistant answering questions strictly from internal business documents.

INSTRUCTIONS (follow all exactly):
- Use ONLY facts explicitly stated in the context.
- Do NOT add assumptions, interpretations, or external knowledge.
- Do NOT use bullet points, lists, markdown, headings, or line breaks.
- Write the answer as ONE concise, logically ordered paragraph.
- Prefer clarity and completeness over verbosity.
- If the context does not contain enough information to answer the question, reply exactly with:
  "I don't have that information in our documents."

Context:
{context}

Question:
{question}

Answer:
"""


    vectorstore = get_company_vectorstore(company_name)

    model = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.0,
        convert_system_message_to_human=True,
    )

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    rag_client = RetrievalQA.from_chain_type(
        llm=model,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,
            },
        ),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


    _RAG_CLIENTS[company_name] = rag_client
    return rag_client
