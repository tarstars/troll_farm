import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd


@pytest.fixture
def server(tmp_path):
    store = coordd.Store(db_path=str(tmp_path / "c.sqlite3"))
    srv = coordd.make_server(store, token="sekret", port=0)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _call(base, path, payload=None, token="sekret"):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_health_needs_no_token(server):
    assert _call(server, "/health", token=None)["ok"] is True


def test_bad_token_401(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        _call(server, "/tasks", token="wrong")
    assert e.value.code == 401


def test_register_claim_conflict_flow(server):
    _call(server, "/register", {"agent": "a1", "protocol_version": 1})
    _call(server, "/register", {"agent": "a2", "protocol_version": 1})
    _call(server, "/task", {"task_id": "t1", "title": "demo"})
    got = _call(server, "/claim", {"agent": "a1", "task_id": "t1",
                                   "prefixes": ["docs/x"]})
    assert got["generation"] == 1
    with pytest.raises(urllib.error.HTTPError) as e:
        _call(server, "/claim", {"agent": "a2", "task_id": "t1",
                                 "prefixes": ["docs/x"]})
    assert e.value.code == 409
    assert _call(server, "/tasks?state=claimed")[0]["id"] == "t1"


def test_status_page_lists_live_tasks(server):
    _call(server, "/register", {"agent": "a1", "protocol_version": 1})
    _call(server, "/task", {"task_id": "t-status", "title": "visible"})
    _call(server, "/claim", {"agent": "a1", "task_id": "t-status",
                             "prefixes": ["docs/x"]})
    req = urllib.request.Request(server + "/status",
                                 headers={"Authorization": "Bearer sekret"})
    html = urllib.request.urlopen(req).read().decode()
    assert "t-status" in html and "a1" in html
