# RAG Security Analysis

This project builds a RAG system over the personal websites of the repository's contributors (and optionally a local Obsidian vault), then exploits it using the [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf).

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
python main.py --reindex [andrew|michaela]         # re-index web sources (Andrew's and/or Michaela's website)
python main.py --obsidian /path/to/vault           # index (or re-index) an Obsidian vault
python main.py --reindex --obsidian /path/to/vault # re-index web sources + vault together
```

This will:
1. Scrape [andrewzgheib.github.io](https://andrewzgheib.github.io) and/or [michaelaelrif.github.io](https://michaelaelrif.github.io)
2. Chunk the content
3. Embed with Gemini embeddings
4. Store in ChromaDB at `./chroma_db/`

The `--obsidian` flag will:
1. Recursively walks the vault for `.md` files
2. Strips YAML frontmatter, wikilinks `[[Note]]`, inline tags `#tag`, callouts, and embeds
3. Chunks the plain text using the same `CHUNK_SIZE` / `CHUNK_OVERLAP` settings as web sources
4. Stores chunks in ChromaDB under source tag `obsidian`

### RAG

```bash
python main.py                   # chat using all indexed sources
python main.py --filter andrew   # restrict to Andrew's website
python main.py --filter michaela # restrict to Michaela's website
python main.py --filter obsidian # restrict to Obsidian vault
```

### Exploits

```bash
python -m exploits.llm[0-10]_<exploit_name> # run an exploit module
```

## Notes

- The project assumes the use of Gemini for both LLM and embeddings, but the code is modular. You can swap out the LLM or embedding providers by modifying `config.py` and updating the relevant wrapper functions in `embeddings.py` and `rag.py`.
- [LLM10](./exploits/llm10_unbounded_consumption.py) runs in `DRY_RUN=True` mode by default to avoid burning API quota. Set `DRY_RUN=False` to execute live.