import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Support RAG Bot", layout="centered")
st.title("💬 AngelOne Support Chatbot")

question = st.text_input("Ask a question based on support docs:")

if st.button("Ask") and question:
    with st.spinner("Generating answer..."):
        res = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
        answer = res.json().get("answer", "Error occurred")
        st.markdown(f"**Answer:** {answer}")