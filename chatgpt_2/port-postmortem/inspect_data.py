#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
target = 6480540


def compact(value, limit=6000):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return text[:limit]


profile = json.loads((root / "local_claude_1/reconstructions/profiles/norxondor_gorgonax.json").read_text())
print("PROFILE_GAME_COUNT", len(profile.get("games", [])))
if profile.get("games"):
    first = profile["games"][0]
    print("PROFILE_GAME_KEYS", sorted(first))
    print("PROFILE_GAME_SAMPLE", compact(first, 12000))
    all_keys = sorted({key for row in profile["games"] for key in row})
    print("PROFILE_GAME_ALL_KEYS", all_keys)

for section in ("verbs_by_bucket_per_game", "training", "planting", "harvesting", "chopping", "mining"):
    print("PROFILE_SECTION_SAMPLE", section, compact(profile.get(section), 12000))

raw_hits = []
for path in sorted((root / "data/raw/games").glob("*.json")):
    try:
        game = json.loads(path.read_text())
    except Exception:
        continue
    ids = [int(agent["agentId"]) for agent in game.get("agents", []) if agent.get("agentId") is not None]
    if target in ids:
        raw_hits.append((path, game))
print("RAW_TARGET_GAMES", len(raw_hits))
if raw_hits:
    path, game = raw_hits[0]
    print("RAW_SAMPLE_PATH", path.relative_to(root))
    print("RAW_SAMPLE_AGENTS", compact(game.get("agents"), 12000))
    print("RAW_SAMPLE_METADATA", compact(game.get("metadata"), 12000))
    print("RAW_SAMPLE_SCORES", compact(game.get("scores"), 12000))

package_names = ["games-41202036", "games-41234663", "games-41236823"]
for dirname in package_names:
    directory = root / "local_claude_1"
    candidates = list(directory.glob(f"**/{dirname}/games-*.jsonl.gz"))
    if not candidates:
        print("PACKAGE_MISSING", dirname)
        continue
    package = candidates[0]
    with gzip.open(package, "rt", encoding="utf-8") as handle:
        row = json.loads(next(line for line in handle if line.strip()))
    print("PACKAGE_PATH", package.relative_to(root))
    print("PACKAGE_ROW_KEYS", dirname, sorted(row))
    print("PACKAGE_AGENTS", dirname, compact(row.get("agents"), 12000))
    print("PACKAGE_METADATA", dirname, compact(row.get("metadata"), 12000))
    manifest = package.parent / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        print("PACKAGE_MANIFEST_KEYS", dirname, sorted(data))
        print("PACKAGE_MANIFEST_SAMPLE", dirname, compact(data, 16000))
    ladder = package.parent / "ladder-read.json"
    if ladder.exists():
        data = json.loads(ladder.read_text())
        print("PACKAGE_LADDER_KEYS", dirname, sorted(data[0]) if isinstance(data, list) and data else sorted(data))
        print("PACKAGE_LADDER_SAMPLE", dirname, compact(data[:2] if isinstance(data, list) else data, 16000))

for path in [
    root / "data/raw/leaderboard.json",
    root / "data/processed/stats.json",
]:
    data = json.loads(path.read_text())
    print("DATA_SAMPLE", path.relative_to(root), compact(data, 16000))
