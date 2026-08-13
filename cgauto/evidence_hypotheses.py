#!/usr/bin/env python3
"""Lightweight open-question tier. Entry cost is deliberately low; rigour is the closing tax."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

START = "<!-- HYPOTHESIS-JSON"
END = "END-HYPOTHESIS-JSON -->"
ID_RE = re.compile(r"^Q\d+$")
HYPOTHESIS_REQUIRED = {
    "id", "question", "origin", "positions", "status", "next_action",
}
ALLOWED_HYPOTHESIS_STATUS = {"open", "investigating", "resolved", "void"}

class HypothesisError(ValueError):
    pass

def extract_hypothesis(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise HypothesisError(f"{path}: missing HYPOTHESIS-JSON block")
    return json.loads(text.split(START, 1)[1].split(END, 1)[0].strip())

def load_hypotheses(repo_root: Path) -> list[dict[str, Any]]:
    d = repo_root / "docs/evidence/hypotheses"
    if not d.exists():
        return []
    return sorted(
        (extract_hypothesis(p) for p in sorted(d.glob("*.md"))),
        key=lambda h: int(h["id"][1:]) if ID_RE.match(h.get("id", "")) else 0,
    )

def validate_hypothesis(
    h: dict[str, Any], record_ids: set[str], repo_root: Path | None = None
) -> None:
    missing = sorted(HYPOTHESIS_REQUIRED - h.keys())
    if missing:
        raise HypothesisError(f"{h.get('id','<unknown>')}: missing fields {missing}")
    hid = h["id"]
    if not ID_RE.match(hid):
        raise HypothesisError(f"{hid}: id must match Q<n>")
    if h["status"] not in ALLOWED_HYPOTHESIS_STATUS:
        raise HypothesisError(f"{hid}: invalid status {h['status']!r}")
    for key in ("question", "next_action"):
        if not isinstance(h[key], str) or not h[key].strip():
            raise HypothesisError(f"{hid}: {key} required")
    for key in ("origin", "positions"):
        if not isinstance(h[key], list) or not h[key]:
            raise HypothesisError(f"{hid}: non-empty {key} required")
    for origin in h["origin"]:
        p = Path(origin)
        if p.is_absolute() or ".." in p.parts:
            raise HypothesisError(f"{hid}: unsafe origin path: {origin}")
        if repo_root is not None and not (repo_root / p).exists():
            raise HypothesisError(f"{hid}: origin path does not exist: {origin}")
    for i, pos in enumerate(h["positions"]):
        if not isinstance(pos, dict) or not pos.get("agent") or not pos.get("stance"):
            raise HypothesisError(f"{hid}.positions[{i}]: agent and stance required")
    if h["status"] == "resolved":
        target = h.get("graduated_to")
        if not target:
            raise HypothesisError(f"{hid}: resolved requires graduated_to record id")
        if target not in record_ids:
            raise HypothesisError(f"{hid}: graduated_to names unknown record {target}")
