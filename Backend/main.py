from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["TOKENIZERS_PARALLELISM"] = os.getenv("TOKENIZERS_PARALLELISM", "false")

# Load data
try:
    documents = pickle.load(open("data_preparation/data/documents.pkl", "rb"))
    index = faiss.read_index("data_preparation/data/faiss_index.index")
except FileNotFoundError:
    # Try alternative paths for deployment
    documents = pickle.load(open("../data_preparation/data/documents.pkl", "rb"))
    index = faiss.read_index("../data_preparation/data/faiss_index.index")

model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

# Update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    question = query.question
    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding).astype("float32"), k=3)

    retrieved_docs = [documents[i] for i in I[0] if i != -1 and D[0][list(I[0]).index(i)] > 0.7]

    if not retrieved_docs:
        return {"answer": "I don't know."}

    context = "\n".join(retrieved_docs)
    prompt = f"Answer the question based on the context below.\nIf the answer is not in the context, say 'I don't know.'\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    return {"answer": answer.strip()}

# Add this to make the app run when the file is executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))  # Changed default port to 10000
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=120,  # Increased keep-alive timeout
        workers=4,  # Number of worker processes
        timeout=120  # Request timeout
    )