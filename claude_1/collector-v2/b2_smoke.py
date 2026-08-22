#!/usr/bin/env python3
"""B2 smoke test — real round-trip against the bucket (task `20260811-s3-collector-v2`).

Exercises the stdlib client end to end with the live credentials, under the plan's limits:
writes only under `games/probe/`, never assumes `games/raw/backfill/` exists or is complete,
and treats the append-only grant as a property to MEASURE rather than to trust.

Steps, each recorded pass/fail in the JSON evidence:

  1. list `games/` — proves read access and reports what is already there
  2. put a unique probe object, get it back, verify sha256 byte-for-byte
  3. head the probe — size and ETag agree with what was uploaded
  4. attempt DELETE on the probe — expected to be REFUSED; a success here means the grant is
     wider than designed, which is a finding, not a convenience
  5. attempt an overwrite of the same key, twice: once plain, once with `If-None-Match: *`.
     The plan's append-only claim rests on the grant lacking delete, but nothing in the grant
     stops a PUT to an existing key, so this measures what actually protects a written object

Nothing is ever deleted, including the probe: the plan says leave it, and the uploader could
not remove it anyway. Secrets are never printed — only the key id prefix appears, via
`Credentials.__repr__`.

Usage: python3 claude_1/collector-v2/b2_smoke.py --out <results.json>
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s3client import DEFAULT_ENDPOINT, DEFAULT_KEYS, Credentials, S3Client, S3Error  # noqa: E402

BUCKET = "troll-farm-data"


def step(record: dict, name: str, fn):
    entry = {"step": name}
    try:
        entry["result"] = fn()
        entry["status"] = "ok"
    except S3Error as error:
        entry.update(status="s3_error", http_status=error.status, code=error.code,
                     message=error.s3_message)
    except Exception as error:  # noqa: BLE001
        entry.update(status="error", error=f"{type(error).__name__}: {error}"[:400])
    record["steps"].append(entry)
    return entry


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B2 live smoke test")
    ap.add_argument("--out", required=True)
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--keys", default=str(DEFAULT_KEYS))
    args = ap.parse_args(argv)

    credentials = Credentials.load(args.keys)
    client = S3Client(args.bucket, credentials=credentials, endpoint=args.endpoint)

    run_stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    probe_key = f"games/probe/b2-smoke-{run_stamp}-{os.getpid()}.json"
    payload = json.dumps({
        "probe": "b2-smoke", "task_id": "20260811-s3-collector-v2", "agent": "claude_1",
        "written_utc": run_stamp,
        "note": "B2 round-trip probe. Left in place deliberately: the plan says leave it, and "
                "the uploader grant cannot delete it.",
    }, indent=2, sort_keys=True).encode()
    digest = hashlib.sha256(payload).hexdigest()

    record: dict = {
        "check": "b2-s3-smoke",
        "task_id": "20260811-s3-collector-v2",
        "run_utc": run_stamp,
        "endpoint": args.endpoint,
        "bucket": args.bucket,
        "credentials": repr(credentials),  # redacted by construction
        "probe_key": probe_key,
        "payload_sha256": digest,
        "steps": [],
    }

    listing = step(record, "list games/", lambda: {
        "count": len(client.list_objects("games/")),
        "sample_keys": [row["key"] for row in client.list_objects("games/")[:10]],
    })

    put = step(record, "put probe", lambda: client.put_object(
        probe_key, payload, content_type="application/json"))

    def roundtrip():
        body = client.get_object(probe_key)
        return {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "identical": hashlib.sha256(body).hexdigest() == digest,
                "byte_for_byte": body == payload}

    got = step(record, "get probe and verify sha256", roundtrip)
    head = step(record, "head probe", lambda: client.head_object(probe_key))

    delete = step(record, "attempt delete (expected refused)",
                  lambda: client.delete_object(probe_key))
    overwrite = step(record, "attempt plain overwrite",
                     lambda: client.put_object(probe_key, payload + b"\n",
                                               content_type="application/json"))
    guarded = step(record, "attempt overwrite with If-None-Match: *",
                   lambda: client.put_object(probe_key, payload + b"\n\n",
                                             content_type="application/json",
                                             if_none_match=True))

    delete_refused = delete["status"] != "ok"
    overwrite_allowed = overwrite["status"] == "ok"
    guard_honoured = guarded["status"] != "ok"

    record["findings"] = {
        "read_access": listing["status"] == "ok",
        "write_round_trip_verified": (put["status"] == "ok" and got["status"] == "ok"
                                      and got.get("result", {}).get("byte_for_byte") is True),
        "head_agrees": (head["status"] == "ok"
                        and head.get("result", {}).get("size") == len(payload)),
        "delete_refused_as_designed": delete_refused,
        "overwrite_possible_despite_append_only_grant": overwrite_allowed,
        "if_none_match_honoured_by_endpoint": guard_honoured,
    }
    record["notes"] = [
        "The probe object is left in place on purpose (plan B2) and cannot be removed with "
        "this grant.",
        ("Append-only comes from the GRANT lacking delete; it does NOT stop a PUT to an "
         "existing key. Measured above: overwrite "
         + ("SUCCEEDED" if overwrite_allowed else "was refused")
         + ", If-None-Match guard "
         + ("was honoured" if guard_honoured else "did NOT prevent the write")
         + ". B3/B4 must therefore make key collisions impossible by construction rather "
           "than rely on the grant."),
    ]
    blocking = [name for name, ok in (
        ("read_access", record["findings"]["read_access"]),
        ("write_round_trip_verified", record["findings"]["write_round_trip_verified"]),
        ("head_agrees", record["findings"]["head_agrees"]),
    ) if not ok]
    record["verdict"] = "SMOKE_OK" if not blocking else "SMOKE_FAILED"
    record["blocking"] = blocking

    Path(args.out).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": record["verdict"], "findings": record["findings"],
                      "probe_key": probe_key, "blocking": blocking}, indent=2))
    return 0 if not blocking else 1


if __name__ == "__main__":
    sys.exit(main())
