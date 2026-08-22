#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
SOURCE_REL = Path('rust/src/bin/yamo_orchard_live.rs')
CONTROL_REL = Path('cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs')
SOURCE_SHA256 = 'fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f'
CONTROL_SHA256 = '6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19'
CONSTRUCTOR_NAME = 'banana_seed_factory_opponent_crop_b100_e6'
CONSTRUCTOR_ANCHOR = '            pub fn banana_seed_factory_source_separated() -> Self {'
CONSTRUCTOR_INSERT = '            pub fn banana_seed_factory_opponent_crop_b100_e6() -> Self {\n                let mut bot = Self::banana_seed_factory();\n                bot.inner.opponent_crop_bonus = 100;\n                bot.inner.opponent_crop_eta_limit = 6;\n                bot.inner.opponent_crop_start_turn = 1;\n                bot.inner.opponent_crop_min_seen = 1;\n                bot\n            }\n'
MAIN_ANCHOR = '    let mut bot = SecureOrchardBot::new();'
MAIN_REPLACEMENT = '    let mut bot = SecureOrchardBot::banana_seed_factory_opponent_crop_b100_e6();'

class BuildError(RuntimeError):
    pass

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def verify_file(path: Path, expected_sha256: str, label: str) -> bytes:
    if not path.is_file():
        raise BuildError(f'{label} missing: {path}')
    payload = path.read_bytes()
    actual = sha256_bytes(payload)
    if actual != expected_sha256:
        raise BuildError(f'{label} SHA-256 drift: expected {expected_sha256}, got {actual}: {path}')
    return payload

def unique_replace(source: str, before: str, after: str, label: str) -> str:
    count = source.count(before)
    if count != 1:
        raise BuildError(f'{label}: expected one anchor, found {count}')
    return source.replace(before, after, 1)

def inject_candidate(source: str) -> str:
    if CONSTRUCTOR_NAME in source:
        raise BuildError(f'candidate constructor already present: {CONSTRUCTOR_NAME}')
    result = unique_replace(source, CONSTRUCTOR_ANCHOR, CONSTRUCTOR_INSERT + CONSTRUCTOR_ANCHOR, 'constructor insertion')
    result = unique_replace(result, MAIN_ANCHOR, MAIN_REPLACEMENT, 'main activation')
    if result.count(f'pub fn {CONSTRUCTOR_NAME}() -> Self') != 1:
        raise BuildError('candidate constructor count is not exactly one')
    if result.count(MAIN_REPLACEMENT) != 1:
        raise BuildError('candidate main activation count is not exactly one')
    return result

def compact(repo: Path, source: str) -> str:
    sys.path.insert(0, str(repo))
    try:
        from cgauto.compact_rust_source import compact as compact_rust
    except Exception as exc:
        raise BuildError(f'cannot import cgauto.compact_rust_source: {exc}') from exc
    finally:
        try:
            sys.path.remove(str(repo))
        except ValueError:
            pass
    return compact_rust(source)

def write_sidecar(path: Path, digest: str) -> None:
    path.with_name(path.name + '.sha256').write_text(f'{digest}  {path.name}\n')

def build(repo: Path, output_dir: Path) -> dict:
    repo = repo.resolve()
    source_path = repo / SOURCE_REL
    control_path = repo / CONTROL_REL
    source_payload = verify_file(source_path, SOURCE_SHA256, 'byte-sacred source')
    verify_file(control_path, CONTROL_SHA256, 'current b100/e6 control')
    original = source_payload.decode('utf-8')
    activated = inject_candidate(original)
    if source_path.read_bytes() != source_payload:
        raise BuildError('source changed while generating candidate')
    output_dir.mkdir(parents=True, exist_ok=True)
    research_path = output_dir / 'banana-factory-b100-e6.research.rs'
    compact_path = output_dir / 'banana-factory-b100-e6.compact.rs'
    research_path.write_text(activated)
    compacted = compact(repo, activated)
    compact_path.write_text(compacted)
    research_sha = sha256_bytes(activated.encode())
    compact_sha = sha256_bytes(compacted.encode())
    write_sidecar(research_path, research_sha)
    write_sidecar(compact_path, compact_sha)
    if source_path.read_bytes() != source_payload:
        raise BuildError('byte-sacred source was modified')
    manifest = {'schema': 'troll-farm-banana-factory-b100-e6-research-build-v1', 'status': 'research_only_not_submission_ready', 'repo': str(repo), 'inputs': {'source': str(SOURCE_REL), 'source_sha256': SOURCE_SHA256, 'control': str(CONTROL_REL), 'control_sha256': CONTROL_SHA256}, 'intervention': {'constructor': CONSTRUCTOR_NAME, 'opponent_crop_bonus': 100, 'opponent_crop_eta_limit': 6, 'opponent_crop_start_turn': 1, 'opponent_crop_min_seen': 1, 'banana_factory': True, 'selector': False, 'dual_value': False, 'worker_three_bridge': False}, 'outputs': {'research': {'path': str(research_path), 'sha256': research_sha, 'bytes': research_path.stat().st_size}, 'compact': {'path': str(compact_path), 'sha256': compact_sha, 'bytes': compact_path.stat().st_size, 'under_100000_bytes': compact_path.stat().st_size < 100000}}, 'required_next_gates': ['standalone Rust compile', 'source semantic tests', 'generic b100/e6 versus deployed artifact equality', 'research versus compact/slim command-stream equality', 'factory-aware slimming if compact source exceeds 100000 bytes', 'latency and stderr checks', 'four-arm prospective panel']}
    manifest_path = output_dir / 'banana-factory-b100-e6.build.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = build(args.repo, args.output_dir)
    except BuildError as exc:
        parser.error(str(exc))
    print(json.dumps(manifest, indent=2))
if __name__ == '__main__':
    main()
