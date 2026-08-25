import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd_mirror


def test_mirror_posts_new_files_once(tmp_path):
    root = tmp_path / "messages"
    (root / "claude_1").mkdir(parents=True)
    (root / "claude_1" / "20260810T000000Z-x-progress.md").write_text("hi")
    (root / "claude_1" / "README.md").write_text("not a message")
    cursor = tmp_path / "cursor.json"
    posted = []
    n = coordd_mirror.main(messages_root=root, post=posted.append,
                           cursor_path=cursor)
    assert n == 1 and posted[0]["idempotency_key"].endswith("-x-progress.md")
    assert posted[0]["actor"] == "claude_1"
    n2 = coordd_mirror.main(messages_root=root, post=posted.append,
                            cursor_path=cursor)
    assert n2 == 0 and len(posted) == 1                 # cursor holds

    (root / "claude_1" / "20260810T000001Z-x-ack.md").write_text("hi2")
    assert coordd_mirror.main(messages_root=root, post=posted.append,
                              cursor_path=cursor) == 1
