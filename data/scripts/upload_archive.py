#!/usr/bin/env python3
"""Upload the USB-resident bulk trees to S3 (spec Phase 3, cold archive).

Mirrors the on-disk layout under `s3://<bucket>/archive/<path>` so that a later
GeeseFS mount at the `medium_data` project path resolves the repo's 2,351
symlinks unchanged — that is why files go up individually rather than packed.
Per-file manifests land at `archive-manifest/<tree>.jsonl` (outside `archive/`,
which stays a pure mirror) with lines
`{"path", "sha256", "size", "key", "storage_class"}`.

Every object carries its sha256 as user metadata, so a re-run is idempotent
(head-and-skip when the digest already matches) and verification does not have
to re-download everything. Multipart ETags are not digests of the content, which
is precisely why the sha256 travels in metadata instead.

Nothing is ever deleted: this uploads and verifies, the USB keeps its copy.

Verification (`--verify-only` runs it alone):
  1. every manifest line has a remote object of the same size and sha256 metadata;
  2. a sample of objects is fully re-downloaded and sha256-compared, always
     including the largest sampled file so multipart reassembly is exercised;
  3. remote object count under `archive/` equals the manifest line total.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import threading
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

# Storage class per tree follows the approved spec inventory: the frozen legacy
# trees are cold, the warm experiment rows stay standard because they are read
# through the mount. `data/` (generated + external) is not in the spec's table;
# it is a symlink target read by tests, so it is treated as warm.
TREES: tuple[tuple[str, str], ...] = (
    ("artifacts/legacy-data-analysis", "COLD"),
    ("artifacts/legacy-tracked-migration", "COLD"),
    ("artifacts/worktree-salvage-20260810", "COLD"),
    ("artifacts/git-history-backup", "COLD"),
    ("outputs", "COLD"),
    ("yt_work", "COLD"),
    ("artifacts/experiments", "STANDARD"),
    ("data", "STANDARD"),
)

ARCHIVE_PREFIX = "archive/"
MANIFEST_PREFIX = "archive-manifest/"
_local = threading.local()


def _client(creds_path: str):
    """One boto3 client per thread — cheap, and avoids sharing session state."""
    if not hasattr(_local, "s3"):
        c = json.loads(Path(creds_path).expanduser().read_text())
        _local.s3 = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            region_name="ru-central1",
            aws_access_key_id=c["access_key"]["key_id"],
            aws_secret_access_key=c["secret"],
        )
    return _local.s3


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def remote_sha256(s3, bucket: str, key: str) -> tuple[str | None, int | None]:
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "403"):
            return None, None
        raise
    # Yandex echoes user metadata title-cased ("Sha256"), unlike AWS's lowercase.
    meta = {k.lower(): v for k, v in head["Metadata"].items()}
    return meta.get("sha256"), head["ContentLength"]


def tree_files(root: Path, tree: str) -> list[Path]:
    base = root / tree
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*") if p.is_file() and not p.is_symlink())


def upload_one(a, root: Path, path: Path, storage_class: str) -> dict:
    s3 = _client(a.creds)
    rel = path.relative_to(root).as_posix()
    key = f"{ARCHIVE_PREFIX}{rel}"
    digest = sha256_of(path)
    size = path.stat().st_size
    have, have_size = remote_sha256(s3, a.bucket, key)
    if have == digest and have_size == size:
        skipped = True
    else:
        s3.upload_file(
            str(path), a.bucket, key,
            ExtraArgs={"StorageClass": storage_class, "Metadata": {"sha256": digest}},
        )
        skipped = False
    return {"path": rel, "sha256": digest, "size": size,
            "key": key, "storage_class": storage_class, "skipped": skipped}


def upload_tree(a, root: Path, tree: str, storage_class: str) -> list[dict]:
    files = tree_files(root, tree)
    if not files:
        print(f"  {tree}: no files, nothing to upload")
        return []
    rows: list[dict] = []
    done_bytes = 0
    total_bytes = sum(f.stat().st_size for f in files)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(upload_one, a, root, f, storage_class) for f in files]
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            row = fut.result()
            rows.append(row)
            done_bytes += row["size"]
            if i % 100 == 0 or i == len(files):
                pct = 100 * done_bytes / total_bytes if total_bytes else 100
                print(f"  {tree}: {i}/{len(files)} files, {done_bytes/2**30:.2f} GiB ({pct:.0f}%)",
                      flush=True)
    rows.sort(key=lambda r: r["path"])
    reused = sum(1 for r in rows if r["skipped"])
    print(f"  {tree}: done — {len(rows)} objects [{storage_class}], "
          f"{total_bytes/2**30:.2f} GiB, {reused} already present")
    return rows


def write_manifest(a, tree: str, rows: list[dict]) -> str:
    s3 = _client(a.creds)
    slug = tree.replace("/", "-")
    key = f"{MANIFEST_PREFIX}{slug}.jsonl"
    body = "".join(
        json.dumps({k: r[k] for k in ("path", "sha256", "size", "key", "storage_class")},
                   sort_keys=True) + "\n"
        for r in rows
    ).encode()
    s3.put_object(Bucket=a.bucket, Key=key, Body=body,
                  Metadata={"sha256": hashlib.sha256(body).hexdigest()})
    return key


def load_manifests(a, trees=TREES) -> list[dict]:
    s3 = _client(a.creds)
    rows: list[dict] = []
    for tree, _ in trees:
        key = f"{MANIFEST_PREFIX}{tree.replace('/', '-')}.jsonl"
        try:
            body = s3.get_object(Bucket=a.bucket, Key=key)["Body"].read()
        except ClientError:
            continue
        rows.extend(json.loads(line) for line in body.decode().splitlines() if line)
    return rows


def count_prefix(s3, bucket: str, prefix: str) -> int:
    n, token = 0, None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        n += r.get("KeyCount", 0)
        if not r.get("IsTruncated"):
            return n
        token = r["NextContinuationToken"]


def verify(a, rows: list[dict], trees=TREES) -> bool:
    s3 = _client(a.creds)
    if not rows:
        print("VERIFY: FAIL — no manifest rows found")
        return False

    def check(row: dict) -> tuple[str, bool]:
        have, size = remote_sha256(_client(a.creds), a.bucket, row["key"])
        return row["key"], (have == row["sha256"] and size == row["size"])

    bad: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for key, ok in pool.map(check, rows):
            if not ok:
                bad.append(key)
    print(f"head-check: {len(rows) - len(bad)}/{len(rows)} objects match manifest size+sha256")
    for key in bad[:10]:
        print(f"  MISMATCH {key}")
    ok = not bad

    # Byte-level proof on a sample: spread across the corpus, plus the largest
    # sampled object so multipart reassembly is covered.
    by_size = sorted(rows, key=lambda r: r["size"])
    step = max(1, len(by_size) // a.spot_checks)
    sample = by_size[::step][: a.spot_checks - 1] + [by_size[-1]]
    for row in sample:
        body = s3.get_object(Bucket=a.bucket, Key=row["key"])["Body"].read()
        match = hashlib.sha256(body).hexdigest() == row["sha256"]
        print(f"spot-check {row['path']} ({row['size']/2**20:.1f} MiB): "
              f"{'sha256 MATCH' if match else 'MISMATCH'}")
        ok = ok and match

    n_remote = sum(count_prefix(s3, a.bucket, f"{ARCHIVE_PREFIX}{t}/") for t, _ in trees)
    print(f"remote objects across {len(trees)} tree prefixes: {n_remote} (expect {len(rows)})")
    ok = ok and n_remote == len(rows)
    if tuple(trees) == TREES:  # full run: a whole-prefix count also catches orphans
        n_all = count_prefix(s3, a.bucket, ARCHIVE_PREFIX)
        print(f"remote objects under {ARCHIVE_PREFIX}: {n_all} (expect {len(rows)})")
        ok = ok and n_all == len(rows)

    total = sum(r["size"] for r in rows)
    print(f"archived: {len(rows)} files, {total/2**30:.2f} GiB")
    print("VERIFY: PASS" if ok else "VERIFY: FAIL")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/media/tarstars/medium_data/database/troll_farm")
    ap.add_argument("--bucket", default="troll-farm-data")
    ap.add_argument("--creds", default="~/.config/yandex-cloud/keys/agent-s3.json")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--spot-checks", type=int, default=6)
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--only", action="append", default=None,
                    help="restrict to these trees (repeatable); default is all")
    a = ap.parse_args()

    trees = [t for t in TREES if a.only is None or t[0] in a.only]
    if not trees:
        print(f"--only matched no tree; known: {', '.join(t[0] for t in TREES)}")
        return 2

    root = Path(a.root)
    if not root.is_dir():
        print(f"source root missing: {root} — is the USB attached?")
        return 2

    if not a.verify_only:
        for tree, storage_class in trees:
            print(f"tree {tree} [{storage_class}]", flush=True)
            rows = upload_tree(a, root, tree, storage_class)
            if rows:
                print(f"  manifest -> {write_manifest(a, tree, rows)}")

    return 0 if verify(a, load_manifests(a, trees), trees) else 2


if __name__ == "__main__":
    raise SystemExit(main())
