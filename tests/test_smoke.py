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
