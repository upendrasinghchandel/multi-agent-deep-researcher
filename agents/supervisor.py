from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.state import ResearchState
from prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT

class SupervisorDecision(BaseModel):
    is_sufficient: bool = Field(description="True if evidence is sufficient to report; False if critical gaps remain.")
    gap_summary: str = Field(description="Summary of identified gaps.")
    followup_queries: list[str] = Field(default_factory=list, description="Followup search queries.")

def run_supervisor(state: ResearchState) -> dict:
    current_iter = state.get("research_iteration", 0) + 1
    sources = state.get("web_sources", [])
    analysis = state.get("critical_analysis") or {}

    # Quality check: count high-authority domains
    high_value_sources = sum(1 for s in sources if s.get("credibility_score", 0.45) >= 0.75)

    if current_iter >= settings.MAX_RESEARCH_ITERATIONS or len(sources) < 2:
        return {
            "research_iteration": current_iter,
            "status_messages": [f"Supervisor: Iteration cap reached ({current_iter}/{settings.MAX_RESEARCH_ITERATIONS}). Routing to synthesis."]
        }

    llm = create_llm(model_name=settings.OPENROUTER_MODEL_FAST, temperature=0.0)
    structured_llm = llm.with_structured_output(SupervisorDecision)

    try:
        decision: SupervisorDecision = structured_llm.invoke([
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Topic: '{state.get('topic')}'\n"
                        f"High-Value Sources: {high_value_sources}\n"
                        f"Identified Gaps: {analysis.get('missing_information', [])}"
            )
        ])

        new_queries = state.get("search_queries", [])
        status_msg = f"Supervisor: Iteration {current_iter}. Evidence evaluated as sufficient."

        if not decision.is_sufficient and decision.followup_queries:
            new_queries = decision.followup_queries[:settings.MAX_SEARCH_QUERIES]
            status_msg = f"Supervisor: Identified gaps ({decision.gap_summary}). Triggering follow-up research with {len(new_queries)} queries."

        return {
            "research_iteration": current_iter,
            "search_queries": new_queries,
            "status_messages": [status_msg]
        }
    except Exception:
        return {
            "research_iteration": current_iter,
            "status_messages": [f"Supervisor: Proceeding forward from iteration {current_iter}."]
        }

def route_research(state: ResearchState) -> str:
    iteration = state.get("research_iteration", 0)
    status_str = " ".join(state.get("status_messages", []))
    if iteration < settings.MAX_RESEARCH_ITERATIONS and "Triggering follow-up research" in status_str:
        return "technical_researcher"
    return "insight_generator"