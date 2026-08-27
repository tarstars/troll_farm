#!/usr/bin/env python3
"""Cut regenerable telemetry windows from real instrumented ladder replays.

The output is deliberately a derived index, not a copy of the replay corpus.  Each
fixture names its source game/seat/bot, records the detector that selected it, and
contains the NARRATE v6 rows needed by a grading harness.  Re-running this script on
the next instrument manifest replaces the evidence base instead of freezing old bot
behaviour as a gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

CLASSES = (
    "dance",
    "parked_troll",
    "blocked_troll",
    "stall",
    "turn_100_shack_engine_not_starting",
    "long_kept_goal",
)
UNIT_RE = re.compile(
    r"^u(?P<id>\d+)=(?P<chosen>[^/]+)/(?P<available>[^/]+)/r=(?P<branch>[A-Z])/b=(?P<blocked>\d+)/k=(?P<keep>[012])$"
)
META_RE = re.compile(r"^(?P<name>[a-z][a-z0-9_]*)=(?P<value>\d+)$")
CONCRETE = ("SHACK", "BANK(", "CELL(", "TREE(")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def narrate_fragment(stdout: str) -> str | None:
    for fragment in stdout.split(";"):
        words = fragment.strip().split()
        if "NARRATE" in words:
            at = words.index("NARRATE")
            if at + 1 < len(words) and words[at + 1] == "v6":
                return " ".join(words[at:])
    return None


def decode(fragment: str) -> dict[str, Any]:
    words = fragment.split()
    if len(words) < 3 or words[:2] != ["NARRATE", "v6"] or not words[2].startswith("t="):
        raise ValueError(f"off-grammar v6 fragment: {fragment!r}")
    row: dict[str, Any] = {"turn": int(words[2][2:]), "units": {}, "meta": {}}
    for word in words[3:]:
        unit = UNIT_RE.fullmatch(word)
        if unit:
            values = unit.groupdict()
            uid = int(values.pop("id"))
            values["blocked"] = int(values["blocked"])
            row["units"][str(uid)] = values
            continue
        meta = META_RE.fullmatch(word)
        if not meta:
            raise ValueError(f"off-grammar v6 token {word!r}")
        row["meta"][meta.group("name")] = int(meta.group("value"))
    required = {"wc", "ka", "xc", "nl", "nl_producer", "nl_door", "nl_admissibility", "nl_other"}
    missing = sorted(required - row["meta"].keys())
    if missing:
        raise ValueError(f"v6 row missing fields {missing}")
    return row


def replay_rows(path: Path, seat: int) -> list[dict[str, Any]]:
    replay = json.loads(path.read_text())
    rows = []
    for frame in replay["frames"]:
        if frame.get("agentId") != seat or not frame.get("stdout"):
            continue
        fragment = narrate_fragment(frame["stdout"])
        if fragment:
            row = decode(fragment)
            row["telemetry"] = fragment
            rows.append(row)
    rows.sort(key=lambda row: row["turn"])
    if [row["turn"] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(f"{path}: telemetry turns are not contiguous from 1")
    return rows


def concrete(value: str) -> bool:
    return value == "SHACK" or value.startswith(CONCRETE[1:])


def runs(turns: list[int]) -> list[tuple[int, int]]:
    if not turns:
        return []
    output, start, last = [], turns[0], turns[0]
    for turn in turns[1:]:
        if turn != last + 1:
            output.append((start, last))
            start = turn
        last = turn
    output.append((start, last))
    return output


def selected(rows: list[dict[str, Any]]) -> list[tuple[str, int, int, str | None, str]]:
    hits: list[tuple[str, int, int, str | None, str]] = []
    for row in rows:
        turn, meta = row["turn"], row["meta"]
        if meta["wc"] or meta["xc"]:
            hits.append(("dance", turn, turn, None, "wc>0 or xc>0"))
        if meta["ka"] > 30:
            hits.append(("long_kept_goal", turn, turn, None, "ka>30"))
        for uid, unit in row["units"].items():
            if unit["branch"] == "W":
                hits.append(("blocked_troll", turn, turn, uid, "resolver branch W"))
    idle: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        for uid, unit in row["units"].items():
            if unit["branch"] == "N" and unit["chosen"] == "NONE" and concrete(unit["available"]):
                idle[uid].append(row["turn"])
    for uid, unit_turns in idle.items():
        for start, end in runs(unit_turns):
            length = end - start + 1
            if length >= 10:
                hits.append(("parked_troll", start, end, uid, "N/NONE with concrete work >=10 turns"))
            if length >= 60:
                hits.append(("stall", start, end, uid, "N/NONE with concrete work >=60 turns"))
    return hits


def window(rows: list[dict[str, Any]], start: int, end: int, radius: int) -> list[dict[str, Any]]:
    lo, hi = max(1, start - radius), min(len(rows), end + radius)
    return [{"turn": row["turn"], "telemetry": row["telemetry"]} for row in rows if lo <= row["turn"] <= hi]


def generate(manifest_path: Path, games_dir: Path, bot_hash: str, radius: int) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    fixtures, counts, errors = [], Counter(), []
    census = {"games_matched": 0, "games_decoded": 0, "games_zero_telemetry": 0, "rows_total": 0}
    blocked_turns: dict[tuple[str, str], list[int]] = defaultdict(list)
    keep_active = False
    max_wc = 0
    for entry in manifest["entries"]:
        if not str(entry["source_sha256_prefix"]).startswith(bot_hash):
            continue
        census["games_matched"] += 1
        game_path = games_dir / f"{entry['game_id']}.json"
        if not game_path.exists():
            errors.append(f"missing game {entry['game_id']}")
            continue
        if sha256(game_path) != entry["file_sha256"]:
            errors.append(f"hash mismatch game {entry['game_id']}")
            continue
        try:
            rows = replay_rows(game_path, int(entry["our_seat"]))
            census["games_decoded"] += 1
            census["rows_total"] += len(rows)
            if not rows:
                census["games_zero_telemetry"] += 1
            keep_active = keep_active or any(
                unit["keep"] != "0" for row in rows for unit in row["units"].values()
            )
            max_wc = max([max_wc] + [row["meta"]["wc"] for row in rows])
            for klass, start, end, uid, detector in selected(rows):
                fixture_id = f"{klass}:{entry['game_id']}:s{entry['our_seat']}:u{uid or '-'}:t{start}-{end}"
                fixtures.append({
                    "fixture_id": fixture_id,
                    "class": klass,
                    "bot_hash": entry["source_sha256_prefix"],
                    "game_id": str(entry["game_id"]),
                    "seat": int(entry["our_seat"]),
                    "unit_id": None if uid is None else int(uid),
                    "event_window": [start, end],
                    "detector": detector,
                    "rows": window(rows, start, end, radius),
                })
                counts[klass] += 1
                if klass == "blocked_troll" and uid is not None:
                    blocked_turns[(str(entry["game_id"]), uid)].append(start)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"game {entry['game_id']}: {exc}")
    fixtures.sort(key=lambda item: item["fixture_id"])
    absent = {}
    for klass in CLASSES:
        if counts[klass]:
            continue
        if klass == "turn_100_shack_engine_not_starting":
            absent[klass] = "v6 does not expose referee-success ownership or the shack-engine start predicate; unavailable, not inferred"
        elif klass == "long_kept_goal" and not keep_active:
            absent[klass] = "inapplicable to this arm: keep machinery is inactive (k=0 on every decoded unit-row)"
        elif klass == "dance" and not keep_active and max_wc == 0:
            absent[klass] = "xc is inapplicable because keep machinery is inactive; wc was not observed and has no positive control in this real slice"
        elif klass == "dance" and max_wc == 0:
            absent[klass] = "not observed; wc has no positive control in this real slice"
        else:
            absent[klass] = "not observed in the selected hash-pinned replay slice"
    blocked_runs = sum(len(runs(sorted(turns))) for turns in blocked_turns.values())
    return {
        "schema_version": 1,
        "regenerate": "Run scripts/cut_fixtures.py again with the next bot hash and collector manifest; old libraries are records, never gates. Consumers should import scripts.cut_fixtures.decode for v6 rows.",
        "source_manifest_sha256": sha256(manifest_path),
        "bot_hash_filter": bot_hash,
        "window_radius": radius,
        "counts": {klass: counts[klass] for klass in CLASSES},
        "detector_metrics": {
            "blocked_troll_runs": blocked_runs,
            "blocked_troll_turn_windows": counts["blocked_troll"],
        },
        "decode_census": census,
        "absent_classes": absent,
        "errors": errors,
        "fixtures": fixtures,
    }


def grade(library: dict[str, Any]) -> list[str]:
    errors = list(library.get("errors", []))
    counts = Counter(item.get("class") for item in library.get("fixtures", []))
    for klass in CLASSES:
        if library.get("counts", {}).get(klass) != counts[klass]:
            errors.append(f"count mismatch for {klass}")
        if not counts[klass] and klass not in library.get("absent_classes", {}):
            errors.append(f"zero-count class {klass} lacks an explicit absence reason")
    for item in library.get("fixtures", []):
        for field in ("bot_hash", "game_id", "seat", "event_window", "rows", "detector"):
            if field not in item:
                errors.append(f"{item.get('fixture_id')}: missing {field}")
        if not item.get("rows"):
            errors.append(f"{item.get('fixture_id')}: empty window")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--games-dir", type=Path)
    parser.add_argument("--bot-hash")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument("--grade", type=Path, help="validate a generated library instead")
    args = parser.parse_args()
    if args.grade:
        errors = grade(json.loads(args.grade.read_text()))
        print(json.dumps({"grade": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
        return 1 if errors else 0
    if not all((args.manifest, args.games_dir, args.bot_hash, args.output)):
        parser.error("generation requires --manifest, --games-dir, --bot-hash and --output")
    library = generate(args.manifest, args.games_dir, args.bot_hash, args.radius)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(library, indent=2, sort_keys=True) + "\n")
    errors = grade(library)
    print(json.dumps({"output": str(args.output), "counts": library["counts"], "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
