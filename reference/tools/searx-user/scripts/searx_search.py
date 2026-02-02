#!/usr/bin/env python3
"""SearXNG Search Script for Codex Skill"""
import requests
from bs4 import BeautifulSoup
import json
import sys

def search(query, max_results=10, lang="en"):
    """Search using SearXNG and return structured results"""
    engine = "http://127.0.0.1:8888"
    params = {"q": query, "language": lang, "safesearch": 1}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(f"{engine}/search", params=params, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.find_all("article", class_="result")
        
        output = []
        for result in results[:max_results]:
            h3 = result.find("h3")
            if h3:
                link = h3.find("a")
                if link:
                    output.append({
                        "title": link.text.strip(),
                        "url": link.get("href", "")
                    })
        return output
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    results = search(query, 5, "en")
    print(json.dumps(results, ensure_ascii=False, indent=2))
