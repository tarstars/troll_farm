#!/usr/bin/env python3
"""coordctl — thin client for coordd plus the local `doctor` aggregate.
Stdlib only. Exit codes: 0 ok, 1 server refused (4xx/5xx, e.g. claim conflict),
2 transport/guard failure."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:7077"


def _token(explicit):
    if explicit:
        return explicit
    if os.environ.get("COORDD_TOKEN"):
        return os.environ["COORDD_TOKEN"]
    p = Path.home() / ".coordd" / "token"
    return p.read_text().strip() if p.exists() else ""


def _call(base, token, path, payload=None):
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"}
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _doctor(repo):
    sys.path.insert(0, str(Path(repo) / "scripts"))
    import check_clock, check_cron_health, check_ref_census
    codes = [check_clock.main(repo=repo),
             check_cron_health.main(log_path=str(Path(repo) /
                                                 "data/raw/collect_wide.log")),
             check_ref_census.main(repo=repo)]
    sacred = Path(repo) / "rust/src/bin/yamo_orchard_live.rs"
    digest = hashlib.sha256(sacred.read_bytes()).hexdigest()
    ok = digest.startswith("fff6669b")
    print(f"sacred source: {digest[:12]} {'OK' if ok else 'VIOLATED'}")
    codes.append(0 if ok else 2)
    theirs = subprocess.run(
        ["git", "-C", repo, "show", "origin/main:scripts/inbox_sweep.py"],
        capture_output=True).stdout
    mine = (Path(repo) / "scripts/inbox_sweep.py").read_bytes()
    same = hashlib.sha256(mine).hexdigest() == hashlib.sha256(theirs).hexdigest()
    print(f"inbox_sweep digest vs origin/main: {'match' if same else 'DRIFT'}")
    codes.append(0 if same else 2)
    return max(codes)


def main(argv=None, base_url=None, token=None):
    ap = argparse.ArgumentParser(prog="coordctl")
    ap.add_argument("--url", default=None)
    ap.add_argument("--token", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, *specs):
        p = sub.add_parser(name)
        for flag, kw in specs:
            p.add_argument(flag, **kw)
        return p

    add("register", ("--agent", {"required": True}),
        ("--role", {"default": "contributor"}),
        ("--tool-digest", {"default": None}),
        ("--protocol-version", {"type": int, "default": 1}))
    add("task", ("--id", {"required": True}), ("--title", {"required": True}),
        ("--priority", {"type": int, "default": 2}))
    add("task-state", ("--id", {"required": True}),
        ("--state", {"required": True}), ("--actor", {"required": True}))
    add("claim", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--prefix", {"action": "append", "required": True}))
    add("heartbeat", ("--agent", {"required": True}),
        ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}))
    add("release", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}),
        ("--outcome", {"required": True}))
    add("event", ("--actor", {"required": True}), ("--type", {"required": True}),
        ("--task", {"default": None}), ("--payload", {"default": "{}"}),
        ("--idempotency-key", {"default": None}))
    add("ack", ("--agent", {"required": True}),
        ("--event-seq", {"type": int, "required": True}))
    add("handoff", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}),
        ("--ref", {"required": True}), ("--commit", {"required": True}),
        ("--path", {"action": "append", "required": True}))
    add("tasks", ("--state", {"default": None}))
    add("events", ("--since", {"type": int, "default": 0}))
    add("doctor", ("--repo", {"default": "."}))

    a = ap.parse_args(argv)
    base = base_url or a.url or os.environ.get("COORDD_URL", DEFAULT_URL)
    tok = _token(token or a.token)

    if a.cmd == "doctor":
        try:
            h = _call(base, tok, "/health")
            print(f"coordd: reachable, server time {h['time']}")
        except (urllib.error.URLError, OSError) as e:
            print(f"coordd: UNREACHABLE ({e}) — warn-only until P2")
        return _doctor(a.repo)

    posts = {
        "register": ("/register", lambda a: {
            "agent": a.agent, "role": a.role, "tool_digest": a.tool_digest,
            "protocol_version": a.protocol_version}),
        "task": ("/task", lambda a: {"task_id": a.id, "title": a.title,
                                     "priority": a.priority}),
        "task-state": ("/task_state", lambda a: {"task_id": a.id,
                                                 "state": a.state,
                                                 "actor": a.actor}),
        "claim": ("/claim", lambda a: {"agent": a.agent, "task_id": a.task,
                                       "prefixes": a.prefix}),
        "heartbeat": ("/heartbeat", lambda a: {"agent": a.agent,
                                               "task_id": a.task,
                                               "generation": a.generation}),
        "release": ("/release", lambda a: {"agent": a.agent, "task_id": a.task,
                                           "generation": a.generation,
                                           "outcome": a.outcome}),
        "event": ("/event", lambda a: {"actor": a.actor, "type_": a.type,
                                       "task_id": a.task,
                                       "payload": json.loads(a.payload),
                                       "idempotency_key": a.idempotency_key}),
        "ack": ("/ack", lambda a: {"agent": a.agent, "event_seq": a.event_seq}),
        "handoff": ("/handoff", lambda a: {
            "agent": a.agent, "task_id": a.task, "generation": a.generation,
            "git_ref": a.ref, "commit_hex": a.commit, "paths": a.path}),
    }
    try:
        if a.cmd in posts:
            path, build = posts[a.cmd]
            print(json.dumps(_call(base, tok, path, build(a))))
        elif a.cmd == "tasks":
            q = f"?state={a.state}" if a.state else ""
            print(json.dumps(_call(base, tok, "/tasks" + q)))
        elif a.cmd == "events":
            print(json.dumps(_call(base, tok, f"/events?since={a.since}")))
        return 0
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": e.read().decode(), "status": e.code}))
        return 1
    except (urllib.error.URLError, OSError) as e:
        print(f"transport failure: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
