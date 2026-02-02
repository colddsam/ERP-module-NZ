from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RagEngine:
    def __init__(self,dbPath:str="db/chroma"):
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
            model_name=os.getenv("EMBEDDING_MODEL")
            )
        self.vectorstore = Chroma(
            persist_directory=dbPath,
            embedding_function=self.embeddings
            )
        self.model = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
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
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": self.prompt_template}
            )
    
    def get_answer(self,question):
        response = self.retrieval_qa.invoke({
            "query": question
        })
        answer = response['result']
        return answer

