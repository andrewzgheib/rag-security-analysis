import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Models
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-2"

# Target Websites
TARGET_SITES = [
    {"url": "https://andrewzgheib.github.io", "source_tag": "andrew"},
    {"url": "https://michaelaelrif.github.io", "source_tag": "michaela"},
]

# Chunking
CHUNK_SIZE = 400 # words per chunk
CHUNK_OVERLAP = 60 # word overlap between consecutive chunks

# ChromaDB
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "website_rag"

# Retrieval
TOP_K = 5 # chunks to retrieve per query

# System Prompt (intentionally exposed here for exploit demos)
SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about two personal websites: "
    "Andrew Zgheib (andrewzgheib.github.io) and Michaela El Rif (michaelaelrif.github.io). "
    "When answering, clearly indicate which person the information refers to. "
)