# ERP-module-NZ — RAG Customer Support System

A **Retrieval-Augmented Generation (RAG)** based customer support system built with:

- **LangChain**
- **Qdrant Vector DB**
- **HuggingFace Embeddings**
- **Google Gemini (LLM)**
- **FastAPI**

This project allows you to:
1. Ingest documents (PDF, CSV, TXT)
2. Store embeddings in Qdrant Vector DB
3. Ask natural-language questions via API
4. Get answers strictly from your documents with sources

---

## 🧠 Architecture Overview

```
Documents → Ingestion → Chunking → Embeddings → Qdrant
↓
Retrieval
↓
Gemini LLM
↓
FastAPI API
```

---

## 📦 Requirements

- Python **3.9+**
- Google Gemini API key
- Qdrant Cloud Cluster (or local instance)
- Git

---

## 📥 1. Clone the Repository

```bash
git clone https://github.com/colddsam/ERP-module-NZ.git
cd ERP-module-NZ
```

---

## 🧪 2. Create Virtual Environment (Recommended)

### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 4. Environment Configuration

Create a `.env` file in the project root:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gemini-2.0-flash-exp
GOOGLE_API_KEY=your_google_api_key_here
QDRANT_ENDPOINT=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=rag
```

---

## 📂 5. Document Structure (IMPORTANT)

Documents must be placed inside `datasource/` with **folder-based metadata**.

```
datasource/
├── hr/
│   ├── policies/
│   │   └── leave_policy.pdf
├── finance/
│   └── invoices.csv
├── support/
│   └── faq.txt
```

### Metadata Automatically Generated

Each chunk contains:

* `category`
* `sub_category`
* `doc_type`
* `document_name`
* `chunk_id`
* `token_count`
* `source`

---

## 📥 6. Ingest Documents into Vector DB

Run the ingestion script:

```bash
python main.py
```

### What this does:

* Loads PDF / CSV / TXT files
* Splits text into chunks
* Creates embeddings using HuggingFace
* Stores vectors in **Qdrant**

Output example:

```
Ingesting documents from ./datasource...
Loaded 12 documents.
Split 240 chunks.
Ingested 240 chunks into https://xxx.qdrant.tech.
```

---

## 🧠 7. RAG Engine (How Q&A Works)

The `RagEngine`:

* Retrieves relevant chunks from Qdrant
* Uses **strict prompting**
* Answers **only from documents**
* Returns source-backed answers

If information is missing, it responds:

```
"I don't have that information in our documents."
```

---

## 🚀 8. Start the FastAPI Server

```bash
uvicorn app:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## 🩺 9. Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## ❓ 10. Ask a Question (API)

### Endpoint

```http
POST /ask
```

### Request Body

```json
{
  "query": "What is the leave policy?"
}
```

### Response

```json
{
  "answer": "Employees are entitled to 24 annual leaves per year. (Source: leave_policy.pdf)"
}
```

---

## 🗂 Project Structure

```
ERP-module-NZ/
├── datasource/              # Input documents
├── utils/
│   ├── rag.py               # RAG engine
│   └── ingest.py            # Document ingestion logic
├── schemas/
│   └── schemas.py           # Request / response models
├── app.py                   # FastAPI application
├── main.py                  # Ingestion Entry point
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
└── README.md                # Project documentation
```

---

## 🔒 Prompt Safety Rules

* Answers ONLY from provided context
* No hallucinations
* Always includes source
* Fixed fallback response when data is missing

---

## 📌 Use Cases

* Customer Support Chatbot
* Internal Knowledge Base
* HR Policy Assistant
* ERP / Enterprise Q&A
* Document-grounded AI APIs

---

## 📄 License

Licensed under **Apache 2.0**

---

## ✨ Future Improvements

* Metadata-based filtering
* Streaming responses
* Authentication
* Multi-tenant vector stores
* UI dashboard

---

## 🤝 Contributions

Pull requests are welcome.
For major changes, please open an issue first.
