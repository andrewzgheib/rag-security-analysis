# RAG Security Analysis

This project builds a RAG system over the personal websites of the repository's contributors, then exploits it using the [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf).

Submitted in partial fulfillment for the AI & Cybersecurity course at [Saint Joseph University of Beirut](https://www.usj.edu.lb?lang=2).

## Usage

### Environment

```bash
# Clone the repo
git clone https://github.com/andrewzgheib/rag-security-analysis.git
cd rag-security-analysis

# Setup python environment
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env # Edit .env to include your Gemini API key
```

Get your API key from:
- Gemini: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Index

```bash
python main.py --reindex [andrew|michaela]
```

This will:
1. Scrape [andrewzgheib.github.io](https://andrewzgheib.github.io) and/or [michaelaelrif.github.io](https://michaelaelrif.github.io)
2. Chunk the content
3. Embed with Gemini embeddings
4. Store in ChromaDB at `./chroma_db/`

### RAG

```bash
python main.py                   # Chat using both sites (auto-builds if empty)
python main.py --filter andrew   # Chat restricted to Andrew's content only
python main.py --filter michaela # Chat restricted to Michaela's content only
```

### Exploits

```bash
python -m exploits.llm[0-10]_<exploit_name>                 # Run a single exploit module directly
```

## Notes

- The project assumes the use of Gemini for both LLM and embeddings, but the code is modular. You can swap out the LLM or embedding providers by modifying `config.py` and updating the relevant wrapper functions in `embeddings.py` and `rag.py`.
- [LLM10](./exploits/llm10_unbounded_consumption.py) runs in `DRY_RUN=True` mode by default to avoid burning API quota. Set `DRY_RUN=False` to execute live.