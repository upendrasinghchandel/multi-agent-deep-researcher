import json
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

from config import settings
from graph import build_research_graph
from models.llm import validate_openrouter_credentials
from models.state import ResearchState
from tools.document_loader import load_and_chunk_document
from tools.upload_validator import validate_uploaded_file
from tools.vector_store import (
    create_isolated_session_id,
    ingest_documents_isolated,
    purge_session_table
)

st.set_page_config(
    page_title="Multi-Agent AI Deep Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)
###
# Sidebar Configuration
with st.sidebar:
    st.header("Runtime Controls")
    
    # Model Routing Display
    st.subheader("Model Routing")
    st.text_input("Planner / Supervisor", value=settings.OPENROUTER_MODEL_FAST, disabled=True)
    st.text_input("Analyst / Reasoner", value=settings.OPENROUTER_MODEL_REASONING, disabled=True)
    st.text_input("Executive Writer", value=settings.OPENROUTER_MODEL_WRITER, disabled=True)

    st.markdown("---")
    
    # Execution Safeguards
    st.subheader("Execution Safeguards")
    settings.MAX_RESEARCH_ITERATIONS = st.slider(
        "Max Iterations", 
        min_value=1, 
        max_value=3, 
        value=settings.MAX_RESEARCH_ITERATIONS
    )
    settings.MAX_SEARCH_QUERIES = st.slider(
        "Max Queries", 
        min_value=2, 
        max_value=8, 
        value=settings.MAX_SEARCH_QUERIES
    )
    settings.MAX_RESULTS_PER_QUERY = st.slider(
        "Results per Query", 
        min_value=2, 
        max_value=8, 
        value=settings.MAX_RESULTS_PER_QUERY
    )

    st.markdown("---")
    
    # Session Management
    if st.button("Reset Session & Clear Embeddings", use_container_width=True):
        purge_session_table(st.session_state["active_session_id"])
        st.session_state["active_session_id"] = create_isolated_session_id()
        st.session_state.pop("completed_research", None)
        st.rerun()

###
# Session State Initialization
if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = create_isolated_session_id()
if "cancel_requested" not in st.session_state:
    st.session_state["cancel_requested"] = False

# Sidebar Configuration
with st.sidebar:
    pass

st.title("🔬 Multi-Agent AI Deep Researcher")
st.caption("Autonomous multi-source research powered by LangGraph + OpenRouter")

# Research Input Form
with st.form("research_form"):
    topic = st.text_area(
        "Research Topic",
        placeholder="e.g., Can small language models replace large language models for enterprise RAG applications?",
        height=90
    )
    uploaded_files = st.file_uploader(
        "Optional Reference Documents (PDF, DOCX, TXT, MD - Max 10MB)",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md"]
    )
    col_run, col_cancel = st.columns([5, 1])
    with col_run:
        submitted = st.form_submit_button("Start Deep Research", type="primary", use_container_width=True)
    with col_cancel:
        cancel_pressed = st.form_submit_button("Cancel", use_container_width=True)

if cancel_pressed:
    st.session_state["cancel_requested"] = True
    st.warning("Cancellation requested. Halting pipeline execution.")

if submitted:
    st.session_state["cancel_requested"] = False

    # Pre-flight credential check
    valid_key, msg = validate_openrouter_credentials(settings.OPENROUTER_API_KEY)
    if not valid_key:
        st.error(f"Pre-flight authentication failed: {msg}")
        st.stop()

    if not topic.strip():
        st.warning("Please enter a research topic to proceed.")
        st.stop()

    session_id = st.session_state["active_session_id"]
    st_errors = []

    # Process Document Uploads
    if uploaded_files:
        seen_names = set()
        all_chunks = []
        for file in uploaded_files:
            if file.name in seen_names:
                st_errors.append(f"Duplicate upload ignored: '{file.name}'.")
                continue
            seen_names.add(file.name)

            valid_file, err_file = validate_uploaded_file(file)
            if not valid_file:
                st_errors.append(err_file)
                continue

            save_dir = os.path.join("data", "uploads", session_id)
            os.makedirs(save_dir, exist_ok=True)
            target_path = os.path.join(save_dir, file.name)
            with open(target_path, "wb") as f:
                f.write(file.getbuffer())

            chunks = load_and_chunk_document(target_path)
            all_chunks.extend(chunks)

        if all_chunks:
            _, index_err = ingest_documents_isolated(all_chunks, session_id)
            if index_err:
                st_errors.append(index_err)

    # State Container Initialization
    current_state: ResearchState = {
        "topic": topic.strip(),
        "session_id": session_id,
        "research_plan": None,
        "search_queries": [],
        "raw_web_sources": [],
        "web_sources": [],
        "document_sources": [],
        "critical_analysis": None,
        "fact_check": None,
        "insights": None,
        "final_report": None,
        "citation_audit": None,
        "research_iteration": 0,
        "status_messages": [],
        "errors": st_errors
    }

    graph = build_research_graph()

    # Visual Multi-Agent Streaming
    with st.status("Executing Multi-Agent Deep Research...", expanded=True) as status_box:
        for update in graph.stream(current_state, stream_mode="updates"):
            if st.session_state.get("cancel_requested", False):
                status_box.update(label="Job Halted by User Request.", state="error")
                current_state["errors"].append("Execution aborted: User clicked Cancel.")
                break

            for node_name, output in update.items():
                for k, v in output.items():
                    if k in current_state and isinstance(current_state[k], list) and isinstance(v, list):
                        current_state[k] = current_state[k] + v
                    else:
                        current_state[k] = v

                last_msg = output.get("status_messages", [""])[-1]
                if node_name == "planner":
                    status_box.write(f"✓ **Planner**: {last_msg}")
                elif node_name == "technical_researcher":
                    status_box.write(f"⚙️ **Technical Worker**: {last_msg}")
                elif node_name == "market_researcher":
                    status_box.write(f"📊 **Market Worker**: {last_msg}")
                elif node_name == "counter_researcher":
                    status_box.write(f"🛡️ **Counter Worker**: {last_msg}")
                elif node_name == "provenance_filter":
                    status_box.write(f"🔗 **Provenance Filter**: {last_msg}")
                elif node_name == "document_research":
                    status_box.write(f"✓ **Document Research**: {last_msg}")
                elif node_name == "critical_analysis":
                    status_box.write(f"✓ **Critical Analyst**: {last_msg}")
                elif node_name == "fact_checker":
                    status_box.write(f"✓ **Fact Checker**: {last_msg}")
                elif node_name == "supervisor":
                    status_box.write(f"⚖️ **Supervisor**: {last_msg}")
                elif node_name == "insight_generator":
                    status_box.write(f"✓ **Insight Generator**: {last_msg}")
                elif node_name == "report_builder":
                    status_box.write(f"✓ **Report Builder**: Markdown briefing assembled.")
                elif node_name == "citation_auditor":
                    status_box.write(f"🛡️ **Citation Auditor**: {last_msg}")

        if not st.session_state.get("cancel_requested"):
            status_box.update(label="Research Execution Complete!", state="complete", expanded=False)

    st.session_state["completed_research"] = current_state

# Results View
if "completed_research" in st.session_state:
    data: ResearchState = st.session_state["completed_research"]
    sources = data.get("web_sources") or []
    analysis = data.get("critical_analysis") or {}
    fact_check = data.get("fact_check") or {}
    insights = data.get("insights") or {}
    report = data.get("final_report") or ""
    audit_data = data.get("citation_audit") or {}
    errors = data.get("errors") or []
    coverage = audit_data.get("citation_coverage_pct", 100.0)

    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Sources Examined", len(sources))
    m2.metric("Claims Verified", len(fact_check.get("claims", [])))
    m3.metric("Contradictions", len(analysis.get("conflicting_findings", [])))
    m4.metric("Citation Coverage", f"{coverage:.1f}%")
    m5.metric("Iterations Run", data.get("research_iteration", 1))

    tab_report, tab_sources, tab_analysis, tab_errors = st.tabs([
        "📄 Final Report",
        "🌐 Sources & Evidence",
        "🧠 Agent Analysis",
        f"⚠️ Pipeline Errors ({len(errors)})"
    ])

    with tab_report:
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            st.download_button("📥 Download Report (.md)", data=report, file_name="report.md", mime="text/markdown", use_container_width=True)
        with c2:
            st.download_button("📥 Download State (.json)", data=json.dumps(data, indent=2), file_name="state.json", mime="application/json", use_container_width=True)

        if audit_data:
            with st.expander("🛡️ Citation Audit Log", expanded=False):
                st.write(f"**Coverage:** {coverage:.1f}% | **Rejected:** {audit_data.get('rejection_count', 0)}")
                for f in audit_data.get("audit_findings", []):
                    badge = "green" if f["status"] == "verified" else "red"
                    st.markdown(f"- :{badge}[● {f['status'].upper()}] `[{f['citation_id']}]`: {f['target_sentence']}")
                    st.caption(f"Reasoning: {f['reasoning']}")

        st.markdown("---")
        st.markdown(report)

    with tab_sources:
        if sources:
            rows = [
                {
                    "Citation": s.get("citation_id", "N/A"),
                    "Title": s.get("title", "Untitled"),
                    "Track": s.get("agent_track", "Web"),
                    "Credibility": s.get("credibility_score", 0.45),
                    "URL": s.get("url", "")
                }
                for s in sources
            ]
            st.dataframe(rows, use_container_width=True)
            with st.expander("Inspect Raw Evidence Text"):
                for s in sources:
                    st.write(f"**[{s.get('citation_id')}] {s.get('title')}** ({s.get('url')})")
                    st.caption(s.get("content", ""))
                    st.divider()
        else:
            st.info("No sources retained.")

    with tab_analysis:
        ca1, ca2 = st.columns(2)
        with ca1:
            st.subheader("Critical Analysis")
            st.markdown("**Confirmed Findings:**")
            for item in analysis.get("confirmed_findings", []):
                st.markdown(f"- {item}")
            st.markdown("**Disputed Findings:**")
            for item in analysis.get("conflicting_findings", []):
                st.markdown(f"- :red[{item}]")
            st.markdown("**Missing Information:**")
            for item in analysis.get("missing_information", []):
                st.markdown(f"- :orange[{item}]")

        with ca2:
            st.subheader("Verified Claims")
            for claim in fact_check.get("claims", []):
                st_val = claim.get("status", "").lower()
                badge = "green" if st_val == "supported" else "orange" if "partially" in st_val else "red"
                with st.expander(f":{badge}[● {st_val.upper()}] {claim.get('claim')}"):
                    st.write(f"**Confidence:** {claim.get('confidence', 0.0) * 100:.1f}%")
                    st.write(f"**Supporting:** {', '.join(claim.get('supporting_sources', [])) or 'None'}")
                    st.write(f"**Conflicting:** {', '.join(claim.get('conflicting_sources', [])) or 'None'}")
                    st.write(f"**Reasoning:** {claim.get('reasoning_summary')}")

        st.markdown("---")
        ci1, ci2 = st.columns(2)
        with ci1:
            st.markdown("**Trends & Patterns:**")
            for item in insights.get("trends", []) + insights.get("patterns", []):
                st.markdown(f"- {item}")
        with ci2:
            st.markdown("**Risks & Opportunities:**")
            for item in insights.get("risks", []):
                st.markdown(f"- ⚠️ **Risk:** {item}")
            for item in insights.get("opportunities", []):
                st.markdown(f"- 💡 **Opportunity:** {item}")

    with tab_errors:
        if errors:
            for err in errors:
                st.error(f"• {err}")
        else:
            st.success("Execution completed with 0 errors.")