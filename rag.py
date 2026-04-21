import google.genai as genai
from google.genai import types
from vectorstore import query_store
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, TOP_K

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")
client = genai.Client(api_key=GEMINI_API_KEY)

if not GEMINI_MODEL:
    raise EnvironmentError("GEMINI_MODEL is not set in your config.py file.")

if not SYSTEM_PROMPT:
    raise EnvironmentError("SYSTEM_PROMPT is not set in your config.py file.")

if not TOP_K:
    raise EnvironmentError("TOP_K is not set in your config.py file.")

def _build_prompt(context_chunks: list[str], query: str) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    return (
        f"Context retrieved from the website:\n"
        f"{context}\n\n"
        f"---\n\n"
        f"User question: {query}\n\n"
    )

def query_rag(user_query: str, top_k: int = TOP_K, system_prompt: str = SYSTEM_PROMPT) -> str:
    results = query_store(user_query, top_k=top_k)
    context_docs = [r["document"] for r in results]
    prompt = _build_prompt(context_docs, user_query)

    response = client.models.generate_content(model = GEMINI_MODEL, contents = prompt, config = types.GenerateContentConfig(system_instruction=system_prompt))
    return response.text

def query_rag_verbose(user_query: str, top_k: int = TOP_K, system_prompt: str = SYSTEM_PROMPT, where: dict | None = None) -> dict:
    results = query_store(user_query, top_k=top_k, where=where)
    context_docs = [r["document"] for r in results]
    prompt = _build_prompt(context_docs, user_query)

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt, config=types.GenerateContentConfig(system_instruction=system_prompt))

    return {"query": user_query, "context": results, "prompt": prompt, "answer": response.text}