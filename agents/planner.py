from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.schemas import ResearchPlan
from models.state import ResearchState
from prompts.planner import PLANNER_SYSTEM_PROMPT

def run_planner(state: ResearchState) -> dict:
    topic = state.get("topic", "").strip()
    if not topic:
        return {"errors": ["Planner: Research topic is empty."]}

    llm = create_llm(model_name=settings.OPENROUTER_MODEL_FAST, temperature=0.0)
    structured_llm = llm.with_structured_output(ResearchPlan)

    try:
        plan: ResearchPlan = structured_llm.invoke([
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Deconstruct this research topic: '{topic}'")
        ])
        return {
            "research_plan": plan.model_dump(),
            "search_queries": plan.search_queries[:settings.MAX_SEARCH_QUERIES],
            "status_messages": [f"Planner: Strategy formulated with {len(plan.search_queries)} search queries."]
        }
    except Exception as e:
        return {"errors": [f"Planner Agent failure: {str(e)}"]}