import sys
from scraper import scrape_all_sites, scrape_and_chunk
from vectorstore import ingest_chunks, collection_count, delete_by_source
from config import TARGET_SITES

if not TARGET_SITES:
    raise EnvironmentError("[!] TARGET_SITES is empty in config.py.")

def _show_banner(site_filter: str | None, obsidian_path: str | None = None):
    if site_filter:
        print(f"> RAG filtered to: [{site_filter}]")
    else:
        sources = ["andrewzgheib.github.io", "michaelaelrif.github.io"]
        if obsidian_path:
            sources.append(f"obsidian vault ({obsidian_path})")
        print(f"> RAG sources: {', '.join(sources)}")

def _build_one_website(tag: str):
    site = next((s for s in TARGET_SITES if s["source_tag"] == tag), None)
    if not site:
        print(
            f"[!] Unknown source tag '{tag}'.\n"
            f"Available source tags: {[s['source_tag'] for s in TARGET_SITES]}"
        )
        sys.exit(1)
    delete_by_source(tag)
    chunks = scrape_and_chunk(site["url"])
    ingest_chunks(chunks, source=tag)

def _build_all_websites():
    sites = scrape_all_sites()
    for site in sites:
        ingest_chunks(site["chunks"], source=site["source_tag"])

def _build_obsidian(vault_path: str):
    from obsidian import load_vault, OBSIDIAN_SOURCE_TAG
    from vectorstore import ingest_vault_chunks

    delete_by_source(OBSIDIAN_SOURCE_TAG)
    chunks = load_vault(vault_path)
    if not chunks:
        print("[!] No markdown files found in vault. Nothing was indexed.")
        return
    ingest_vault_chunks(chunks)

def _rag(site_filter: str | None, obsidian_path: str | None = None):
    _show_banner(site_filter, obsidian_path)

    # Build ChromaDB where-filter when a single source is requested
    where = {"source": site_filter} if site_filter else None

    while True:
        try:
            query = input("\nPrompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query:
            continue

        if query == "--help":
            print(
                "  Ask anything about the indexed sources.\n"
                "  --reindex [tag]              rebuild web index (optional tag: andrew|michaela)\n"
                "  --filter <tag>               restrict answers to one source\n"
                "  --obsidian <vault_path>      index a local Obsidian vault\n"
                "  --reindex obsidian           re-index (requires --obsidian <path>)\n"
            )
            continue

        try:
            from rag import query_rag_verbose
            result = query_rag_verbose(query, where=where) if where else query_rag_verbose(query)
            print(f"\nAssistant: {result['answer']}\n")
        except Exception as exc:
            print(f"[!] Error: {exc}\n")

def _parse_flag(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    idx = args.index(flag)
    if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
        return args[idx + 1]
    return None

def main():
    args = sys.argv[1:]

    obsidian_path = _parse_flag(args, "--obsidian")
    if "--obsidian" in args and not obsidian_path:
        print("[!] --obsidian requires a vault path")
        sys.exit(1)

    site_filter = _parse_flag(args, "--filter")
    if "--filter" in args and not site_filter:
        print("[!] --filter requires a source tag")
        sys.exit(1)

    if "--reindex" in args:
        tag = _parse_flag(args, "--reindex")

        if tag == "obsidian":
            # python main.py --reindex obsidian --obsidian <path>
            if not obsidian_path:
                print("[!] --reindex obsidian requires --obsidian <vault_path>")
                sys.exit(1)
            _build_obsidian(obsidian_path)

        elif tag:
            # python main.py --reindex andrew|michaela [--obsidian <path>]
            _build_one_website(tag)
            if obsidian_path:
                _build_obsidian(obsidian_path)

        else:
            # python main.py --reindex [--obsidian <path>]
            _build_all_websites()
            if obsidian_path:
                _build_obsidian(obsidian_path)

    elif obsidian_path:
        # always (re)index the vault then chat
        _build_obsidian(obsidian_path)

    elif collection_count() == 0:
        _build_all_websites()

    _rag(site_filter, obsidian_path)

if __name__ == "__main__":
    main()