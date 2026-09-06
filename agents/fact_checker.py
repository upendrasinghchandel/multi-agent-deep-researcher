from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.schemas import FactCheckResult
from models.state import ResearchState
from prompts.fact_checker import FACT_CHECKER_SYSTEM_PROMPT
from services.citations import CitationManager

def run_fact_checker(state: ResearchState) -> dict:
    sources = state.get("web_sources", [])
    if not sources:
        return {"status_messages": ["Fact Checker skipped: Missing evidence."]}

    evidence = CitationManager.format_sources_for_prompt(sources)
    llm = create_llm(model_name=settings.OPENROUTER_MODEL_REASONING, temperature=0.0)
    structured_llm = llm.with_structured_output(FactCheckResult)

    try:
        fact_check: FactCheckResult = structured_llm.invoke([
            SystemMessage(content=FACT_CHECKER_SYSTEM_PROMPT),
            HumanMessage(content=f"Topic: '{state.get('topic')}'\n\nEvidence Context:\n{evidence}")
        ])
        return {
            "fact_check": fact_check.model_dump(),
            "status_messages": [f"Fact Checker: Verified {len(fact_check.claims)} core claims against citations."]
        }
    except Exception as e:
        return {"errors": [f"Fact Checker failure: {str(e)}"]}