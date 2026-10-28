from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from .db import get_db

AGENTS: list[dict[str, Any]] = [
    {
        "id": "executive",
        "name": "Executive Orchestrator",
        "role": "Plans and coordinates complex work",
        "status": "ready",
    },
    {
        "id": "research",
        "name": "Research Agent",
        "role": "Retrieval, evidence synthesis, citations",
        "status": "ready",
    },
    {
        "id": "architect",
        "name": "Systems Architect",
        "role": "Platform and infrastructure architecture",
        "status": "ready",
    },
    {
        "id": "developer",
        "name": "Developer Agent",
        "role": "Implementation, debugging, testing",
        "status": "ready",
    },
    {
        "id": "security",
        "name": "Ethical Hacker AI",
        "role": "Authorized defensive security review",
        "status": "ready",
    },
    {
        "id": "creator",
        "name": "Creative Director",
        "role": "Content, brand, interface and media planning",
        "status": "ready",
    },
    {
        "id": "documentation",
        "name": "Documentation Agent",
        "role": "Specifications, manuals and reports",
        "status": "ready",
    },
    {
        "id": "automation",
        "name": "Automation Agent",
        "role": "Workflow and task orchestration",
        "status": "ready",
    },
]


@dataclass
class RouteDecision:
    mode: str
    agent_ids: list[str]
    provider: str
    reason: str


class ModelAdapter(Protocol):
    """Contract for local and external text-generation adapters."""

    provider_name: str

    def complete(self, prompt: str) -> str: ...


class ModelRouter:
    """Provider-neutral model router with a deterministic local fallback."""

    def route(self, message: str, requested_mode: str = "auto") -> RouteDecision:
        text = message.lower()
        mode = requested_mode
        if mode == "auto":
            if any(k in text for k in ("secure", "security", "vulnerability", "audit")):
                mode = "security"
            elif any(k in text for k in ("code", "python", "api", "database", "debug")):
                mode = "code"
            elif any(k in text for k in ("research", "source", "history", "paper")):
                mode = "research"
            elif any(k in text for k in ("design", "logo", "interface", "website")):
                mode = "design"
            elif any(k in text for k in ("business", "strategy", "market")):
                mode = "business"
            else:
                mode = "general"

        mapping = {
            "security": ["executive", "security", "documentation"],
            "code": ["executive", "architect", "developer", "documentation"],
            "research": ["executive", "research", "documentation"],
            "design": ["executive", "creator", "architect"],
            "business": ["executive", "research", "documentation"],
            "general": ["executive", "documentation"],
        }
        return RouteDecision(
            mode=mode,
            agent_ids=mapping[mode],
            provider="onoma-local-fallback",
            reason=f"Selected {mode} workflow from request intent.",
        )


class SearchService:
    def search(
        self, query: str, project_id: int | None, limit: int
    ) -> list[dict[str, Any]]:
        terms = re.findall(r"\w+", query, flags=re.UNICODE)
        if not terms:
            return []
        safe_query = " AND ".join(f'"{term}"' for term in terms)
        with get_db() as db:
            sql = """
                SELECT d.id, d.project_id, d.name, d.media_type,
                       snippet(documents_fts, 1, '<mark>', '</mark>', ' … ', 24) AS snippet,
                       bm25(documents_fts) AS score
                FROM documents_fts
                JOIN documents d ON d.id = documents_fts.rowid
                WHERE documents_fts MATCH ?
            """
            params: list[Any] = [safe_query]
            if project_id is not None:
                sql += " AND d.project_id = ?"
                params.append(project_id)
            sql += " ORDER BY score LIMIT ?"
            params.append(limit)
            rows = db.execute(sql, params).fetchall()
            return [dict(row) for row in rows]


class OnomaOrchestrator:
    def __init__(self) -> None:
        self.router = ModelRouter()
        self.search_service = SearchService()

    def execute(
        self, message: str, project_id: int | None, requested_mode: str
    ) -> dict[str, Any]:
        route = self.router.route(message, requested_mode)
        evidence = self.search_service.search(message, project_id, 5)
        memory = self._recent_memory(project_id)
        response = self._compose(message, route, evidence, memory)
        self._audit(
            "chat.completed",
            {"mode": route.mode, "agents": route.agent_ids, "project_id": project_id},
        )
        return {
            "answer": response,
            "route": {
                "mode": route.mode,
                "agents": route.agent_ids,
                "provider": route.provider,
                "reason": route.reason,
            },
            "evidence": evidence,
            "memory_used": memory,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _recent_memory(self, project_id: int | None) -> list[dict[str, Any]]:
        with get_db() as db:
            if project_id is None:
                rows = db.execute(
                    "SELECT id, kind, content, created_at FROM memories ORDER BY id DESC LIMIT 5"
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT id, kind, content, created_at FROM memories "
                    "WHERE project_id = ? ORDER BY id DESC LIMIT 5",
                    (project_id,),
                ).fetchall()
            return [dict(row) for row in rows]

    def _compose(
        self,
        message: str,
        route: RouteDecision,
        evidence: list[dict[str, Any]],
        memory: list[dict[str, Any]],
    ) -> str:
        evidence_note = (
            f"I found {len(evidence)} relevant workspace document result(s) "
            "and incorporated them into the execution context."
            if evidence
            else "No matching workspace documents were found, so this response "
            "uses the local Genesis planning engine only."
        )
        memory_note = (
            f"{len(memory)} project memory item(s) were loaded."
            if memory
            else "No project memory was available."
        )
        agents = ", ".join(route.agent_ids)
        return (
            f"Onoma interpreted this as a **{route.mode}** task. "
            f"The active execution team is: {agents}.\n\n"
            f"**Request:** {message}\n\n"
            f"**Execution status:** The Genesis MVP has planned and routed the task "
            f"successfully. {evidence_note} {memory_note}\n\n"
            "**Implementation boundary:** This local build currently provides "
            "orchestration, persistence, search, memory, and agent routing. "
            "Connect an authorized external or local language-model adapter in "
            "`app/services.py` to generate provider-backed completions."
        )

    def _audit(self, event_type: str, payload: dict[str, Any]) -> None:
        with get_db() as db:
            db.execute(
                "INSERT INTO audit_events(event_type, payload) VALUES (?, ?)",
                (event_type, json.dumps(payload)),
            )
