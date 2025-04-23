# RAG Chatbot (AngelOne Support)

## 🛠 Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Data Preparation

```bash
cd data_preparation
python extract_docs.py
```

### Frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

## ✨ Features

- Retrieval-Augmented Generation chatbot
- Answers only from support documents
- Replies "I don't know" if info isn't present

## 🔐 Environment

Set `OPENAI_API_KEY` in your shell or `.env` file.
