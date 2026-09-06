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
    try:
        messages = [
            SystemMessage(content=FACT_CHECKER_SYSTEM_PROMPT),
            HumanMessage(content=f"Topic: '{state.get('topic')}'\n\nEvidence Context:\n{evidence}"),
        ]
        models = [settings.OPENROUTER_MODEL_REASONING]
        if settings.OPENROUTER_MODEL_FALLBACK not in models:
            models.append(settings.OPENROUTER_MODEL_FALLBACK)

        fact_check = None
        last_error = None
        for model_name in models:
            try:
                llm = create_llm(model_name=model_name, temperature=0.0)
                fact_check = llm.with_structured_output(FactCheckResult).invoke(messages)
                break
            except Exception as error:
                last_error = error

        if fact_check is None:
            raise last_error or RuntimeError("No fact-checking model was available.")

        return {
            "fact_check": fact_check.model_dump(),
            "status_messages": [f"Fact Checker: Verified {len(fact_check.claims or [])} core claims against citations."]
        }
    except Exception as e:
        return {"errors": [f"Fact Checker failure: {str(e)}"]}