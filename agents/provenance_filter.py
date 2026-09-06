import hashlib
from models.state import ResearchState
from services.source_ranker import calculate_credibility_score

def run_provenance_filter(state: ResearchState) -> dict:
    """Fan-in node: Deduplicates across parallel streams and eliminates syndicated articles."""
    raw_sources = state.get("raw_web_sources", [])
    seen_urls = set()
    seen_hashes = set()
    deduped_sources: list[dict] = []

    for src in raw_sources:
        url = src.get("url", "").strip()
        content = src.get("content", "").strip()

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if url in seen_urls or content_hash in seen_hashes:
            continue

        seen_urls.add(url)
        seen_hashes.add(content_hash)
        
        src_copy = dict(src)
        src_copy["credibility_score"] = calculate_credibility_score(url, content)
        deduped_sources.append(src_copy)

    duplicates_dropped = len(raw_sources) - len(deduped_sources)
    return {
        "web_sources": deduped_sources,
        "status_messages": [
            f"Provenance Filter: Ingested {len(raw_sources)} raw sources. "
            f"Pruned {duplicates_dropped} duplicates; retained {len(deduped_sources)} independent records."
        ]
    }