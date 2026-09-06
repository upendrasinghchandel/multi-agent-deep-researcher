import os
import uuid
from langchain_openai import OpenAIEmbeddings
from config import settings

try:
    import lancedb
    from langchain_community.vectorstores import LanceDB
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

DB_ROOT = os.path.join(os.getcwd(), "data", "lancedb")

def create_isolated_session_id() -> str:
    """Generates an isolated identifier for session vector tables."""
    return f"run_{uuid.uuid4().hex[:12]}"

def ingest_documents_isolated(docs: list, session_id: str):
    """Indexes documents in an isolated LanceDB table."""
    if not LANCEDB_AVAILABLE:
        return None, "LanceDB is not installed or available."
    if not docs:
        return None, "No document chunks provided for indexing."

    try:
        os.makedirs(DB_ROOT, exist_ok=True)
        db = lancedb.connect(DB_ROOT)
        embeddings = OpenAIEmbeddings(
            model=settings.OPENROUTER_EMBEDDING_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        vectorstore = LanceDB.from_documents(docs, embeddings, connection=db, table_name=session_id)
        return vectorstore, None
    except Exception as e:
        return None, f"LanceDB ingestion failed: {str(e)}"

def retrieve_session_context(query: str, session_id: str, top_k: int = 4) -> list[dict]:
    """Retrieves context specifically from the active session's table."""
    if not LANCEDB_AVAILABLE:
        return []
    try:
        db = lancedb.connect(DB_ROOT)
        if session_id not in db.table_names():
            return []
        embeddings = OpenAIEmbeddings(
            model=settings.OPENROUTER_EMBEDDING_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        table = db.open_table(session_id)
        vectorstore = LanceDB(table=table, embedding=embeddings)
        results = vectorstore.similarity_search(query, k=top_k)

        return [
            {
                "citation_id": f"DOC{idx}",
                "title": doc.metadata.get("source_file", "Uploaded File"),
                "url": "local-session-document",
                "content": doc.page_content,
                "source_name": "User Upload"
            }
            for idx, doc in enumerate(results, 1)
        ]
    except Exception:
        return []

def purge_session_table(session_id: str) -> None:
    """Drops the session table to prevent data leakage between runs."""
    if not LANCEDB_AVAILABLE:
        return
    try:
        db = lancedb.connect(DB_ROOT)
        if session_id in db.table_names():
            db.drop_table(session_id)
    except Exception:
        pass