import requests
from bs4 import BeautifulSoup
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

BASE_URL = "https://www.angelone.in/support"

# You would expand this to get all child URLs under the support section.
PAGES = [
    BASE_URL,
    BASE_URL + "/account-opening",
    BASE_URL + "/funds",
    BASE_URL + "/ipo",
    BASE_URL + "/stocks",
    # Add more URLs after crawling
]

def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    texts = soup.find_all(["p", "li"])
    return "\n".join([t.get_text().strip() for t in texts if t.get_text().strip()])

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = []
embeddings = []

for url in PAGES:
    text = fetch_text_from_url(url)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    documents.extend(chunks)
    embeddings.extend(model.encode(chunks))

# Save docs
os.makedirs("data", exist_ok=True)
pickle.dump(documents, open("data/documents.pkl", "wb"))

# Save FAISS index
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings).astype("float32"))
faiss.write_index(index, "data/faiss_index.index")

print("Documents and index saved.")