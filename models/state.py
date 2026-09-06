import operator
from typing import Annotated, TypedDict

class ResearchState(TypedDict):
    topic: str
    session_id: str
    research_plan: dict | None
    search_queries: list[str]
    raw_web_sources: Annotated[list[dict], operator.add]
    web_sources: list[dict]
    document_sources: list[dict]
    critical_analysis: dict | None
    fact_check: dict | None
    insights: dict | None
    final_report: str | None
    citation_audit: dict | None
    research_iteration: int
    status_messages: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]