import json
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from models.llm import create_llm
from models.state import ResearchState
from prompts.report_writer import REPORT_WRITER_SYSTEM_PROMPT
from services.citations import CitationManager

def run_report_builder(state: ResearchState) -> dict:
    sources = state.get("web_sources", [])
    payload = {
        "topic": state.get("topic"),
        "research_plan": state.get("research_plan"),
        "critical_analysis": state.get("critical_analysis"),
        "fact_check": state.get("fact_check"),
        "insights": state.get("insights"),
        "sources": [{"id": s.get("citation_id"), "title": s.get("title"), "url": s.get("url")} for s in sources]
    }

    llm = create_llm(model_name=settings.OPENROUTER_MODEL_WRITER, temperature=0.2)

    try:
        response = llm.invoke([
            SystemMessage(content=REPORT_WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"Draft formal research report from this state:\n{json.dumps(payload, indent=2)}")
        ])
        content = response.content
        if "## Sources" not in content:
            content += "\n\n" + CitationManager.generate_sources_section(sources)

        return {
            "final_report": content,
            "status_messages": ["Report Builder: Executive Markdown briefing successfully compiled."]
        }
    except Exception as e:
        return {"errors": [f"Report Builder failure: {str(e)}"]}