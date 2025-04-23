import streamlit as st
import requests
import time

BACKEND_URL = "https://rag-chat-customer-support-1.onrender.com"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Support RAG Bot", layout="centered")
st.title("💬 AngelOne Support Chatbot")

# Add information about cold starts
st.info("⚠️ First request may take up to 60 seconds while the server wakes up from sleep mode.")

# Custom CSS for better chat appearance
st.markdown("""
    <style>
    .user-message {
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .bot-message {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 15px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>👤 You: {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>🤖 Bot: {message['content']}</div>", unsafe_allow_html=True)

# Chat input
question = st.text_input("Ask a question:", key="question_input")


if st.button("Send", key="send_button") and question:
    start_time = time.time()
    st.session_state.messages.append({"role": "user", "content": question})
    
    try:
        # First check if backend is awake
        requests.get(f"{BACKEND_URL}/ping", timeout=5)
        
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{BACKEND_URL}/ask",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=15  # Reduced timeout
            )
            answer = res.json().get("answer")
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
    except requests.exceptions.Timeout:
        st.error("Server timeout - please try again")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.write(f"⏱️ Response time: {time.time()-start_time:.1f}s")
    
    except requests.exceptions.Timeout:
        error_msg = "The server is still starting up. Please wait a minute and try again."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.experimental_rerun()
    except requests.exceptions.HTTPError as e:
        if "502" in str(e):
            error_msg = "The server is waking up from sleep mode. Please try again in 30-60 seconds."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            error_msg = f"Server error: {str(e)}. Please try again later."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.experimental_rerun()
    except Exception as e:
        error_msg = "Sorry, I couldn't connect to the server. Please try again."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.experimental_rerun()