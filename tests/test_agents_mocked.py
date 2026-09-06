from unittest.mock import MagicMock, patch
from agents.planner import run_planner
from tools.web_search import search_web_safe
from models.schemas import ResearchPlan
from models.state import ResearchState

def test_planner_agent_mocked():
    mock_plan = ResearchPlan(
        topic="Small language models for RAG",
        objective="Assess SLM accuracy versus costs",
        research_questions=["What is the throughput difference?"],
        search_queries=["slm vs llm rag latency"],
        key_entities=["Phi-3", "Llama-3-8B"],
        required_evidence=["benchmarks"]
    )

    with patch("agents.planner.create_llm") as mock_create:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_plan
        mock_create.return_value = mock_instance

        mock_state: ResearchState = {
            "topic": "Small language models for RAG",
            "session_id": "test_session",
            "research_plan": None,
            "search_queries": [],
            "raw_web_sources": [],
            "web_sources": [],
            "document_sources": [],
            "critical_analysis": None,
            "fact_check": None,
            "insights": None,
            "final_report": None,
            "citation_audit": None,
            "research_iteration": 0,
            "status_messages": [],
            "errors": []
        }

        output = run_planner(mock_state)
        assert output["research_plan"]["objective"] == "Assess SLM accuracy versus costs"
        assert len(output["search_queries"]) == 1

def test_web_search_error_handling_mocked():
    with patch("tools.web_search.search_tavily") as mock_tavily, \
         patch("tools.web_search.DDGS") as mock_ddgs, \
         patch("tools.web_search.search_wikipedia_fallback") as mock_wiki:
        # Mock all search methods to return empty/fail
        mock_tavily.return_value = []
        mock_ddgs.return_value.text.side_effect = Exception("Rate limit reached")
        mock_wiki.return_value = []
        
        docs, err = search_web_safe("test query", max_results=3)
        assert len(docs) == 0
        assert err is not None
        assert "unavailable" in err.lower()