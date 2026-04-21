import sys
from scraper import scrape_all_sites, scrape_and_chunk
from vectorstore import ingest_chunks, collection_count, delete_by_source
from config import TARGET_SITES

if not TARGET_SITES:
    raise EnvironmentError("[!] TARGET_SITES is empty in config.py.")

def _show_banner(site_filter: str | None):
    if site_filter:
        print(f"> RAG filtered to: [{site_filter}]")
    else:
        print("> RAG filtered to andrewzgheib.github.io and michaelaelrif.github.io")

def _build_one_website(tag: str):
    site = next((s for s in TARGET_SITES if s["source_tag"] == tag), None)
    if not site:
        print(f"[!] Unknown source tag '{tag}'.\nAvailable source tags are: {[s['source_tag'] for s in TARGET_SITES]}")
        sys.exit(1)

    delete_by_source(tag)
    chunks = scrape_and_chunk(site["url"])
    ingest_chunks(chunks, source=tag)

def _build_all_websites():
    sites = scrape_all_sites()
    for site in sites:
        ingest_chunks(site["chunks"], source=site["source_tag"])

def _rag(site_filter: str | None):
    _show_banner(site_filter)

    where = {"source": site_filter} if site_filter else None # Build where-filter for ChromaDB if a site filter is active

    while True:
        try:
            query = input("\nPrompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query:
            continue
        if query == "--help":
            print("  Ask anything about the indexed websites.\n"
                  "  --reindex: rebuild the full index\n"
                  "  --filter <tag>: restrict answers to one site\n")
            continue

        try:
            from rag import query_rag_verbose
            result = query_rag_verbose(query, where=where) if where else query_rag_verbose(query)
            print(f"\nAssistant: {result['answer']}\n")
        except Exception as exc:
            print(f"[!] Error: {exc}\n")

def main():
    args = sys.argv[1:]

    site_filter = None
    if "--filter" in args:
        idx = args.index("--filter")
        if idx + 1 < len(args):
            site_filter = args[idx + 1]
        else:
            print("[!] --filter requires a source tag")
            sys.exit(1)

    if "--reindex" in args:
        idx = args.index("--reindex")
        tag = args[idx + 1] if idx + 1 < len(args) and not args[idx + 1].startswith("--") else None
        if tag:
            _build_one_website(tag)
        else:
            _build_all_websites()
    elif collection_count() == 0:
        _build_all_websites()

    _rag(site_filter)

if __name__ == "__main__":
    main()