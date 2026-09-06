# 🔬 Multi-Agent AI Deep Researcher

A sophisticated multi-agent research system powered by **LangGraph**, **OpenRouter API**, and **Streamlit**. Autonomously conducts deep research on any topic by orchestrating specialized agents across planning, search, analysis, fact-checking, and reporting phases.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **Multi-Agent Orchestration**: Parallelized research agents working in coordinated workflows
- **LangGraph State Management**: Robust state tracking across research iterations
- **Advanced Search Capabilities**: Multi-tier search (Tavily API → DuckDuckGo → Wikipedia fallback)
- **Document Analysis**: Support for PDF, DOCX, TXT, and Markdown uploads
- **Citation Audit**: Automatic verification of claims against sources
- **Fact Checking**: Cross-source validation of research findings
- **Conflict Detection**: Identifies and flags contradictory information
- **Iterative Refinement**: Automatic gap-closure through supervisor-guided re-search
- **Vector Embeddings**: Isolated session-based document indexing with LanceDB
- **Professional Reports**: Structured markdown output with verified citations

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Agent Framework** | LangGraph (StateGraph, conditional routing) |
| **LLM API** | OpenRouter (supports Llama, DeepSeek, etc.) |
| **Web Search** | Tavily API + DuckDuckGo |
| **Vector DB** | LanceDB (in-process) |
| **UI Framework** | Streamlit |
| **Document Processing** | LangChain's document loaders |
| **Testing** | pytest, unittest.mock |
| **Language** | Python 3.12+ |

---

