from typing import Any

class CitationManager:
    """Maintains deterministic source IDs and prompt encapsulation."""

    @staticmethod
    def index_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        indexed = []
        for idx, src in enumerate(sources, 1):
            src_copy = dict(src)
            if not src_copy.get("citation_id"):
                src_copy["citation_id"] = f"S{idx}"
            indexed.append(src_copy)
        return indexed

    @staticmethod
    def format_sources_for_prompt(sources: list[dict[str, Any]]) -> str:
        blocks = []
        for s in sources:
            cid = s.get("citation_id", "S?")
            title = s.get("title", "Untitled")
            url = s.get("url", "")
            content = s.get("content", "").strip()
            # Encapsulate untrusted evidence
            blocks.append(
                f'<untrusted_evidence id="{cid}" source="{url}">\n'
                f'Title: {title}\nContent: {content}\n'
                f'</untrusted_evidence>'
            )
        return "\n\n".join(blocks)

    @staticmethod
    def generate_sources_section(sources: list[dict[str, Any]]) -> str:
        lines = ["## Sources\n"]
        for s in sources:
            cid = s.get("citation_id", "S?")
            title = s.get("title", "Untitled")
            url = s.get("url", "#")
            lines.append(f"- [{cid}] **{title}** — {url}")
        return "\n".join(lines)