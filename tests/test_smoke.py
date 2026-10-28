from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/api/health')
    assert r.status_code == 200
    j = r.json()
    assert j.get('status') == 'operational'


def test_projects_list_initial():
    r = client.get('/api/projects')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_and_chat_accept_fts_syntax_characters():
    for query in ("How do I debug Python?", "onoma-local", "C++", 'a "quoted" term'):
        search = client.post('/api/search', json={'query': query})
        assert search.status_code == 200

        chat = client.post('/api/chat', json={'message': query})
        assert chat.status_code == 200
