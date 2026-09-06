from pydantic import BaseModel, Field

class ResearchPlan(BaseModel):
    topic: str
    objective: str
    research_questions: list[str] = Field(description="Targeted research sub-questions.")
    search_queries: list[str] = Field(description="Search engine queries.")
    key_entities: list[str] = Field(description="Key systems, technologies, or entities.")
    required_evidence: list[str] = Field(description="Empirical evidence types required.")

class SourceDocument(BaseModel):
    title: str
    url: str
    source_name: str | None = None
    published_date: str | None = None
    content: str
    retrieved_at: str

class CriticalAnalysis(BaseModel):
    confirmed_findings: list[str] = Field(description="Corroborated cross-source facts.")
    conflicting_findings: list[str] = Field(description="Direct contradictions or disputes.")
    weak_evidence: list[str] = Field(description="Unverified marketing or single-source claims.")
    missing_information: list[str] = Field(description="Critical gaps remaining in research.")
    source_quality_notes: list[str] = Field(description="Authority and recency observations.")

class VerifiedClaim(BaseModel):
    claim: str
    status: str = Field(description="'supported', 'partially supported', 'disputed', or 'unsupported'")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    supporting_sources: list[str]
    conflicting_sources: list[str]
    reasoning_summary: str

class FactCheckResult(BaseModel):
    claims: list[VerifiedClaim]

class ResearchInsights(BaseModel):
    patterns: list[str]
    trends: list[str]
    implications: list[str]
    opportunities: list[str]
    risks: list[str]
    hypotheses: list[str]

class AuditFinding(BaseModel):
    citation_id: str
    target_sentence: str
    status: str = Field(description="'verified', 'rejected_unsupported', or 'rejected_missing'")
    reasoning: str

class CitationAuditResult(BaseModel):
    audit_findings: list[AuditFinding]
    rejection_count: int
    citation_coverage_pct: float