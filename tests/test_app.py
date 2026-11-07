import os
import tempfile
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

os.environ['DATABASE_PATH'] = tempfile.mktemp(suffix='.db')
from app.main import app, init_db


def test_health():
    with TestClient(app) as client:
        assert client.get('/api/health').json()['status'] == 'ok'


def test_repo_validation():
    with TestClient(app) as client:
        r = client.post('/api/analyze', json={'repo': 'invalid repo'})
        assert r.status_code == 422


def test_approval_required():
    with TestClient(app) as client:
        r = client.post('/api/runs/missing/post', json={'draft': 'hello'})
        assert r.status_code == 403


def test_analysis_saves_draft():
    sample = [{'number': 1, 'title': 'Bug', 'body': 'Fails', 'labels': ['bug'], 'url': 'https://github.com/example/repo/issues/1'}]
    with patch('app.main.github_issues', new_callable=AsyncMock, return_value=sample), patch('app.main.llm_report', new_callable=AsyncMock, return_value=('Issue #1 needs triage.', 'Please review issue #1.')):
        with TestClient(app) as client:
            r = client.post('/api/analyze', json={'repo': 'example/repo'})
            assert r.status_code == 200
            assert r.json()['status'] == 'awaiting_approval'
            assert len(client.get('/api/runs').json()) >= 1
