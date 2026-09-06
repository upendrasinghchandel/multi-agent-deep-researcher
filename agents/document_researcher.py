from models.state import ResearchState
from tools.vector_store import retrieve_session_context

def run_document_research(state: ResearchState) -> dict:
    """LangGraph node: Queries local isolated vector store for uploaded document evidence."""
    topic = state.get("topic", "")
    session_id = state.get("session_id", "default")
    existing = state.get("web_sources", [])

    doc_sources = retrieve_session_context(query=topic, session_id=session_id, top_k=4)
    if not doc_sources:
        return {"status_messages": ["Document Research: No uploaded session documents matched."]}

    return {
        "document_sources": doc_sources,
        "web_sources": existing + doc_sources,
        "status_messages": [f"Document Research: Extracted {len(doc_sources)} relevant chunks from upload store."]
    }