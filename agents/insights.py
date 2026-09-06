import json
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.schemas import ResearchInsights
from models.state import ResearchState
from prompts.insights import INSIGHTS_SYSTEM_PROMPT

def _list_value(value) -> list:
    return value if isinstance(value, list) else []

def run_insight_generator(state: ResearchState) -> dict:
    analysis = state.get("critical_analysis") or {}
    fact_check = state.get("fact_check") or {}

    payload = {
        "topic": state.get("topic"),
        "confirmed": _list_value(analysis.get("confirmed_findings")),
        "contradictions": _list_value(analysis.get("conflicting_findings")),
        "verified_claims": _list_value(fact_check.get("claims"))
    }

    llm = create_llm(model_name=settings.OPENROUTER_MODEL_REASONING, temperature=0.2)
    structured_llm = llm.with_structured_output(ResearchInsights)

    try:
        insights: ResearchInsights = structured_llm.invoke([
            SystemMessage(content=INSIGHTS_SYSTEM_PROMPT),
            HumanMessage(content=f"Synthesize strategic insights from data:\n{json.dumps(payload, indent=2)}")
        ])
        return {
            "insights": insights.model_dump(),
            "status_messages": [
                f"Insight Generator: Extrapolated {len(insights.trends or [])} trends "
                f"and {len(insights.risks or [])} risks."
            ]
        }
    except Exception as e:
        return {"errors": [f"Insight Generator failure: {str(e)}"]}