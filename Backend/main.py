from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Pre-load everything during startup
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # Add device parameter
documents = pickle.load(open("data/documents.pkl", "rb"))
index = faiss.read_index("data/faiss_index.index")

app = FastAPI()

# Define Query class before it's used
class Query(BaseModel):
    question: str

# Update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with correct path
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Add keepalive endpoint
@app.get("/ping")
async def ping():
    return {"status": "ready"}
    
# Serve index.html at root
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Remove the duplicate home() route:
# @app.get("/")
# def home():
#     return {"message": "Hello from RAG Chatbot!"}

    
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

# Remove the if __name__ == "__main__" block completely# The application will be run by Gunicorn instead
