import os
import re
import time
import random
import httpx
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from duckduckgo_search import DDGS
from config import settings
from models.schemas import SourceDocument

CONVERSATIONAL_PREFIXES = re.compile(
    r"^(tell me about|what is|what are|explain|how does|give me|find info on|please provide|provide|notes for)\s+",
    re.IGNORECASE
)

def clean_query_for_search(query: str, max_words: int = 7) -> str:
    """Extracts core search keywords and drops conversational prefixes."""
    cleaned = CONVERSATIONAL_PREFIXES.sub("", query.strip())
    cleaned = re.sub(r"[^\w\s\-\.]", " ", cleaned)
    words = cleaned.split()
    return " ".join(words[:max_words])

def normalize_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))
    except Exception:
        return url.strip().rstrip("/")

def search_tavily(query: str, api_key: str, max_results: int = 5) -> list[SourceDocument]:
    """Uses Tavily search API (designed for AI agents; immune to DDG 202 blocks)."""
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": max_results, "search_depth": "basic"},
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            retrieved_at = datetime.now(timezone.utc).isoformat()
            docs = []
            for r in data.get("results", []):
                docs.append(SourceDocument(
                    title=r.get("title", "Web Source"),
                    url=normalize_url(r.get("url", "")),
                    source_name=urlparse(r.get("url", "")).netloc.replace("www.", "") or "Tavily Source",
                    content=r.get("content", "")[:settings.MAX_SOURCE_CONTENT_LENGTH],
                    retrieved_at=retrieved_at
                ))
            return docs
    except Exception:
        pass
    return []

def search_wikipedia_fallback(query: str, max_results: int = 3) -> list[SourceDocument]:
    """Safety net: retrieves public Wikipedia API summaries when all web search engines block the IP."""
    try:
        params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": max_results}
        resp = httpx.get("https://en.wikipedia.org/w/api.php", params=params, timeout=5.0)
        if resp.status_code == 200:
            results = resp.json().get("query", {}).get("search", [])
            retrieved_at = datetime.now(timezone.utc).isoformat()
            docs = []
            for r in results:
                title = r.get("title", "")
                snippet = re.sub(r"<.*?>", "", r.get("snippet", ""))
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                docs.append(SourceDocument(
                    title=f"Wikipedia: {title}",
                    url=url,
                    source_name="wikipedia.org",
                    content=snippet,
                    retrieved_at=retrieved_at
                ))
            return docs
    except Exception:
        pass
    return []

def search_web_safe(query: str, max_results: int = 5) -> tuple[list[SourceDocument], str | None]:
    """Three-tier search executor: Tavily -> DuckDuckGo Lite -> Wikipedia fallback."""
    refined_query = clean_query_for_search(query)
    
    # 1. Check for Tavily API key in settings
    if settings.TAVILY_API_KEY:
        docs = search_tavily(refined_query, settings.TAVILY_API_KEY, max_results=max_results)
        if docs:
            return docs, None

    # 2. DuckDuckGo with 'lite' backend (bypasses Cloudflare html 202 endpoints)
    try:
        time.sleep(random.uniform(0.5, 1.2))  # Jitter to avoid rapid-fire blocks
        results = DDGS().text(refined_query, max_results=max_results, backend="lite")
        if results:
            retrieved_at = datetime.now(timezone.utc).isoformat()
            docs = []
            for r in results:
                raw_url = r.get("href", "")
                if not raw_url:
                    continue
                docs.append(SourceDocument(
                    title=r.get("title", "Web Source"),
                    url=normalize_url(raw_url),
                    source_name=urlparse(raw_url).netloc.replace("www.", "") or "Web Source",
                    content=r.get("body", "")[:settings.MAX_SOURCE_CONTENT_LENGTH],
                    retrieved_at=retrieved_at
                ))
            return docs, None
    except Exception:
        pass

    # 3. Last-resort fallback so the demo never fails with 0 sources
    fallback_docs = search_wikipedia_fallback(refined_query, max_results=max_results)
    if fallback_docs:
        return fallback_docs, f"DuckDuckGo IP rate-limited; retrieved {len(fallback_docs)} fallback sources."

    return [], f"Search providers unavailable for '{refined_query}'. Please provide TAVILY_API_KEY."