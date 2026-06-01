import os
import re

from config import CHUNK_SIZE, CHUNK_OVERLAP, OBSIDIAN_SOURCE_TAG

if not CHUNK_SIZE:
    raise EnvironmentError("[!] CHUNK_SIZE is not set in config.py.")

if not CHUNK_OVERLAP:
    raise EnvironmentError("[!] CHUNK_OVERLAP is not set in config.py.")

def _strip_frontmatter(text: str) -> str:
    return re.sub(r"^\s*---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)

def _clean_markdown(text: str) -> str:
    text = _strip_frontmatter(text)

    # [[Note|alias]] → alias,  [[Note]] → Note
    text = re.sub(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]", r"\1", text)

    # Inline tags: #tag or #nested/tag (not heading #s)
    text = re.sub(r"(?<!\S)#[\w/\-]+", "", text)

    # Obsidian callouts: > [!note] / > [!warning] etc.
    text = re.sub(r">\s*\[!.*?\]\s*", "", text)

    # Embedded files: ![[image.png]]
    text = re.sub(r"!\[\[.*?\]\]", "", text)

    # Standard markdown images: ![alt](url)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # HTML comments: <!-- ... -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Collapse excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_vault(vault_path: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    if not os.path.isdir(vault_path):
        raise FileNotFoundError(f"[!] Vault path not found: {vault_path}")

    all_chunks: list[dict] = []
    note_count = 0

    for root, dirs, files in os.walk(vault_path):
        # Skip all hidden directories in-place so os.walk doesn't descend into them
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))

        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, vault_path)

            try:
                with open(fpath, encoding="utf-8") as f:
                    raw = f.read()
            except (UnicodeDecodeError, OSError) as exc:
                print(f"[!] Skipping {rel_path}: {exc}")
                continue

            cleaned = _clean_markdown(raw)
            if not cleaned:
                continue

            note_count += 1
            for chunk in _chunk_text(cleaned, chunk_size, overlap):
                all_chunks.append(
                    {
                        "text": chunk,
                        "file": rel_path,
                        "note": os.path.splitext(fname)[0],
                        "source": OBSIDIAN_SOURCE_TAG,
                    }
                )

    return all_chunks