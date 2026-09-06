import time
from config import settings
from models.state import ResearchState
from tools.web_search import search_web_safe, clean_query_for_search

def run_technical_researcher(state: ResearchState) -> dict:
    topic_keywords = clean_query_for_search(state.get("topic", ""))
    queries = [
        f"{topic_keywords} architecture benchmarks latency",
        f"{topic_keywords} memory throughput evaluation"
    ]
    collected, errors = [], []
    for q in queries:
        docs, err = search_web_safe(q, max_results=settings.MAX_RESULTS_PER_QUERY)
        if err:
            errors.append(err)
        for doc in docs:
            d = doc.model_dump()
            d["agent_track"] = "Technical / Benchmarks"
            collected.append(d)

    return {
        "raw_web_sources": collected,
        "errors": errors,
        "status_messages": [f"Technical Worker: Gathered {len(collected)} benchmark sources."]
    }

def run_market_researcher(state: ResearchState) -> dict:
    time.sleep(0.8)  # Stagger worker launch
    topic_keywords = clean_query_for_search(state.get("topic", ""))
    queries = [
        f"{topic_keywords} enterprise deployment cost",
        f"{topic_keywords} production case studies"
    ]
    collected, errors = [], []
    for q in queries:
        docs, err = search_web_safe(q, max_results=settings.MAX_RESULTS_PER_QUERY)
        if err:
            errors.append(err)
        for doc in docs:
            d = doc.model_dump()
            d["agent_track"] = "Market / TCO"
            collected.append(d)

    return {
        "raw_web_sources": collected,
        "errors": errors,
        "status_messages": [f"Market Worker: Gathered {len(collected)} enterprise sources."]
    }

def run_counter_researcher(state: ResearchState) -> dict:
    time.sleep(1.6)  # Stagger worker launch
    topic_keywords = clean_query_for_search(state.get("topic", ""))
    queries = [
        f"{topic_keywords} limitations failure modes",
        f"{topic_keywords} challenges risks critique"
    ]
    collected, errors = [], []
    for q in queries:
        docs, err = search_web_safe(q, max_results=settings.MAX_RESULTS_PER_QUERY)
        if err:
            errors.append(err)
        for doc in docs:
            d = doc.model_dump()
            d["agent_track"] = "Adversarial / Counter-Evidence"
            collected.append(d)

    return {
        "raw_web_sources": collected,
        "errors": errors,
        "status_messages": [f"Counter Worker: Gathered {len(collected)} counter-evidence sources."]
    }