## 📦 Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/))
- **Git** ([Download](https://git-scm.com/))
- **API Keys**:
  - OpenRouter API Key (sign up at [openrouter.ai](https://openrouter.ai))
  - Tavily API Key (sign up at [tavily.com](https://tavily.com)) - *optional, falls back to DuckDuckGo*

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/upendrasinghchandel/multi-agent-deep-researcher.git
cd multi-agent-deep-researcher
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example` if available):

```env
# OpenRouter API Authentication (required)
OPENROUTER_API_KEY=sk-or-v1-your_key_here

# Tavily API Authentication (optional, but recommended)
TAVILY_API_KEY=tvly-dev-your_key_here

# Workload Model Routing
OPENROUTER_MODEL_FAST=meta-llama/llama-3.1-8b-instruct
OPENROUTER_MODEL_REASONING=deepseek/deepseek-chat
OPENROUTER_MODEL_FALLBACK=meta-llama/llama-3.1-8b-instruct
OPENROUTER_MODEL_WRITER=meta-llama/llama-3.3-70b-instruct

# Execution Guardrails & Budgeting
MAX_RESEARCH_ITERATIONS=2
MAX_SEARCH_QUERIES=6
MAX_RESULTS_PER_QUERY=5
MAX_SOURCE_CONTENT_LENGTH=8000
MAX_UPLOAD_SIZE_MB=10

# Embedding Configuration
OPENROUTER_EMBEDDING_MODEL=text-embedding-3-small
```

**⚠️ Security Note**: Never commit `.env` to version control. Use `.env.example` as a template.

---

## 🎯 Configuration

### API Keys

**OpenRouter API Key**:
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up and navigate to Dashboard
3. Copy your API key (starts with `sk-or-`)
4. Paste into `.env` as `OPENROUTER_API_KEY`

**Tavily API Key** (Optional):
1. Visit [tavily.com](https://tavily.com)
2. Sign up for free tier
3. Copy your API key (starts with `tvly-`)
4. Paste into `.env` as `TAVILY_API_KEY`

### Model Selection

Edit `.env` to select different models:

```env
# Fast decision-making
OPENROUTER_MODEL_FAST=meta-llama/llama-3.1-8b-instruct

# Deep reasoning
OPENROUTER_MODEL_REASONING=deepseek/deepseek-chat

# Fallback when the reasoning provider is overloaded
OPENROUTER_MODEL_FALLBACK=meta-llama/llama-3.1-8b-instruct

# Report writing
OPENROUTER_MODEL_WRITER=meta-llama/llama-3.3-70b-instruct
```

Browse available models at [openrouter.ai/models](https://openrouter.ai/models)

---

## ▶️ Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501` in your browser.

### Alternative: Custom Port

```bash
streamlit run app.py --server.port 8502
```

### Running in Docker

```bash
docker build -t multi-agent-researcher .
docker run -p 8501:8501 \
  -e OPENROUTER_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  multi-agent-researcher
```

---

## 📂 Project Structure

```
multi-agent-ai-deep-researcher/
├── app.py                          # Streamlit UI entry point
├── config.py                       # Settings & environment management
├── graph.py                        # LangGraph workflow orchestration
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
├── agents/                         # Research agents
│   ├── planner.py                 # Initial research planning
│   ├── parallel_researchers.py     # Technical/Market/Counter researchers
│   ├── provenance_filter.py        # Source quality filtering
│   ├── document_researcher.py      # Document analysis
│   ├── analyst.py                  # Critical analysis
│   ├── fact_checker.py             # Fact verification
│   ├── supervisor.py               # Gap-detection & routing
│   ├── insights.py                 # Pattern extraction
│   ├── report_writer.py            # Report generation
│   └── citation_auditor.py         # Citation verification
│
├── models/                         # Data models & schemas
│   ├── llm.py                      # LLM factory & validation
│   ├── schemas.py                  # Pydantic models (ResearchPlan, etc.)
│   └── state.py                    # LangGraph ResearchState definition
│
├── prompts/                        # Agent system prompts
│   ├── planner.py
│   ├── analyst.py
│   ├── fact_checker.py
│   ├── citation_auditor.py
│   └── ...
│
├── services/                       # Business logic services
│   ├── citations.py                # Citation indexing & formatting
│   └── source_ranker.py            # Source quality scoring
│
├── tools/                          # External integrations
│   ├── web_search.py               # Search API (Tavily/DuckDuckGo/Wikipedia)
│   ├── vector_store.py             # LanceDB vector embeddings
│   ├── document_loader.py          # File parsing (PDF/DOCX/TXT/MD)
│   └── upload_validator.py         # File validation
│
├── tests/                          # Test suite
│   ├── test_agents_mocked.py       # Agent unit tests
│   ├── test_citations.py           # Citation manager tests
│   └── test_vector_mocked.py       # Vector store tests
│
├── data/                           # Runtime data
│   ├── lancedb/                    # Vector database (auto-created)
│   └── uploads/                    # User-uploaded documents (temp)
│
└── .streamlit/
    └── config.toml                 # Streamlit UI configuration
```

---

## 💡 Usage Guide

### 1. **Enter Research Topic**

In the Streamlit UI, paste or type your research question:

```
"Can small language models replace large language models for enterprise RAG?"
```

### 2. **Optional: Upload Reference Documents**

Attach PDFs, DOCX, TXT, or Markdown files (up to 10MB per file) for the system to analyze.

### 3. **Start Deep Research**

Click **"Start Deep Research"** to trigger the multi-agent workflow.

### 4. **Monitor Pipeline**

Watch real-time progress as agents:
- Plan research strategy
- Execute parallel searches
- Filter and rank sources
- Analyze documents
- Verify facts
- Detect contradictions
- Generate insights
- Produce final report

### 5. **Review Results**

Navigate through tabs:
- **Final Report**: Complete markdown report with verified citations
- **Sources & Evidence**: All indexed sources with metadata
- **Agent Analysis**: Intermediate findings from each agent
- **Pipeline Errors**: Any failures or warnings

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_citations.py -v
```

### With Coverage Report

```bash
pytest tests/ --cov=agents --cov=tools --cov=models
```

### Test Files

| File | Purpose |
|------|---------|
| `test_agents_mocked.py` | Planner, web search, error handling |
| `test_citations.py` | Citation manager, auditor verification |
| `test_vector_mocked.py` | Document indexing, embeddings |

---

## 🏗️ Architecture

### Agent Workflow

```
START
  ↓
[PLANNER] - Generates research plan & search queries
  ↓
[3x RESEARCHERS] (parallel)
  ├── Technical Researcher
  ├── Market Researcher
  └── Counter Researcher
  ↓
[PROVENANCE FILTER] - Ranks & deduplicates sources
  ↓
[DOCUMENT RESEARCHER] - Analyzes uploaded documents
  ↓
[ANALYZER] - Critical analysis of findings
  ↓
[FACT CHECKER] - Verifies claims against sources
  ↓
[SUPERVISOR] - Detects gaps, routes to re-search if needed
  ↓
[INSIGHT GENERATOR] - Patterns, trends, hypotheses
  ↓
[REPORT WRITER] - Structured markdown output
  ↓
[CITATION AUDITOR] - Verifies inline citations
  ↓
END → Final Report
```

### State Flow

```python
ResearchState = {
    "topic": str,
    "research_plan": ResearchPlan,
    "search_queries": list[str],
    "raw_web_sources": list[dict],
    "web_sources": list[dict],
    "document_sources": list[dict],
    "critical_analysis": CriticalAnalysis,
    "fact_check": FactCheckResult,
    "insights": ResearchInsights,
    "final_report": str,
    "citation_audit": CitationAuditResult,
    "research_iteration": int,
    "status_messages": list[str],
    "errors": list[str]
}
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m "Add amazing feature"`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Clone and set up
git clone https://github.com/upendrasinghchandel/multi-agent-deep-researcher.git
cd multi-agent-deep-researcher
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate on Unix
pip install -r requirements.txt

# Make changes and test
pytest tests/ -v

# Commit and push
git add .
git commit -m "Your message"
git push origin feature/your-feature
```

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 🐛 Troubleshooting

### "Invalid format. OpenRouter keys start with 'sk-or-'"

**Solution**: Ensure your `.env` file has a valid OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
```

### "Search providers unavailable for... Please provide TAVILY_API_KEY"

**Solution**: This is expected if Tavily is not configured. The system will fall back to DuckDuckGo and Wikipedia. To use Tavily, add your key to `.env`:
```env
TAVILY_API_KEY=tvly-dev-your_key_here
```

### "LanceDB read-only mode" or Vector database errors

**Solution**: Ensure the `data/lancedb/` directory is writable:
```bash
chmod 755 data/lancedb/  # macOS/Linux
# or ensure permissions in Windows File Properties
```

### Streamlit not finding modules

**Solution**: Ensure you've activated the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

---

## 📞 Support

For issues, questions, or suggestions:

1. **Check existing issues** on [GitHub Issues](https://github.com/upendrasinghchandel/multi-agent-deep-researcher/issues)
2. **Create a new issue** with detailed description
3. **Contact**: upendrasinghchandel (GitHub)

---

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenRouter API Guide](https://openrouter.ai/docs)
- [Tavily Search API](https://tavily.com/docs)
- [LanceDB Vector Database](https://lancedb.com/docs)

---

## 📊 Project Stats

- **Files**: 46+
- **Tests**: 5+ unit tests
- **Python**: 3.12+
- **Dependencies**: ~30 (see requirements.txt)
- **License**: MIT
- **Status**: Active Development ✅

---

**Built with ❤️ by the Multi-Agent AI community**

Last Updated: September 2026
