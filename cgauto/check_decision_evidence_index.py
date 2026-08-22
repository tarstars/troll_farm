#!/usr/bin/env python3
"""Validate canonical decision/evidence records and deterministic projections."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cgauto.build_decision_evidence_index import load_records, expected_outputs
from cgauto.evidence_git import (
    COMMIT_RE, GitLookupError, commit_resolves, is_ancestor, read_blob, ref_exists,
)
from cgauto.evidence_hypotheses import HypothesisError, load_hypotheses, validate_hypothesis

ALLOWED_STATUS = {"proposed","accepted","authorized","closed","invalidated","diagnosis","void-premise","superseded","declined"}
ALLOWED_ACCEPTANCE = {"proposed", "accepted"}
ALLOWED_STRENGTH = {
    "mechanics_proof","panel_causal","arena_measured","observational_audit",
    "accounting_model","public_source_statement","inference_or_hypothesis",
    "contested","overturned",
}
ALLOWED_RELATIONS = {
    "supports","contradicts","corrects","supersedes","narrows","opens","closes",
    "constrains","does_not_close","calibrates","calibrated_by",
}
PILOT_IDS = {
    "D30","D101","D161","D169","D172a","D175a","H1","D176a",
    "OWNER-GOAL-20260730","OWNER-ARENA-20260730","H7",
}
REQUIRED = {
    "schema_version","id","title","kind","status","decision_date","question","scope",
    "conclusion","primary_evidence_strength","cost","attempts","decisive_claims",
    "textual_evidence","does_not_prove","limitations","relations",
    "reopening_conditions","discussions","constraint_projection","acceptance",
}
LINE_RE = re.compile(r"^lines (\d+)-(\d+)$")
NUM_RE = re.compile(r"(?<![A-Za-z])[-+−±]?\d+(?:\.\d+)?(?:/\d+)?%?")
INTEGRATION_REF = "refs/remotes/origin/main"
INTEGRATION_REF_FALLBACK = "refs/heads/main"

def integration_ref(repo: Path) -> str | None:
    """The ref an unmerged pin is measured against, preferring the tracked
    remote but falling back to a local `main` (single-branch clones, agent
    branches checked out without a remote-tracking ref)."""
    if ref_exists(repo, INTEGRATION_REF):
        return INTEGRATION_REF
    if ref_exists(repo, INTEGRATION_REF_FALLBACK):
        return INTEGRATION_REF_FALLBACK
    return None

class ValidationError(ValueError):
    pass

def safe_path(repo: Path, value: str) -> Path:
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValidationError(f"unsafe repository path: {value}")
    full = (repo / p).resolve()
    if repo.resolve() not in full.parents and full != repo.resolve():
        raise ValidationError(f"path escapes repository: {value}")
    if not full.exists():
        raise ValidationError(f"missing evidence path: {value}")
    return full

def resolve_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValidationError(f"invalid JSON pointer: {pointer}")
    cur = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            try:
                cur = cur[int(token)]
            except (ValueError, IndexError):
                raise ValidationError(f"unresolved JSON pointer: {pointer}") from None
        elif isinstance(cur, dict) and token in cur:
            cur = cur[token]
        else:
            raise ValidationError(f"unresolved JSON pointer: {pointer}")
    return cur

def validate_source(
    repo: Path, source: dict[str, Any], context: str, warnings: list[str] | None = None
) -> Any:
    if not isinstance(source, dict) or not source.get("path"):
        raise ValidationError(f"{context}: source.path required")
    rel = source["path"]
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValidationError(f"unsafe repository path: {rel}")
    commit = source.get("commit")
    if not commit or not COMMIT_RE.match(commit):
        raise ValidationError(f"{context}: source.commit must be a 40-character sha")
    if not commit_resolves(repo, commit):
        raise ValidationError(f"{context}: commit {commit[:12]} does not resolve")
    try:
        text = read_blob(repo, commit, rel)
    except GitLookupError as exc:
        raise ValidationError(f"{context}: {exc}") from None
    locator = source.get("locator")
    pointer = source.get("json_pointer")
    if bool(locator) == bool(pointer):
        raise ValidationError(f"{context}: exactly one of locator/json_pointer required")
    if locator:
        m = LINE_RE.match(locator)
        if not m:
            raise ValidationError(f"{context}: locator must be 'lines N-M'")
        a, b = map(int, m.groups())
        if a < 1 or b < a:
            raise ValidationError(f"{context}: invalid line range")
        lines = text.splitlines()
        if b > len(lines):
            raise ValidationError(f"{context}: line range exceeds {rel} ({len(lines)})")
        result = "\n".join(lines[a - 1:b])
    else:
        if Path(rel).suffix.lower() != ".json":
            raise ValidationError(f"{context}: JSON pointer requires .json source")
        result = resolve_pointer(json.loads(text), pointer)
    if warnings is not None:
        ref = integration_ref(repo)
        if ref is not None and not is_ancestor(repo, commit, ref):
            warnings.append(f"{context}: commit {commit[:12]} pending integration into main")
        quote = source.get("quote")
        if quote:
            current = repo / rel
            if not current.exists() or quote not in current.read_text(
                encoding="utf-8", errors="replace"
            ):
                warnings.append(f"{context}: quote drift — evidence no longer in current {rel}")
    return result

def numeric_tokens(text: str) -> list[str]:
    return NUM_RE.findall(text)

def require_excerpt_tokens(excerpt: Any, tokens: list[str], context: str) -> None:
    if not isinstance(excerpt, str):
        return
    missing = [token for token in dict.fromkeys(tokens) if token not in excerpt]
    if missing:
        raise ValidationError(f"{context}: cited excerpt omits content tokens {missing}")

def require_constraints_identity(source: dict[str, Any], excerpt: Any, rid: str, context: str) -> None:
    if source.get("path") != "docs/CONSTRAINTS.md":
        return
    if not isinstance(excerpt, str) or rid not in excerpt:
        raise ValidationError(f"{context}: CONSTRAINTS excerpt does not identify {rid}")

def validate_record(
    repo: Path, record: dict[str, Any], ids: set[str], warnings: list[str] | None = None
) -> None:
    missing = sorted(REQUIRED - record.keys())
    if missing:
        raise ValidationError(f"{record.get('id','<unknown>')}: missing fields {missing}")
    rid = record["id"]
    if record["schema_version"] != 2:
        raise ValidationError(f"{rid}: schema_version must be 2")
    if record["status"] not in ALLOWED_STATUS:
        raise ValidationError(f"{rid}: invalid status")
    if record["primary_evidence_strength"] not in ALLOWED_STRENGTH:
        raise ValidationError(f"{rid}: invalid primary evidence strength")
    for key in ("question","scope","conclusion"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValidationError(f"{rid}: {key} required")
    for key in ("does_not_prove","limitations","reopening_conditions","attempts"):
        if not isinstance(record[key], list) or not record[key]:
            raise ValidationError(f"{rid}: non-empty {key} required")
    cost = record["cost"]
    if not isinstance(cost, dict) or not cost.get("class") or not cost.get("actual"):
        raise ValidationError(f"{rid}: cost.class and cost.actual required")
    if record["acceptance"].get("state") not in ALLOWED_ACCEPTANCE:
        raise ValidationError(f"{rid}: invalid acceptance state")
    if record["status"] == "void-premise":
        pf = record.get("premise_failure")
        if not isinstance(pf, dict) or not pf.get("false_premise") or not pf.get("refutation"):
            raise ValidationError(f"{rid}: void-premise requires premise_failure")
        excerpt = validate_source(repo, pf.get("source", {}), f"{rid}.premise_failure", warnings)
        require_constraints_identity(pf.get("source", {}), excerpt, rid, f"{rid}.premise_failure")
    elif "premise_failure" in record and record["premise_failure"]:
        raise ValidationError(f"{rid}: premise_failure only valid for void-premise")
    has_arena = False
    for i, c in enumerate(record["decisive_claims"]):
        ctx = f"{rid}.decisive_claims[{i}]"
        for key in ("name","display","population","source","evidence_strength","binding"):
            if key not in c or c[key] in ("", None):
                raise ValidationError(f"{ctx}: {key} required")
        if c["evidence_strength"] not in ALLOWED_STRENGTH:
            raise ValidationError(f"{ctx}: invalid evidence strength")
        has_arena |= c["evidence_strength"] == "arena_measured"
        resolved = validate_source(repo, c["source"], ctx, warnings)
        if c["source"].get("locator"):
            require_excerpt_tokens(resolved, numeric_tokens(c["display"]), ctx)
            require_constraints_identity(c["source"], resolved, rid, ctx)
        if "expected_value" in c and resolved != c["expected_value"]:
            raise ValidationError(f"{ctx}: JSON pointer value differs from expected_value")
        other = c.get("compared_population")
        if other and other != c["population"]:
            mode = c.get("population_compatibility")
            if mode not in {"invalid_disclosed","transformed"}:
                raise ValidationError(f"{ctx}: incompatible populations not disclosed")
            if mode == "invalid_disclosed" and not c.get("incompatibility_reason"):
                raise ValidationError(f"{ctx}: invalid population comparison needs reason")
            if mode == "transformed" and not c.get("population_transform"):
                raise ValidationError(f"{ctx}: transformed comparison needs transform")
    if record.get("claims_ladder_effect") and not has_arena and not record.get("projection_label"):
        raise ValidationError(f"{rid}: ladder effect requires arena_measured or projection_label")
    for i, e in enumerate(record["textual_evidence"]):
        if not e.get("claim"):
            raise ValidationError(f"{rid}.textual_evidence[{i}]: claim required")
        ctx = f"{rid}.textual_evidence[{i}]"
        excerpt = validate_source(repo, e.get("source", {}), ctx, warnings)
        if e.get("source", {}).get("locator"):
            require_excerpt_tokens(excerpt, numeric_tokens(e["claim"]), ctx)
            require_constraints_identity(e.get("source", {}), excerpt, rid, ctx)
    for rel in record["relations"]:
        if rel.get("type") not in ALLOWED_RELATIONS:
            raise ValidationError(f"{rid}: invalid relation type {rel.get('type')}")
        target = rel.get("target","")
        if not target.startswith("external:") and target not in ids:
            raise ValidationError(f"{rid}: unresolved relation target {target}")
    for did in record["discussions"]:
        safe_path(repo, f"docs/evidence/discussions/{did}.md")
    cp = record["constraint_projection"]
    if not cp.get("section") or not cp.get("bullet"):
        raise ValidationError(f"{rid}: constraint projection section/bullet required")
    cp_excerpt = validate_source(repo, cp.get("source", {}), f"{rid}.constraint_projection", warnings)
    bullet = cp["bullet"]
    binding_tokens: list[str] = []
    for c in record["decisive_claims"]:
        if not c.get("binding", True):
            continue
        for token in numeric_tokens(c["display"]):
            binding_tokens.append(token)
            if token not in bullet:
                raise ValidationError(f"{rid}: projection omits decisive numeric token {token}")
    if cp.get("source", {}).get("locator"):
        require_excerpt_tokens(cp_excerpt, binding_tokens, f"{rid}.constraint_projection")
        require_constraints_identity(cp.get("source", {}), cp_excerpt, rid, f"{rid}.constraint_projection")
    if rid == "D176a":
        outcomes = record.get("outcomes", {})
        if outcomes != {"mechanism":"successful","value":"immaterial","protocol_quality":"gate_design_error"}:
            raise ValidationError("D176a must preserve mechanism/value/gate-design distinctions")

def validate_repository(
    repo: Path, require_pilot: bool = True, check_generated: bool = True
) -> tuple[list[dict[str, Any]], list[str]]:
    records = load_records(repo)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValidationError("duplicate record id")
    idset = set(ids)
    if require_pilot and idset != PILOT_IDS:
        raise ValidationError(f"pilot ids mismatch: missing={sorted(PILOT_IDS-idset)} extra={sorted(idset-PILOT_IDS)}")
    warnings: list[str] = []
    for r in records:
        validate_record(repo, r, idset, warnings)
    hypotheses = load_hypotheses(repo)
    hyp_ids = [h["id"] for h in hypotheses]
    if len(hyp_ids) != len(set(hyp_ids)):
        raise ValidationError("duplicate hypothesis id")
    for h in hypotheses:
        try:
            validate_hypothesis(h, idset, repo)
        except HypothesisError as exc:
            raise ValidationError(str(exc)) from None
    if check_generated:
        expected = expected_outputs(records, hypotheses)
        for name, content in expected.items():
            path = repo / "docs/evidence/generated" / name
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise ValidationError(f"generated output differs: {name}")
        manifest_path = repo / "docs/evidence/generated/manifest.json"
        if not manifest_path.exists():
            raise ValidationError("missing generated manifest")
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("record_count") != len(records):
            raise ValidationError("manifest record_count mismatch")
        if manifest.get("void_premise_count") != sum(r["status"]=="void-premise" for r in records):
            raise ValidationError("manifest void count mismatch")
        if manifest.get("closure_count_excluding_void") != sum(r["status"] in {"closed","invalidated"} for r in records):
            raise ValidationError("manifest closure count mismatch")
        if manifest.get("hypothesis_count") != len(hypotheses):
            raise ValidationError("manifest hypothesis_count mismatch")
    return records, warnings

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--no-generated-check", action="store_true")
    p.add_argument("--allow-subset", action="store_true")
    args = p.parse_args()
    records, warnings = validate_repository(
        args.repo_root,
        require_pilot=not args.allow_subset,
        check_generated=not args.no_generated_check,
    )
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(json.dumps({
        "records": len(records),
        "warnings": len(warnings),
        "closures_excluding_void": sum(r["status"] in {"closed","invalidated"} for r in records),
        "void_premise": sum(r["status"]=="void-premise" for r in records),
        "status": "ok",
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
