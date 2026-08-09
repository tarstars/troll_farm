#!/usr/bin/env python3
"""Reproducible mutation runner for the D-1..D-9 bite-test suite.

Reproduces, from the repository alone, the mutation experiment reported in
``claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md``.
The 2026-08-08 version of that experiment lived only under /tmp and was
discarded; review BAR-1 rejected it as non-reproducible.  This runner and
``mutation_manifest.json`` replace it.

GUARANTEES

* The detector sources are never modified in place.  Every mutant is applied
  to a fresh copy under a scratch work root (``--workroot``, default: a
  ``tempfile.mkdtemp``).  The runner refuses to write inside the deliverable
  directory.
* The pinned source SHA-256s in the manifest are verified before anything
  runs; a drift aborts unless ``--allow-drift`` is given (and the drift is
  then recorded in the results).
* Every patch must match its preimage EXACTLY ``expected_matches`` times.  A
  mutant whose preimage matches 0 or >1 times is reported as
  ``PATCH_FAILED`` and excluded from the kill-rate denominator; it is never
  silently applied to a neighbouring occurrence.
* A green control (unmutated copy, full suite) is run first and recorded.

WHAT IS MEASURED, per mutant

  caught              : the FULL 28-test suite has any failure or error.
  caught_by_expected  : the mutant's declared owning test class(es) --- the
                        bite-tests of the detector under mutation --- fail.
                        Reported separately because "some other detector's
                        test happened to notice" is not evidence that the
                        detector's own trigger/near-miss pair discriminates.
  liveness            : LIVE if the mutation changes the pristine digest of
                        the mutated detector over the independent probe
                        corpus (``probe_corpus.py``); UNWITNESSED if it does
                        not.  An UNWITNESSED survivor is NOT evidence that the
                        suite is weak --- the patch may simply be inert.

Usage
-----
    python3 run_mutations.py                       # full run, JSON to results/
    python3 run_mutations.py --only D6-M4,D8-M9    # subset
    python3 run_mutations.py --out /path/x.json

Deterministic, stdlib only, no network.  python3 -m unittest is the test
driver (there is no pytest on this host).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(HERE)          # .../banana-restoration-r2
COPY_FILES = ("trace_detectors.py", "conversion_race_oracle.py",
              "test_trace_detectors.py")
PROBE = os.path.join(HERE, "probe_corpus.py")
TEST_MODULE = "test_trace_detectors"


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_work(workroot, name):
    work = os.path.join(workroot, name)
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    for fn in COPY_FILES:
        shutil.copy2(os.path.join(SRC_DIR, fn), os.path.join(work, fn))
    shutil.copy2(PROBE, os.path.join(work, "probe_corpus.py"))
    return work


def run(cmd, cwd, timeout=300):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=timeout)
    return {
        "cmd": " ".join(cmd),
        "returncode": proc.returncode,
        "seconds": round(time.time() - t0, 3),
        "output_tail": proc.stdout.decode("utf-8", "replace")[-2000:],
    }


def unittest_run(work, target):
    return run([sys.executable, "-m", "unittest", target], work)


def probe_digests(work):
    res = run([sys.executable, "probe_corpus.py"], work)
    if res["returncode"] != 0:
        return None, res
    try:
        return json.loads(res["output_tail"]), res
    except json.JSONDecodeError:
        return None, res


def apply_patch(work, mutant):
    path = os.path.join(work, mutant["file"])
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    n = text.count(mutant["preimage"])
    if n != mutant["expected_matches"]:
        return None, n
    new = text.replace(mutant["preimage"], mutant["replacement"])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return sha256_text(new), n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest",
                    default=os.path.join(HERE, "mutation_manifest.json"))
    ap.add_argument("--out",
                    default=os.path.join(HERE, "results",
                                         "mutation-results.json"))
    ap.add_argument("--workroot", default=None,
                    help="scratch root; default a fresh mkdtemp")
    ap.add_argument("--only", default=None,
                    help="comma-separated mutant ids")
    ap.add_argument("--allow-drift", action="store_true")
    ap.add_argument(
        "--partial", action="store_true",
        help="acknowledge that this is deliberately not a whole-manifest run; "
             "without it, a subset or any structurally failed mutant exits 2")
    args = ap.parse_args(argv)

    with open(args.manifest, encoding="utf-8") as fh:
        manifest = json.load(fh)

    # ---- pinned-source verification -----------------------------------
    live = {name: sha256_file(os.path.join(SRC_DIR, name))
            for name in manifest["pinned_sources"]}
    drift = {name: {"pinned": manifest["pinned_sources"][name],
                    "actual": live[name]}
             for name in live if live[name] != manifest["pinned_sources"][name]}
    if drift and not args.allow_drift:
        sys.stderr.write("PINNED SOURCE DRIFT (use --allow-drift to "
                         "override):\n%s\n" % json.dumps(drift, indent=2))
        return 2

    workroot = args.workroot or tempfile.mkdtemp(prefix="bitetest-mutation-")
    if os.path.abspath(workroot).startswith(os.path.abspath(SRC_DIR)):
        sys.stderr.write("refusing to use a workroot inside the deliverable "
                         "directory: %s\n" % workroot)
        return 2
    os.makedirs(workroot, exist_ok=True)

    # ---- control -------------------------------------------------------
    control_work = make_work(workroot, "control")
    control_suite = unittest_run(control_work, TEST_MODULE)
    control_probe, control_probe_run = probe_digests(control_work)
    control_green = (control_suite["returncode"] == 0
                     and control_probe is not None)

    results = []
    wanted = set(args.only.split(",")) if args.only else None
    for mutant in manifest["mutants"]:
        if wanted is not None and mutant["id"] not in wanted:
            continue
        work = make_work(workroot, mutant["id"])
        mutated_sha, matches = apply_patch(work, mutant)
        row = {
            "id": mutant["id"],
            "detector": mutant["detector"],
            "file": mutant["file"],
            "intent": mutant["intent"],
            "excluded_from_totals": bool(mutant.get("excluded_from_totals")),
            "matches": matches,
        }
        if mutant.get("note"):
            row["note"] = mutant["note"]
        if mutated_sha is None:
            row["status"] = "PATCH_FAILED"
            results.append(row)
            continue
        row["mutated_sha256"] = mutated_sha
        compiled = run([sys.executable, "-c",
                        "import py_compile,sys;"
                        "py_compile.compile('%s', doraise=True)"
                        % mutant["file"]], work)
        if compiled["returncode"] != 0:
            row["status"] = "COMPILE_FAILED"
            row["compile"] = compiled
            results.append(row)
            continue

        full = unittest_run(work, TEST_MODULE)
        focused = {}
        for cls in mutant["owner_test_classes"]:
            focused[cls] = unittest_run(work, "%s.%s" % (TEST_MODULE, cls))
        probe, probe_run = probe_digests(work)

        caught = full["returncode"] != 0
        caught_by_expected = any(r["returncode"] != 0
                                 for r in focused.values())
        if probe is None or control_probe is None:
            liveness = "PROBE_ERROR"
            changed = None
        else:
            det = mutant["detector"]
            changed = sorted(k for k in control_probe
                             if not k.startswith("_")
                             and control_probe[k] != probe.get(k))
            liveness = "LIVE" if det in changed else (
                "LIVE_OTHER" if changed else "UNWITNESSED")

        row.update({
            "status": "OK",
            "caught": caught,
            "caught_by_expected": caught_by_expected,
            "caught_only_by_other_detector": caught and not caught_by_expected,
            "liveness": liveness,
            "probe_changed_detectors": changed,
            "full_suite": full,
            "focused": focused,
            "probe_run_returncode": probe_run["returncode"],
        })
        results.append(row)
        sys.stderr.write("%-8s %-4s caught=%-5s expected=%-5s %s\n" % (
            mutant["id"], mutant["detector"], caught, caught_by_expected,
            liveness))

    ok = [r for r in results if r.get("status") == "OK"
          and not r["excluded_from_totals"]]
    excluded = [r for r in results if r.get("excluded_from_totals")]
    caught_n = sum(1 for r in ok if r["caught"])
    expected_n = sum(1 for r in ok if r["caught_by_expected"])
    live_n = sum(1 for r in ok if r["liveness"] == "LIVE")
    per_det = {}
    for r in ok:
        d = per_det.setdefault(r["detector"], {
            "mutants": 0, "caught": 0, "caught_by_expected": 0,
            "live": 0, "live_survivors": 0})
        d["mutants"] += 1
        d["caught"] += int(r["caught"])
        d["caught_by_expected"] += int(r["caught_by_expected"])
        d["live"] += int(r["liveness"] == "LIVE")
        if r["liveness"] == "LIVE" and not r["caught"]:
            d["live_survivors"] += 1

    # ---- completeness --------------------------------------------------
    # The runner used to `return 0 if control_green else 1`, so an experiment
    # in which most mutants never patched, never compiled, or never produced a
    # probe still reported success as long as the unmutated control was green
    # (chatgpt_1 bite-test audit r2, blocker 4).  The totals already carried
    # the evidence; nothing consulted it.  A partial experiment is a legitimate
    # thing to run and an illegitimate thing to report as whole, so it is now
    # explicit rather than silent.
    patch_failed_n = sum(1 for r in results if r.get("status") == "PATCH_FAILED")
    compile_failed_n = sum(1 for r in results if r.get("status") == "COMPILE_FAILED")
    probe_error_n = sum(1 for r in results if r.get("liveness") == "PROBE_ERROR")
    declared_total = len(manifest["mutants"])
    attempted = len(results)
    subset_run = wanted is not None
    structural_failures = patch_failed_n + compile_failed_n + probe_error_n
    complete = (not subset_run
                and attempted == declared_total
                and structural_failures == 0
                and not drift)
    reasons = []
    if subset_run:
        reasons.append("--only selected %d of %d manifest entries"
                       % (attempted, declared_total))
    if attempted != declared_total and not subset_run:
        reasons.append("attempted %d of %d manifest entries"
                       % (attempted, declared_total))
    if patch_failed_n:
        reasons.append("%d mutant(s) failed to patch" % patch_failed_n)
    if compile_failed_n:
        reasons.append("%d mutant(s) failed to compile" % compile_failed_n)
    if probe_error_n:
        reasons.append("%d mutant(s) produced no probe digest, so their "
                       "liveness is unknown" % probe_error_n)
    if drift:
        reasons.append("pinned-source drift was overridden with --allow-drift")

    doc = {
        "schema": "detector-mutation-results/2",
        "completeness": {
            "complete": complete,
            "acknowledged_partial": bool(args.partial),
            "manifest_entries": declared_total,
            "attempted": attempted,
            "subset_run": subset_run,
            "patch_failed": patch_failed_n,
            "compile_failed": compile_failed_n,
            "probe_error": probe_error_n,
            "drift_overridden": bool(drift),
            "reasons": reasons,
        },
        "manifest_sha256": sha256_file(args.manifest),
        "runner_sha256": sha256_file(os.path.abspath(__file__)),
        "probe_corpus_sha256": sha256_file(PROBE),
        "python": sys.version.split()[0],
        "pinned_sources": manifest["pinned_sources"],
        "live_sources": live,
        "pinned_source_drift": drift,
        "workroot": workroot,
        "control": {
            "green": control_green,
            "suite": control_suite,
            "probe_digests": control_probe,
        },
        "excluded_entries": [
            {k: r.get(k) for k in ("id", "detector", "caught",
                                   "caught_by_expected", "liveness", "note")}
            for r in excluded],
        "totals": {
            "manifest_entries": len(manifest["mutants"]),
            "mutants_declared": len([m for m in manifest["mutants"]
                                     if not m.get("excluded_from_totals")]),
            "mutants_run": len(ok),
            "patch_failed": sum(1 for r in results
                                if r.get("status") == "PATCH_FAILED"),
            "compile_failed": sum(1 for r in results
                                  if r.get("status") == "COMPILE_FAILED"),
            "caught": caught_n,
            "survived": len(ok) - caught_n,
            "caught_by_expected": expected_n,
            "caught_only_by_other_detector": caught_n - expected_n,
            "live": live_n,
            "live_survivors": sum(1 for r in ok
                                  if r["liveness"] == "LIVE"
                                  and not r["caught"]),
            "unwitnessed": sum(1 for r in ok
                               if r["liveness"] == "UNWITNESSED"),
            "kill_rate_caught": (round(caught_n / len(ok), 4) if ok else None),
            "kill_rate_caught_by_expected": (round(expected_n / len(ok), 4)
                                             if ok else None),
        },
        "per_detector": per_det,
        "mutants": results,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write("\n")
    sys.stderr.write(
        "\ncontrol_green=%s  run=%d  caught=%d  caught_by_expected=%d  "
        "survived=%d  live=%d  unwitnessed=%d\nwrote %s\n" % (
            control_green, len(ok), caught_n, expected_n, len(ok) - caught_n,
            live_n, doc["totals"]["unwitnessed"], args.out))

    # Exit status, in severity order.  A green control over a broken experiment
    # is the failure mode being closed here: it is not a success, and it must
    # not be reportable as one by anything gating on exit status.
    if not control_green:
        sys.stderr.write(
            "INCONCLUSIVE: the unmutated control is not green, so no mutant "
            "result means anything.\n")
        return 1
    if not complete:
        if args.partial:
            sys.stderr.write(
                "PARTIAL (acknowledged with --partial): %s\n"
                "These totals describe a subset and must not be published as a "
                "whole-manifest result.\n" % "; ".join(reasons))
            return 0
        sys.stderr.write(
            "INCOMPLETE: %s\n"
            "Exiting 2. Re-run whole, or pass --partial to state on the record "
            "that this is a subset.\n" % "; ".join(reasons))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
