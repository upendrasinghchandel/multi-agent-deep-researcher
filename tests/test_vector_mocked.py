from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from tools.vector_store import ingest_documents_isolated

def test_isolated_document_indexing():
    mock_docs = [Document(page_content="Mock enterprise RAG content", metadata={"source_file": "doc1.txt"})]
    session_id = "run_test_abc123"

    with patch("lancedb.connect") as mock_lancedb, patch("tools.vector_store.OpenAIEmbeddings"):
        mock_db = MagicMock()
        mock_lancedb.return_value = mock_db

        with patch("langchain_community.vectorstores.LanceDB.from_documents") as mock_from_docs:
            mock_from_docs.return_value = MagicMock()
            store, err = ingest_documents_isolated(mock_docs, session_id)
            assert err is None
            assert store is not None
            mock_from_docs.assert_called_once()