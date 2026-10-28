import pytest
from fastapi.testclient import TestClient

from app import db
from app.config import settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "onoma.db")
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_homepage_serves_static_ui(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Onoma AI Genesis" in response.text
    assert client.get("/static/styles.css").status_code == 200


def test_projects_list_initial(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "Onoma AI Genesis"


def test_document_upload_and_search(client):
    project = client.post(
        "/api/projects",
        json={"name": "Search project", "description": ""},
    ).json()
    response = client.post(
        "/api/documents",
        data={"project_id": str(project["id"])},
        files={
            "file": ("notes.md", b"SQLite full text search works.", "text/markdown")
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "notes.md"

    response = client.post(
        "/api/search",
        json={"query": "SQLite search", "project_id": project["id"]},
    )
    assert response.status_code == 200
    assert response.json()[0]["name"] == "notes.md"
    assert "<mark>" in response.json()[0]["snippet"]

    response = client.post(
        "/api/search",
        json={"query": 'SQLite OR "search"'},
    )
    assert response.status_code == 200


def test_upload_size_and_type_limits(client, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_LIMIT_BYTES", 3)
    response = client.post(
        "/api/documents",
        files={"file": ("notes.txt", b"four", "text/plain")},
    )
    assert response.status_code == 413

    response = client.post(
        "/api/documents",
        files={"file": ("program.exe", b"data", "application/octet-stream")},
    )
    assert response.status_code == 415


def test_database_initialization_and_fts_triggers(client):
    db.init_db()
    with db.get_db() as connection:
        project_id = connection.execute("SELECT id FROM projects LIMIT 1").fetchone()[0]
        cursor = connection.execute(
            "INSERT INTO documents(project_id, name, content) VALUES (?, ?, ?)",
            (project_id, "indexed.txt", "alpha search token"),
        )
        document_id = cursor.lastrowid
        assert connection.execute(
            "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
            ('"alpha"',),
        ).fetchone()

        connection.execute(
            "UPDATE documents SET content = ? WHERE id = ?",
            ("beta replacement token", document_id),
        )
        assert (
            connection.execute(
                "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
                ('"alpha"',),
            ).fetchone()
            is None
        )
        assert connection.execute(
            "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
            ('"replacement"',),
        ).fetchone()

        connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        assert (
            connection.execute(
                "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
                ('"replacement"',),
            ).fetchone()
            is None
        )
        assert connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
