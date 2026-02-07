from config.rag import get_rag_client

class RagEngine:
    def __init__(self):
        self.rag_client = get_rag_client()
    
    def get_answer(self,question:str)->str:
        response = self.rag_client.invoke({
            "query": question
        })
        answer = response['result']
        return answer

