#!/usr/bin/env python3
"""pre_review — mechanized adversarial pre-review gate (pipeline v2, Change 1).

Enforces the failure ledger (failure-ledger.json) derived from the three
banana-restoration-r2 rejections. Four mechanized checks:

  trace-provenance  SCRIPTED_TRACE      a trace declared candidate-driven must
                    survive regeneration: compile the declared source, replay
                    the committed transcript, byte-compare the emitted command
                    lines against the committed commands file. Declared
                    scripted controls ({"scripted": true, "critical": false})
                    are allowed but listed; a scripted critical trace blocks.
  single-model      MODEL_DIVERGENCE    every declared oracle module must
                    exist; every allowed importer must actually import it;
                    quantity-pattern hits in scanned files are explained only
                    inside verified importers / declared mirrors. Unexplained
                    hits block. Comment-only lines are reported, not blocked
                    (prose cannot compute).
  red-reason        RED_WRONG_REASON    every red/green pair's check command is
                    run against the OLD bytes; it must exit nonzero AND its
                    output must match every expected-failure-signature regex.
                    Exit 0 on the old bytes, or a signature mismatch, blocks.
  claims-coverage   VACUOUS_EVIDENCE / SPEC_TEST_GAP / MISSING_DELIVERABLE
                    every claims-file evidence path must exist; no critical
                    invariant may carry scripted-control evidence; every
                    critical invariant needs at least one non-scripted entry;
                    every required deliverable must exist; every mechanized
                    ledger class must be fed by the config (or explicitly
                    waived with a reason).

Additionally the config may declare "external_checks": commands run AFTER
the four built-in checks, in declared order (so a configured fuzz-panel
runs last). Exit 0 is CLEAR, exit 1 is a blocking finding attributed to the
entry's declared ledger_class (an external BLOCK is a pre-review BLOCK),
any other exit is a tool error. Ledger classes may name an external check
as their pre_review_check (e.g. UNSAMPLED_STATE_SPACE -> fuzz-panel).

CLI:
  python3 pre_review.py --config <task-config.json> --report <out.md>
                        [--json <out.json>] [--only <check> ...]

Exit codes: 0 = CLEAR, 1 = BLOCK, 2 = tool/config error.

Deterministic: no network, no timestamps, stable ordering. Paths in the
config are resolved relative to the config file's directory;
old_source_git entries are materialized via `git show` against the
repository containing the config (override with "git_root").

Stdlib only (Python 3.12). Rust sources are compiled with
  rustc --edition=2021 -O -Awarnings --crate-name <crate>
(rustc found via $RUSTC, PATH, then ~/.cargo/bin).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK_NAMES = ("trace-provenance", "single-model", "red-reason", "claims-coverage")
EXIT_CLEAR, EXIT_BLOCK, EXIT_ERROR = 0, 1, 2
EVIDENCE_TYPES = ("candidate-driven", "fixture", "static-assert", "scripted-control")
DEFAULT_TIMEOUT = 300

# Which config section feeds each mechanized check (for ledger coverage).
CHECK_INPUT_SECTIONS = {
    "trace-provenance": "traces",
    "single-model": "oracles",
    "red-reason": "red_green_pairs",
    "claims-coverage": "claims",
}


class ToolError(Exception):
    """Config / environment error -> exit 2."""


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

class Context:
    def __init__(self, config_path: Path):
        self.config_path = config_path.resolve()
        self.config_dir = self.config_path.parent
        try:
            self.config = json.loads(self.config_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise ToolError(f"cannot load config {config_path}: {exc}")
        self.tempdir = Path(tempfile.mkdtemp(prefix="pre-review-"))
        self._git_root = None
        self._rustc = None
        self._compile_cache: dict[tuple[str, str], Path] = {}

    def resolve(self, path: str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else (self.config_dir / p).resolve()

    @property
    def git_root(self) -> Path:
        if self._git_root is None:
            declared = self.config.get("git_root")
            if declared:
                self._git_root = self.resolve(declared)
            else:
                proc = subprocess.run(
                    ["git", "-C", str(self.config_dir), "rev-parse", "--show-toplevel"],
                    capture_output=True, text=True)
                if proc.returncode != 0:
                    raise ToolError(
                        "config dir is not inside a git repository and no "
                        "git_root is declared: " + proc.stderr.strip())
                self._git_root = Path(proc.stdout.strip())
        return self._git_root

    @property
    def rustc(self) -> str:
        if self._rustc is None:
            cand = (os.environ.get("RUSTC")
                    or shutil.which("rustc")
                    or str(Path.home() / ".cargo" / "bin" / "rustc"))
            if not Path(cand).exists():
                raise ToolError("rustc not found ($RUSTC, PATH, ~/.cargo/bin)")
            self._rustc = cand
        return self._rustc

    def compile_rust(self, source: Path, crate_name: str) -> Path:
        key = (str(source), crate_name)
        if key in self._compile_cache:
            return self._compile_cache[key]
        out = self.tempdir / f"bin-{crate_name}-{len(self._compile_cache)}"
        proc = subprocess.run(
            [self.rustc, "--edition=2021", "-O", "-Awarnings",
             "--crate-name", crate_name, "-o", str(out), str(source)],
            capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if proc.returncode != 0:
            raise ToolError(
                f"rustc failed on {source} (crate {crate_name}):\n"
                + proc.stderr[-2000:])
        self._compile_cache[key] = out
        return out

    def git_show(self, commit: str, path: str, label: str) -> Path:
        out = self.tempdir / f"git-{label}{Path(path).suffix}"
        proc = subprocess.run(
            ["git", "-C", str(self.git_root), "show", f"{commit}:{path}"],
            capture_output=True)
        if proc.returncode != 0:
            raise ToolError(
                f"git show {commit}:{path} failed: "
                + proc.stderr.decode(errors="replace").strip())
        out.write_bytes(proc.stdout)
        return out


def finding(class_id: str, subject: str, detail: str) -> dict:
    return {"class": class_id, "subject": subject, "detail": detail}


def check_result(name: str, findings: list, info: list) -> dict:
    return {
        "check": name,
        "verdict": "BLOCK" if findings else "CLEAR",
        "findings": findings,
        "info": info,
    }


# ---------------------------------------------------------------------------
# Check a: trace-provenance
# ---------------------------------------------------------------------------

def divergences(expected: str, got: str, limit: int = 5) -> tuple[int, list]:
    """(total_diverging_lines, first `limit` of them) between the committed
    commands and the regenerated output, line-aligned."""
    exp_lines = expected.splitlines()
    got_lines = got.splitlines()
    n = max(len(exp_lines), len(got_lines))
    diffs = []
    total = 0
    for i in range(n):
        e = exp_lines[i] if i < len(exp_lines) else "<absent>"
        g = got_lines[i] if i < len(got_lines) else "<absent>"
        if e != g:
            total += 1
            if len(diffs) < limit:
                diffs.append({"line": i + 1, "committed": e,
                              "regenerated": g})
    return total, diffs


def run_trace_provenance(ctx: Context) -> dict:
    findings, info = [], []
    traces = ctx.config.get("traces", [])
    if not traces:
        info.append("no traces declared in config")
    timeout = ctx.config.get("timeout", DEFAULT_TIMEOUT)
    for tr in traces:
        name = tr.get("name", "<unnamed>")
        transcript = ctx.resolve(tr["transcript"])
        commands = ctx.resolve(tr["commands"])
        for p, what in ((transcript, "transcript"), (commands, "commands")):
            if not p.exists():
                raise ToolError(f"trace {name}: {what} file missing: {p}")
        if tr.get("scripted", False):
            if tr.get("critical", False):
                findings.append(finding(
                    "SCRIPTED_TRACE", name,
                    "declared scripted AND critical: scripted evidence on the "
                    "critical path is an automatic block (pipeline Change 1 "
                    "item 1)"))
            else:
                info.append(
                    f"{name}: declared scripted control (allowed, "
                    f"non-critical). {tr.get('note', '')}".rstrip())
            continue
        source = ctx.resolve(tr["binary_source"])
        if not source.exists():
            raise ToolError(f"trace {name}: binary_source missing: {source}")
        binary = ctx.compile_rust(source, tr["crate_name"])
        try:
            proc = subprocess.run(
                [str(binary)], input=transcript.read_bytes(),
                capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ToolError(f"trace {name}: candidate binary timed out")
        regenerated = proc.stdout.decode(errors="replace")
        committed = commands.read_text()
        if regenerated == committed:
            info.append(
                f"{name}: regeneration MATCH "
                f"({len(committed.splitlines())} command lines byte-identical)")
        else:
            total, divs = divergences(committed, regenerated)
            shown = "; ".join(
                f"line {d['line']}: committed {d['committed']!r} vs "
                f"regenerated {d['regenerated']!r}" for d in divs)
            findings.append(finding(
                "SCRIPTED_TRACE", name,
                "declared candidate-driven but the committed commands do not "
                "survive regeneration from the declared source "
                f"({tr['binary_source']}): {total} of "
                f"{len(committed.splitlines())} command lines diverge "
                f"(regenerated {len(regenerated.splitlines())} lines). "
                f"First {len(divs)}: {shown}"))
    return check_result("trace-provenance", findings, info)


# ---------------------------------------------------------------------------
# Check b: single-model
# ---------------------------------------------------------------------------

def default_import_regex(module_stem: str) -> str:
    return (r"^\s*(?:import\s+.*\b{m}\b|from\s+.*\b{m}\b\s+import\b)"
            .format(m=re.escape(module_stem)))


def is_comment_line(line: str) -> bool:
    s = line.lstrip()
    return s.startswith(("#", "//", "/*", "*"))


def run_single_model(ctx: Context) -> dict:
    findings, info = [], []
    oracles = ctx.config.get("oracles", [])
    if not oracles:
        info.append("no oracles declared in config")
    for oracle in oracles:
        name = oracle["name"]
        module = ctx.resolve(oracle["module_path"])
        if not module.exists():
            findings.append(finding(
                "MODEL_DIVERGENCE", name,
                f"declared oracle module does not exist: "
                f"{oracle['module_path']}"))
            continue
        stem = module.stem
        patterns = [re.compile(p) for p in oracle["quantity_patterns"]]
        import_line_re = re.compile(default_import_regex(stem))
        # verified files whose hits are explained
        verified: dict[str, str] = {}   # resolved path -> how explained
        for imp in oracle.get("allowed_importers", []):
            entry = {"path": imp} if isinstance(imp, str) else imp
            p = ctx.resolve(entry["path"])
            if not p.exists():
                findings.append(finding(
                    "MODEL_DIVERGENCE", entry["path"],
                    f"allowed_importer of {name} does not exist"))
                continue
            rx = re.compile(entry.get("import_regex")
                            or default_import_regex(stem), re.M)
            if rx.search(p.read_text(errors="replace")):
                verified[str(p)] = "verified importer"
                info.append(f"{name}: importer verified: {entry['path']}")
            else:
                findings.append(finding(
                    "MODEL_DIVERGENCE", entry["path"],
                    f"listed as allowed_importer of {name} but no import "
                    f"statement matching {rx.pattern!r} was found - its "
                    "quantity references are unexplained"))
        for mir in oracle.get("allowed_mirrors", []):
            entry = {"path": mir} if isinstance(mir, str) else mir
            p = ctx.resolve(entry["path"])
            if not p.exists():
                findings.append(finding(
                    "MODEL_DIVERGENCE", entry["path"],
                    f"allowed_mirror of {name} does not exist"))
                continue
            text = p.read_text(errors="replace")
            marker = entry.get("marker_regex")
            if marker and not re.search(marker, text):
                findings.append(finding(
                    "MODEL_DIVERGENCE", entry["path"],
                    f"declared mirror of {name} lacks the required marker "
                    f"{marker!r} - an unmarked mirror is indistinguishable "
                    "from a divergent reimplementation"))
                continue
            verified[str(p)] = "declared mirror"
            cites = name in text
            info.append(
                f"{name}: mirror accepted: {entry['path']}"
                + ("" if cites else
                   f" [NOTE: file never cites the oracle name {name}"
                   + (f"; declared rationale: {entry['note']}"
                      if entry.get("note") else "") + "]"))
        for sf in oracle.get("scan_files", []):
            p = ctx.resolve(sf)
            if not p.exists():
                raise ToolError(f"single-model scan file missing: {sf}")
            if p == module:
                continue    # the oracle itself is the one sanctioned home
            comment_mentions = 0
            for lineno, line in enumerate(
                    p.read_text(errors="replace").splitlines(), start=1):
                if import_line_re.search(line):
                    continue
                matched = [pt.pattern for pt in patterns if pt.search(line)]
                if not matched:
                    continue
                if is_comment_line(line):
                    comment_mentions += 1
                    continue
                where = f"{sf}:{lineno}"
                if str(p) in verified:
                    info.append(
                        f"{name}: explained hit ({verified[str(p)]}) "
                        f"{where}: {line.strip()[:120]}")
                else:
                    findings.append(finding(
                        "MODEL_DIVERGENCE", where,
                        f"quantity governed by {name} computed outside the "
                        f"oracle (pattern {matched[0]!r}) in a file that is "
                        "neither a verified importer nor a declared mirror: "
                        f"{line.strip()[:160]}"))
            if comment_mentions:
                info.append(
                    f"{name}: {sf}: {comment_mentions} comment-only "
                    "mention(s) (prose, not computation - not blocking)")
    return check_result("single-model", findings, info)


# ---------------------------------------------------------------------------
# Check c: red-reason
# ---------------------------------------------------------------------------

def run_red_reason(ctx: Context) -> dict:
    findings, info = [], []
    pairs = ctx.config.get("red_green_pairs", [])
    if not pairs:
        info.append("no red/green pairs declared in config")
    timeout = ctx.config.get("timeout", DEFAULT_TIMEOUT)
    for pair in pairs:
        name = pair.get("name", "<unnamed>")
        if "old_source" in pair:
            old = ctx.resolve(pair["old_source"])
            old_label = pair["old_source"]
            if not old.exists():
                raise ToolError(f"pair {name}: old_source missing: {old}")
        else:
            g = pair["old_source_git"]
            old = ctx.git_show(g["commit"], g["path"],
                               re.sub(r"\W+", "-", name))
            old_label = f"git:{g['commit']}:{g['path']}"
        cmd = [a.replace("{source}", str(old)) for a in pair["check_cmd"]]
        cwd = ctx.resolve(pair.get("cwd", "."))
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ToolError(f"pair {name}: check command timed out")
        except OSError as exc:
            raise ToolError(f"pair {name}: cannot run {cmd[0]}: {exc}")
        output = proc.stdout + proc.stderr
        if proc.returncode == 0:
            findings.append(finding(
                "RED_WRONG_REASON", name,
                f"check exits 0 on the old bytes ({old_label}) - the "
                "regression does not discriminate the defect at all"))
            continue
        missing = [rx for rx in
                   pair["expected_failure_signature"]["must_match_regexes"]
                   if not re.search(rx, output, re.S)]
        if missing:
            findings.append(finding(
                "RED_WRONG_REASON", name,
                f"check fails on the old bytes ({old_label}, exit "
                f"{proc.returncode}) but the failure signature does not match "
                f"the documented defect mechanism; unmatched regex(es): "
                + "; ".join(repr(m) for m in missing)
                + f". Output tail: {output[-400:]!r}"))
        else:
            info.append(
                f"{name}: RED for the right reason on {old_label} "
                f"(exit {proc.returncode}, all "
                f"{len(pair['expected_failure_signature']['must_match_regexes'])}"
                " signature regexes matched)")
    return check_result("red-reason", findings, info)


# ---------------------------------------------------------------------------
# Check d: claims-coverage
# ---------------------------------------------------------------------------

def load_ledger(ctx: Context) -> dict:
    declared = ctx.config.get("ledger")
    if declared:
        path = ctx.resolve(declared)
    else:
        path = Path(__file__).resolve().parent / "failure-ledger.json"
    if not path.exists():
        raise ToolError(f"failure ledger not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ToolError(f"failure ledger is not valid JSON: {exc}")


def config_feeds_check(ctx: Context, check: str, class_id: str) -> bool:
    cfg = ctx.config
    for entry in cfg.get("external_checks", []):
        if entry.get("name") == check:
            return True
    if check == "trace-provenance":
        return any(not t.get("scripted", False) for t in cfg.get("traces", []))
    if check == "single-model":
        return bool(cfg.get("oracles"))
    if check == "red-reason":
        return bool(cfg.get("red_green_pairs"))
    if check == "claims-coverage":
        if class_id == "MISSING_DELIVERABLE":
            return bool(cfg.get("required_deliverables"))
        claims = cfg.get("claims") or {}
        return bool(claims.get("path")) and bool(
            claims.get("critical_invariants"))
    return False


def run_claims_coverage(ctx: Context) -> dict:
    findings, info = [], []
    ledger = load_ledger(ctx)
    claims_cfg = ctx.config.get("claims") or {}
    entries = []
    if claims_cfg.get("path"):
        claims_path = ctx.resolve(claims_cfg["path"])
        if not claims_path.exists():
            raise ToolError(f"claims file missing: {claims_path}")
        try:
            entries = json.loads(claims_path.read_text())
        except json.JSONDecodeError as exc:
            raise ToolError(f"claims file is not valid JSON: {exc}")
    critical = list(claims_cfg.get("critical_invariants", []))
    by_invariant: dict[str, list] = {}
    for i, entry in enumerate(entries):
        inv = entry.get("invariant", f"<entry {i}>")
        etype = entry.get("evidence_type")
        epath = entry.get("evidence_path", "")
        if etype not in EVIDENCE_TYPES:
            raise ToolError(
                f"claims entry {i} ({inv}): evidence_type {etype!r} not in "
                f"{EVIDENCE_TYPES}")
        resolved = ctx.resolve(epath)
        exists = resolved.exists()
        if not exists:
            findings.append(finding(
                "VACUOUS_EVIDENCE", f"{inv} -> {epath}",
                "claims entry cites an evidence path that does not exist"))
        if inv in critical and etype == "scripted-control":
            findings.append(finding(
                "VACUOUS_EVIDENCE", f"{inv} -> {epath}",
                "critical invariant backed by scripted-control evidence - "
                "scripted evidence on the critical path is an automatic "
                "block (pipeline Change 1 item 1)"))
        by_invariant.setdefault(inv, []).append(
            {"type": etype, "exists": exists})
    for inv in critical:
        good = [e for e in by_invariant.get(inv, [])
                if e["exists"] and e["type"] != "scripted-control"]
        if good:
            info.append(
                f"critical invariant {inv}: {len(good)} non-scripted "
                "evidence entr(y/ies) present")
        else:
            findings.append(finding(
                "SPEC_TEST_GAP", inv,
                "critical invariant has no existing non-scripted-control "
                "evidence entry - no committed artifact would fail if it "
                "were violated (UNGUARDED)"))
    for dep in ctx.config.get("required_deliverables", []):
        if ctx.resolve(dep).exists():
            info.append(f"required deliverable present: {dep}")
        else:
            findings.append(finding(
                "MISSING_DELIVERABLE", dep,
                "required deliverable is absent from the working tree"))
    # ledger coverage: every mechanized class must be fed or waived
    waivers = {w["class_id"]: w.get("reason", "")
               for w in ctx.config.get("waivers", [])}
    for cls in ledger.get("classes", []):
        cid = cls["id"]
        if cls.get("detection") != "mechanized":
            answer = (ctx.config.get("checklist_answers") or {}).get(cid)
            info.append(
                f"ledger class {cid}: checklist-detected; "
                + (f"answer on file: {answer}" if answer
                   else "NO checklist answer in config (adversarial "
                        "pre-review must answer it in the handoff)"))
            continue
        check = cls.get("pre_review_check")
        if cid in waivers:
            info.append(
                f"ledger class {cid}: WAIVED - {waivers[cid]}")
        elif check and config_feeds_check(ctx, check, cid):
            info.append(
                f"ledger class {cid}: covered by configured check {check}")
        else:
            findings.append(finding(
                "SPEC_TEST_GAP", cid,
                f"mechanized ledger class has no covering input in the "
                f"config (check {check}) and no explicit waiver"))
    return check_result("claims-coverage", findings, info)


# ---------------------------------------------------------------------------
# External checks (run last; a fuzz-panel BLOCK is a pre-review BLOCK)
# ---------------------------------------------------------------------------

def run_external_check(ctx: Context, entry: dict) -> dict:
    name = entry.get("name", "<external>")
    findings, info = [], []
    cmd = list(entry["cmd"])
    cwd = ctx.resolve(entry.get("cwd", "."))
    timeout = entry.get("timeout", ctx.config.get("timeout", DEFAULT_TIMEOUT))
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ToolError(f"external check {name}: timed out after {timeout}s")
    except OSError as exc:
        raise ToolError(f"external check {name}: cannot run {cmd[0]}: {exc}")
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode == 0:
        info.append(f"{name}: CLEAR (exit 0). {output[-400:]}")
    elif proc.returncode == 1:
        findings.append(finding(
            entry.get("ledger_class", "EXTERNAL_CHECK"), name,
            "external check reports BLOCK (exit 1); an external BLOCK is a "
            f"pre-review BLOCK. Output tail: {output[-600:]}"))
    else:
        raise ToolError(
            f"external check {name}: tool error (exit {proc.returncode}): "
            f"{output[-600:]}")
    return check_result(name, findings, info)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

RUNNERS = {
    "trace-provenance": run_trace_provenance,
    "single-model": run_single_model,
    "red-reason": run_red_reason,
    "claims-coverage": run_claims_coverage,
}


def ledger_coverage_rows(ctx: Context, results: list) -> list:
    try:
        ledger = load_ledger(ctx)
    except ToolError:
        return []
    ran = {r["check"]: r for r in results}
    rows = []
    for cls in ledger.get("classes", []):
        cid, check = cls["id"], cls.get("pre_review_check")
        if cls.get("detection") != "mechanized":
            rows.append((cid, "checklist", "n/a (adversarial pre-review)"))
            continue
        if check in ran:
            hits = [f for f in ran[check]["findings"] if f["class"] == cid]
            rows.append((cid, check,
                         f"BLOCK ({len(hits)} finding(s))" if hits
                         else "clear this run"))
        else:
            rows.append((cid, check, "check not run (--only)"))
    return rows


def write_report(path: Path, ctx: Context, results: list, verdict: str):
    lines = []
    task = ctx.config.get("task", "<unnamed task>")
    lines.append(f"# pre_review report - {task}")
    lines.append("")
    lines.append(f"- config: `{ctx.config_path.name}`")
    lines.append(f"- checks run: {', '.join(r['check'] for r in results)}")
    lines.append("")
    lines.append("## Per-check verdicts")
    lines.append("")
    lines.append("| check | verdict | findings |")
    lines.append("|---|---|---|")
    for r in results:
        lines.append(f"| {r['check']} | {r['verdict']} | "
                     f"{len(r['findings'])} |")
    lines.append("")
    lines.append("## Ledger class coverage")
    lines.append("")
    lines.append("| class | mechanism | status this run |")
    lines.append("|---|---|---|")
    for cid, mech, status in ledger_coverage_rows(ctx, results):
        lines.append(f"| {cid} | {mech} | {status} |")
    lines.append("")
    for r in results:
        lines.append(f"## {r['check']} - {r['verdict']}")
        lines.append("")
        if r["findings"]:
            lines.append("### Findings (blocking)")
            lines.append("")
            for f in r["findings"]:
                lines.append(f"- **{f['class']}** `{f['subject']}`: "
                             f"{f['detail']}")
            lines.append("")
        if r["info"]:
            lines.append("### Notes")
            lines.append("")
            for note in r["info"]:
                lines.append(f"- {note}")
            lines.append("")
    lines.append("---")
    lines.append("")
    banner = ("**VERDICT: CLEAR** - no blocking findings"
              if verdict == "CLEAR" else
              "**VERDICT: BLOCK** - blocking findings above; the handoff "
              "must not proceed")
    lines.append(banner)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pre_review",
        description="mechanized adversarial pre-review (pipeline v2)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json", dest="json_out")
    parser.add_argument("--only", action="append",
                        help="run only the named check (repeatable; built-in "
                             "or declared external check names)")
    args = parser.parse_args(argv)
    try:
        ctx = Context(Path(args.config))
        externals = ctx.config.get("external_checks", [])
        known = set(CHECK_NAMES) | {e.get("name") for e in externals}
        selected = args.only or sorted(known)
        unknown = [s for s in selected if s not in known]
        if unknown:
            raise ToolError(f"--only names unknown check(s): {unknown}")
        results = [RUNNERS[name](ctx) for name in CHECK_NAMES
                   if name in selected]
        # external checks always run AFTER the built-ins, in declared order
        results += [run_external_check(ctx, e) for e in externals
                    if e.get("name") in selected]
        verdict = ("BLOCK" if any(r["verdict"] == "BLOCK" for r in results)
                   else "CLEAR")
        write_report(Path(args.report), ctx, results, verdict)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(
                {"task": ctx.config.get("task"), "verdict": verdict,
                 "results": results}, indent=1, sort_keys=True) + "\n")
        print(f"pre_review: {verdict} "
              f"({sum(len(r['findings']) for r in results)} finding(s); "
              f"report: {args.report})")
        return EXIT_CLEAR if verdict == "CLEAR" else EXIT_BLOCK
    except ToolError as exc:
        print(f"pre_review: tool/config error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
