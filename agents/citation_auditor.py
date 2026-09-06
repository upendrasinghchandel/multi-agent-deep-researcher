from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.schemas import CitationAuditResult
from models.state import ResearchState
from prompts.citation_auditor import AUDITOR_SYSTEM_PROMPT
from services.citations import CitationManager

def run_citation_auditor(state: ResearchState) -> dict:
    report = state.get("final_report", "")
    sources = state.get("web_sources", [])

    if not report or not sources:
        return {"status_messages": ["Citation Auditor skipped: Missing report or sources."]}

    evidence_text = CitationManager.format_sources_for_prompt(sources)
    llm = create_llm(model_name=settings.OPENROUTER_MODEL_REASONING, temperature=0.0)
    structured_llm = llm.with_structured_output(CitationAuditResult)

    try:
        audit_result: CitationAuditResult = structured_llm.invoke([
            SystemMessage(content=AUDITOR_SYSTEM_PROMPT),
            HumanMessage(content=f"Draft Report:\n{report}\n\nRegistered Sources:\n{evidence_text}")
        ])

        corrected_report = report
        for finding in audit_result.audit_findings:
            if finding.status != "verified":
                bad_tag = f"[{finding.citation_id}]"
                replacement_tag = f"~~{bad_tag}~~ *(citation rejected: unverified claim)*"
                corrected_report = corrected_report.replace(bad_tag, replacement_tag)

        status_msg = (
            f"Citation Auditor: Completed ({audit_result.citation_coverage_pct:.1f}% verified coverage). "
            f"Pruned {audit_result.rejection_count} unsupported citations."
        )

        return {
            "final_report": corrected_report,
            "citation_audit": audit_result.model_dump(),
            "status_messages": [status_msg]
        }
    except Exception as e:
        return {
            "errors": [f"Citation Auditor failure: {str(e)}"],
            "status_messages": ["Citation Auditor error; preserving original draft."]
        }