import requests
from bs4 import BeautifulSoup
from config import TARGET_SITES, CHUNK_SIZE, CHUNK_OVERLAP

if not TARGET_SITES:
    raise EnvironmentError("[!] TARGET_SITES is empty in config.py.")

if not CHUNK_SIZE:
    raise EnvironmentError("[!] CHUNK_SIZE is not set in config.py.")

if not CHUNK_OVERLAP:
    raise EnvironmentError("[!] CHUNK_OVERLAP is not set in config.py.")

def _bs4_scrape(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "head"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks, step = [], max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def scrape_and_chunk(url: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    scraped = _bs4_scrape(url)
    chunks = _chunk_text(scraped, chunk_size, overlap)
    return chunks

def scrape_all_sites(sites: list[dict] = TARGET_SITES, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    results = []
    for site in sites:
        url = site["url"]
        source_tag = site["source_tag"]
        chunks = scrape_and_chunk(url, chunk_size, overlap)
        results.append({"source_tag": source_tag, "url": url, "chunks": chunks})
    return results

if __name__ == "__main__":
    all_sites = scrape_all_sites()