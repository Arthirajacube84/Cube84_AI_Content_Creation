import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Diagnostic prints for production debugging
print(f"INFO: GROQ_API_KEY is {'DETECTED' if os.getenv('GROQ_API_KEY') else 'MISSING'}")
print(f"INFO: TAVILY_API_KEY is {'DETECTED' if os.getenv('TAVILY_API_KEY') else 'MISSING'}")
print(f"INFO: Running with MODEL_NAME: {os.getenv('MODEL_NAME', 'llama-3.3-70b-versatile')}")

# API Keys
# SECURITY WARNING: For production, set these as environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY","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")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY","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")

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2000"))
