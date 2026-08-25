#!/usr/bin/env python3
"""Shadow-mode mirror (spec §6 P1): posts each new coordination message file into
coordd as a 'legacy_message' event. Git stays authoritative during shadow; the
idempotency key (the repo-relative path) makes re-runs and restarts harmless."""
import argparse
import json
import re
import sys
from pathlib import Path

MSG_RE = re.compile(r"^\d{8}T\d{6}Z-.+\.md$")


def _default_post_factory(url, token):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import coordctl

    def post(ev):
        rc = coordctl.main(
            ["event", "--actor", ev["actor"], "--type", "legacy_message",
             "--task", ev.get("task_id") or "",
             "--payload", json.dumps(ev["payload"]),
             "--idempotency-key", ev["idempotency_key"]],
            base_url=url, token=token)
        if rc != 0:
            raise RuntimeError(f"mirror post failed rc={rc} for {ev}")
    return post


def main(messages_root, post, cursor_path):
    root = Path(messages_root)
    cursor_path = Path(cursor_path)
    seen = set(json.loads(cursor_path.read_text())) if cursor_path.exists() else set()
    new = 0
    for f in sorted(root.glob("*/*.md")):
        rel = f"{f.parent.name}/{f.name}"
        if rel in seen or not MSG_RE.match(f.name):
            continue
        post({"actor": f.parent.name, "task_id": None,
              "payload": {"path": f"coordination/messages/{rel}"},
              "idempotency_key": f"coordination/messages/{rel}"})
        seen.add(rel)
        new += 1
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    cursor_path.write_text(json.dumps(sorted(seen)))
    return new


def cli(argv=None):
    # was a fat __main__ body: URL/env resolution lived unreachable (G4)
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="coordination/messages")
    ap.add_argument("--cursor", default=str(Path.home() / ".coordd" /
                                            "mirror-cursor.json"))
    ap.add_argument("--url", default=None)
    ap.add_argument("--token", default=None)
    a = ap.parse_args(argv)
    url = a.url or os.environ.get("COORDD_URL", "http://127.0.0.1:7077")
    n = main(messages_root=a.root,
             post=_default_post_factory(url, a.token),
             cursor_path=a.cursor)
    print(f"mirrored {n} new message(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
