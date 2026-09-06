from langgraph.graph import StateGraph, START, END
from models.state import ResearchState
from agents.planner import run_planner
from agents.parallel_researchers import (
    run_technical_researcher,
    run_market_researcher,
    run_counter_researcher,
)
from agents.provenance_filter import run_provenance_filter
from agents.document_researcher import run_document_research
from agents.analyst import run_critical_analysis
from agents.fact_checker import run_fact_checker
from agents.supervisor import run_supervisor, route_research
from agents.insights import run_insight_generator
from agents.report_writer import run_report_builder
from agents.citation_auditor import run_citation_auditor

def build_research_graph():
    """Builds and compiles the parallelized, reliable deep research StateGraph."""
    workflow = StateGraph(ResearchState)

    # Register Nodes
    workflow.add_node("planner", run_planner)
    workflow.add_node("technical_researcher", run_technical_researcher)
    workflow.add_node("market_researcher", run_market_researcher)
    workflow.add_node("counter_researcher", run_counter_researcher)
    workflow.add_node("provenance_filter", run_provenance_filter)
    workflow.add_node("document_research", run_document_research)
    workflow.add_node("analyze", run_critical_analysis)
    workflow.add_node("fact_checker", run_fact_checker)
    workflow.add_node("supervisor", run_supervisor)
    workflow.add_node("insight_generator", run_insight_generator)
    workflow.add_node("report_builder", run_report_builder)
    workflow.add_node("citation_auditor", run_citation_auditor)

    # Parallel Fan-Out from Planner
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "technical_researcher")
    workflow.add_edge("planner", "market_researcher")
    workflow.add_edge("planner", "counter_researcher")

    # Fan-In into Provenance Filter
    workflow.add_edge("technical_researcher", "provenance_filter")
    workflow.add_edge("market_researcher", "provenance_filter")
    workflow.add_edge("counter_researcher", "provenance_filter")

    # Synthesis Pipeline
    workflow.add_edge("provenance_filter", "document_research")
    workflow.add_edge("document_research", "analyze")
    workflow.add_edge("analyze", "fact_checker")
    workflow.add_edge("fact_checker", "supervisor")

    # Conditional Gap-Closure Routing
    workflow.add_conditional_edges(
        "supervisor",
        route_research,
        {
            "technical_researcher": "technical_researcher",
            "insight_generator": "insight_generator"
        }
    )

    workflow.add_edge("insight_generator", "report_builder")
    workflow.add_edge("report_builder", "citation_auditor")
    workflow.add_edge("citation_auditor", END)

    return workflow.compile()

research_graph = build_research_graph()