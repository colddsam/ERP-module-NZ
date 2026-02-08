from typing import Dict, List
import numpy as np
from config.rag import get_rag_client


class RagEngine:
    def __init__(self):
        pass

    async def get_answer(self, company_name: str, question: str) -> Dict:
        rag_client = get_rag_client(company_name)

        response = await rag_client.ainvoke({
            "query": question
        })

        answer = response.get("result", "")
        source_docs = response.get("source_documents", [])

        if not source_docs:
            return {
                "answer": answer,
                "confidence": 0.0,
                "citations": []
            }

        citations = []
        relevance_scores = []

        for doc in source_docs:
            score = doc.metadata.get("score", 0.75)  

            citations.append({
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page"),
                "snippet": doc.page_content[:300],
                "score": round(float(score), 2),
            })

            relevance_scores.append(score)

        avg_retrieval_score = float(np.mean(relevance_scores))
        support_ratio = min(len(source_docs) / 3, 1.0)

        confidence = round(
            0.6 * avg_retrieval_score + 0.4 * support_ratio,
            2
        )

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations
        }
