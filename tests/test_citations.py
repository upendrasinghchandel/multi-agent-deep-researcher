import pytest
from unittest.mock import MagicMock, patch
from services.citations import CitationManager
from agents.citation_auditor import run_citation_auditor
from models.state import ResearchState
from models.schemas import CitationAuditResult, AuditFinding

def test_citation_manager_deduplication_and_indexing():
    mock_sources = [
        {"title": "SLM Benchmark 2026", "url": "https://example.com/slm", "content": "Phi-3 outperforms Llama-2."},
        {"title": "Enterprise RAG Costs", "url": "https://example.com/costs", "content": "Self-hosting cuts cost by 60%."},
    ]

    indexed = CitationManager.index_sources(mock_sources)
    assert len(indexed) == 2
    assert indexed[0]["citation_id"] == "S1"
    assert indexed[1]["citation_id"] == "S2"

    references_section = CitationManager.generate_sources_section(indexed)
    assert "- [S1] **SLM Benchmark 2026** — https://example.com/slm" in references_section
    assert "- [S2] **Enterprise RAG Costs** — https://example.com/costs" in references_section

def test_citation_auditor_flags_unsupported_claims():
    mock_sources = [
        {
            "citation_id": "S1",
            "title": "Empirical SLM Benchmarks",
            "url": "https://example.com/benchmarks",
            "content": "In our benchmarks, 8B models achieved 88% accuracy on single-hop retrieval datasets."
        },
        {
            "citation_id": "S2",
            "title": "Hardware Memory Limits",
            "url": "https://example.com/hardware",
            "content": "Quantized 8B models require at least 6GB of VRAM to execute inference."
        }
    ]

    mock_draft = """# Research Report

## Key Findings
- Small models reach 88% retrieval accuracy on single-hop queries [S1].
- Quantized 8B models can run effortlessly on 256MB of RAM with zero latency [S2].

## Sources
- [S1] **Empirical SLM Benchmarks** — https://example.com/benchmarks
- [S2] **Hardware Memory Limits** — https://example.com/hardware
"""

    mock_state: ResearchState = {
        "topic": "SLM RAG performance",
        "session_id": "test_session",
        "research_plan": None,
        "search_queries": [],
        "raw_web_sources": [],
        "web_sources": mock_sources,
        "document_sources": [],
        "critical_analysis": None,
        "fact_check": None,
        "insights": None,
        "final_report": mock_draft,
        "citation_audit": None,
        "research_iteration": 1,
        "status_messages": [],
        "errors": []
    }

    # Mock the LLM to return citation audit findings
    mock_audit_result = CitationAuditResult(
        audit_findings=[
            AuditFinding(
                citation_id="S1",
                target_sentence="Small models reach 88% retrieval accuracy on single-hop queries [S1].",
                status="verified",
                reasoning="Source explicitly mentions '88% accuracy on single-hop retrieval datasets.'"
            ),
            AuditFinding(
                citation_id="S2",
                target_sentence="Quantized 8B models can run effortlessly on 256MB of RAM with zero latency [S2].",
                status="rejected_unsupported",
                reasoning="Source states '6GB of VRAM', not 256MB. Claim is not supported."
            )
        ],
        rejection_count=1,
        citation_coverage_pct=50.0
    )

    with patch("agents.citation_auditor.create_llm") as mock_create:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_audit_result
        mock_create.return_value = mock_instance

        result = run_citation_auditor(mock_state)
        audit = result.get("citation_audit")
        corrected_report = result.get("final_report")

        assert audit is not None
        assert audit["rejection_count"] >= 1
        assert "~~[S2]~~ *(citation rejected: unverified claim)*" in corrected_report
        assert "[S1]" in corrected_report