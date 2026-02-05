import os



# --- Text Processing Settings ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Directory Settings ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
PERSIST_DIRECTORY = "chroma_db"

# --- Model Settings ---
# You can swap these out for testing different models easily
LLM_MODEL_ID = "openai/gpt-oss-20b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Web Search Settings ---
SEARCH_DOMAINS = ["google.com"]
MAX_SEARCH_RESULTS = 2