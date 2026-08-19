from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import get_db, init_db
from .models import ChatRequest, MemoryCreate, ProjectCreate, SearchRequest
from .services import AGENTS, OnomaOrchestrator, SearchService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Onoma AI Genesis", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

orchestrator = OnomaOrchestrator()
search_service = SearchService()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "operational", "platform": "Onoma AI Genesis", "version": "0.1.0"}


@app.get("/api/projects")
def list_projects() -> list[dict[str, Any]]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]


@app.post("/api/projects")
def create_project(project: ProjectCreate) -> dict[str, Any]:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO projects(name, description) VALUES (?, ?)",
            (project.name, project.description),
        )
        row = db.execute("SELECT * FROM projects WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


@app.get("/api/memory")
def list_memory(project_id: int | None = None) -> list[dict[str, Any]]:
    with get_db() as db:
        if project_id is None:
            rows = db.execute("SELECT * FROM memories ORDER BY id DESC LIMIT 100").fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM memories WHERE project_id = ? ORDER BY id DESC LIMIT 100",
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/memory")
def create_memory(memory: MemoryCreate) -> dict[str, Any]:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO memories(project_id, kind, content) VALUES (?, ?, ?)",
            (memory.project_id, memory.kind, memory.content),
        )
        row = db.execute("SELECT * FROM memories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    project_id: int | None = Form(default=None),
) -> dict[str, Any]:
    raw = await file.read()
    if len(raw) > 5_000_000:
        raise HTTPException(status_code=413, detail="File exceeds 5 MB MVP limit")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=415, detail="MVP accepts UTF-8 text, Markdown, JSON, CSV, or source files") from exc

    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO documents(project_id, name, media_type, content) VALUES (?, ?, ?, ?)",
            (project_id, file.filename or "untitled.txt", file.content_type or "text/plain", content),
        )
        row = db.execute("SELECT id, project_id, name, media_type, created_at FROM documents WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


@app.post("/api/search")
def search(request: SearchRequest) -> list[dict[str, Any]]:
    return search_service.search(request.query, request.project_id, request.limit)


@app.get("/api/agents")
def agents() -> list[dict[str, Any]]:
    return AGENTS


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    return orchestrator.execute(request.message, request.project_id, request.mode)


@app.get("/api/audit")
def audit() -> list[dict[str, Any]]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 100").fetchall()
        return [dict(row) for row in rows]
