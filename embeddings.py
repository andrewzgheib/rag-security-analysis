import google.genai as genai
from config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")

if not GEMINI_EMBEDDING_MODEL:
    raise EnvironmentError("GEMINI_EMBEDDING_MODEL is not set in your config.py file.")

CLIENT = genai.Client(api_key=GEMINI_API_KEY)

def embed_documents(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        for text in batch:
            response = CLIENT.models.embed_content(model=GEMINI_EMBEDDING_MODEL, contents=text)
            all_embeddings.append(response.embeddings[0].values)

    return all_embeddings

def embed_query(query: str) -> list[float]:
    response = CLIENT.models.embed_content(model=GEMINI_EMBEDDING_MODEL, contents=query)

    return response.embeddings[0].values