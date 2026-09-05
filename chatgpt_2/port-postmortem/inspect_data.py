#!/usr/bin/env python3
import gzip, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
target = 6480540
hits = []
for p in sorted((root / 'data/raw/games').glob('*.json')):
    try:
        d = json.loads(p.read_text())
    except Exception:
        continue
    ids = []
    for a in d.get('agents', []):
        value = a.get('agentId')
        if value is not None:
            ids.append(int(value))
    if target in ids:
        hits.append((p, d))
print('target_games', len(hits))
if hits:
    p, d = hits[0]
    print('sample_path', p.relative_to(root))
    print('sample_keys', sorted(d))
    print('agent_keys', [sorted(a) for a in d.get('agents', [])])
for p in sorted((root / 'local_claude_1/ladder-queue').glob('games-*/games-*.jsonl.gz'))[-12:]:
    try:
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            row = json.loads(next(line for line in f if line.strip()))
        print('package', p.parent.name, sorted(row), [sorted(a) for a in row.get('agents', [])])
    except Exception as exc:
        print('package_error', p.parent.name, type(exc).__name__)
profile = json.loads((root / 'local_claude_1/reconstructions/profiles/norxondor_gorgonax.json').read_text())
print('profile_keys', sorted(profile))
for k, v in profile.items():
    if isinstance(v, dict):
        print('profile_section', k, sorted(v))
processed = root / 'data/processed/games.jsonl'
print('processed_games', processed.exists(), processed.stat().st_size if processed.exists() else 0)
