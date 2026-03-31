import httpx
from bs4 import BeautifulSoup
import time

def scrape_gfg_article(url: str) -> dict:
    headers = {"User-Agent": "debug-buddy/1.0 (educational tool)"}
    resp = httpx.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="article--viewer__content")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
    
    return {
        "title": title,
        "content": content_div.get_text(separator="\n", strip=True) if content_div else "",
        "url": url
    }

def scrape_gfg_batch(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        results.append(scrape_gfg_article(url))
        time.sleep(2) 
    return results