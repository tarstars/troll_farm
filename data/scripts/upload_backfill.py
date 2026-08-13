#!/usr/bin/env python3
"""Upload the packed backfill to S3 and verify (spec Phase 1, plan A4).

Reads packs/manifests from the staging dir produced by pack_games.py, uploads to
s3://<bucket>/games/raw/backfill/ and /games/manifest/, then verifies:
  1. remote object count matches local pack+manifest count;
  2. >=3 packs re-downloaded and sha256-compared to the local summary;
  3. manifest line totals equal the summary's total_games.
Credentials: a `yc iam access-key create --format json` file (never printed, never
committed). Endpoint: storage.yandexcloud.net (ru-central1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import boto3


def client(creds_path: str):
    c = json.loads(Path(creds_path).expanduser().read_text())
    return boto3.client(
        "s3",
        endpoint_url="https://storage.yandexcloud.net",
        region_name="ru-central1",
        aws_access_key_id=c["access_key"]["key_id"],
        aws_secret_access_key=c["secret"],
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--bucket", default="troll-farm-data")
    ap.add_argument("--creds", default="~/.config/yandex-cloud/keys/agent-s3.json")
    a = ap.parse_args()

    staging = Path(a.staging)
    summary = json.loads((staging / "summary.json").read_text())
    s3 = client(a.creds)

    uploaded = 0
    for p in sorted((staging / "packs").iterdir()):
        s3.upload_file(str(p), a.bucket, f"games/raw/backfill/{p.name}")
        uploaded += 1
    for m in sorted((staging / "manifests").iterdir()):
        s3.upload_file(str(m), a.bucket, f"games/manifest/{m.name}")
        uploaded += 1
    print(f"uploaded {uploaded} objects")

    def count(prefix: str) -> int:
        n, token = 0, None
        while True:
            kw = {"Bucket": a.bucket, "Prefix": prefix}
            if token:
                kw["ContinuationToken"] = token
            r = s3.list_objects_v2(**kw)
            n += r.get("KeyCount", 0)
            if not r.get("IsTruncated"):
                return n
            token = r["NextContinuationToken"]

    n_packs = count("games/raw/backfill/")
    n_manifests = count("games/manifest/backfill-")
    exp = len(summary["packs"])
    print(f"remote: {n_packs} packs (expect {exp}), {n_manifests} manifests (expect {exp})")
    ok = n_packs == exp and n_manifests == exp

    step = max(1, exp // 3)
    for entry in summary["packs"][::step][:3]:
        body = s3.get_object(
            Bucket=a.bucket, Key=f"games/raw/backfill/{entry['pack']}")["Body"].read()
        match = hashlib.sha256(body).hexdigest() == entry["sha256"]
        print(f"spot-check {entry['pack']}: {'sha256 MATCH' if match else 'MISMATCH'}")
        ok = ok and match

    total = sum(1 for m in sorted((staging / "manifests").iterdir())
                for _ in m.open())
    print(f"manifest lines: {total} (expect {summary['total_games']})")
    ok = ok and total == summary["total_games"]

    print("VERIFY: PASS" if ok else "VERIFY: FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
