import json
import threading
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd
import coordctl

import pytest


@pytest.fixture
def live(tmp_path):
    store = coordd.Store(db_path=str(tmp_path / "c.sqlite3"))
    srv = coordd.make_server(store, token="sekret", port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_register_task_claim_roundtrip(live, capsys):
    rc = coordctl.main(["register", "--agent", "a1", "--role", "contributor"],
                       base_url=live, token="sekret")
    assert rc == 0 and json.loads(capsys.readouterr().out)["compatible"] is True
    coordctl.main(["task", "--id", "t1", "--title", "demo"],
                  base_url=live, token="sekret")
    rc = coordctl.main(["claim", "--agent", "a1", "--task", "t1",
                        "--prefix", "docs/x"], base_url=live, token="sekret")
    assert rc == 0
    out = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert out["generation"] == 1


def test_conflict_maps_to_exit_1(live, capsys):
    coordctl.main(["register", "--agent", "a1"], base_url=live, token="sekret")
    coordctl.main(["register", "--agent", "a2"], base_url=live, token="sekret")
    coordctl.main(["task", "--id", "t1", "--title", "demo"],
                  base_url=live, token="sekret")
    coordctl.main(["claim", "--agent", "a1", "--task", "t1", "--prefix", "d/"],
                  base_url=live, token="sekret")
    rc = coordctl.main(["claim", "--agent", "a2", "--task", "t1",
                        "--prefix", "d/"], base_url=live, token="sekret")
    assert rc == 1 and "error" in capsys.readouterr().out
