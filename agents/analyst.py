from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.schemas import CriticalAnalysis
from models.state import ResearchState
from prompts.analyst import CRITICAL_ANALYST_SYSTEM_PROMPT
from services.citations import CitationManager

def run_critical_analysis(state: ResearchState) -> dict:
    sources = state.get("web_sources", [])
    if not sources:
        return {"status_messages": ["Critical Analysis skipped: Empty evidence pool."]}

    indexed_sources = CitationManager.index_sources(sources)
    evidence = CitationManager.format_sources_for_prompt(indexed_sources)

    llm = create_llm(model_name=settings.OPENROUTER_MODEL_REASONING, temperature=0.1)
    structured_llm = llm.with_structured_output(CriticalAnalysis)

    try:
        analysis: CriticalAnalysis = structured_llm.invoke([
            SystemMessage(content=CRITICAL_ANALYST_SYSTEM_PROMPT),
            HumanMessage(content=f"Topic: '{state.get('topic')}'\n\nEvidence Context:\n{evidence}")
        ])
        return {
            "web_sources": indexed_sources,
            "critical_analysis": analysis.model_dump(),
            "status_messages": [
                f"Critical Analyst: Confirmed {len(analysis.confirmed_findings)} findings; "
                f"flagged {len(analysis.conflicting_findings)} contradictions."
            ]
        }
    except Exception as e:
        return {"errors": [f"Critical Analysis Agent failure: {str(e)}"]}