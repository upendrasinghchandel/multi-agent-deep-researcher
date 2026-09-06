from urllib.parse import urlparse

HIGH_AUTHORITY_DOMAINS = {
    "arxiv.org", "github.com", "ieee.org", "acm.org", "nature.com",
    "science.org", "nist.gov", "huggingface.co", "mit.edu", "stanford.edu"
}

MEDIUM_AUTHORITY_DOMAINS = {
    "reuters.com", "bloomberg.com", "techcrunch.com", "theverge.com",
    "venturebeat.com", "zdnet.com", "wired.com", "infoworld.com"
}

def calculate_credibility_score(url: str, content: str) -> float:
    """Calculates Source Relevance Score (0.0 to 1.0) using domain trust and content depth."""
    domain = urlparse(url).netloc.replace("www.", "").lower()
    score = 0.45

    if any(auth in domain for auth in HIGH_AUTHORITY_DOMAINS):
        score = 0.95
    elif any(auth in domain for auth in MEDIUM_AUTHORITY_DOMAINS):
        score = 0.75

    words = len(content.split())
    if words > 250:
        score = min(1.0, score + 0.05)

    return round(score, 2)