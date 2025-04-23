import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", 10000))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HOST = "0.0.0.0"  # Add this line