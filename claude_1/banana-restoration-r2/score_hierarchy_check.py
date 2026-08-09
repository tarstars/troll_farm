#!/usr/bin/env python3
"""Re-runnable checks for the score-hierarchy audit (item M2).

This module implements the *mechanical* parts of the audit method described in
``score-hierarchy-audit-method-2026-08-10.md``.  It deliberately implements only
what can be made sound with the Python 3.12 standard library and no Rust parser:

  1. ``identity``  -- artefact pinning (SHA-256) and subject/companion divergence.
  2. ``census``    -- score-site *drift detection* against a frozen ledger.
                      This is a change detector, NOT a discovery tool: it cannot
                      prove the inventory complete.  See the method packet, S2.
  3. ``bindings``  -- call-site enumeration for a named inherent function, with a
                      mechanically checked soundness side-condition (no bare uses
                      of the identifier, i.e. no function-pointer aliasing).
  4. ``ranges``    -- interval arithmetic over a *human-supplied, cited* range
                      model, plus clamp-deadness proofs.  The tool does the
                      arithmetic; the ledger supplies the input bounds and the
                      file:line citation and proof method for each one.

What is NOT implemented, because it cannot be made sound here: deriving input
bounds from the Rust source, control-flow reachability, co-reachability of two
candidates in one candidate set.  Those are manual procedures in the method
packet (S2.1, S3.1, S4.4).  Do not add a regex that pretends otherwise.

Usage:
    python3 score_hierarchy_check.py --ledger score-hierarchy-ledger.json \\
        [--subject PATH | --git-ref REF:PATH] [--repo DIR] [--json]

Exit status: 0 = every enabled check passed; 1 = drift or failure; 2 = usage.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 0. Source acquisition and pinning
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_from_git(repo: Path, ref_path: str) -> bytes:
    """Read a blob as ``git show <ref>:<path>``.  Read-only."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", ref_path],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise FileNotFoundError(
            f"git show {ref_path} failed in {repo}: {proc.stderr.decode(errors='replace').strip()}"
        )
    return proc.stdout


# ---------------------------------------------------------------------------
# 1. Lexical preprocessing: blank comments and literal contents in place
# ---------------------------------------------------------------------------


def blank_comments_and_strings(src: str) -> str:
    """Return ``src`` with comment bodies and string/char literal bodies replaced
    by spaces, preserving length and every newline (so offsets and line numbers
    are unchanged).

    Handles: ``//`` line comments, ``/* */`` block comments (nested, per Rust),
    ``"..."`` with backslash escapes, raw strings ``r"..."`` / ``r#"..."#``,
    byte-string prefixes ``b`` / ``br``, and char literals -- distinguishing
    ``'a'`` from a lifetime ``'a`` by lookahead.

    This is lexical, not syntactic.  It is sound for the purpose it is used for
    (removing text that must not be searched); it does not parse Rust.
    """
    out = list(src)
    i = 0
    n = len(src)

    def blank(start: int, end: int) -> None:
        for k in range(start, min(end, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = src[i]
        # line comment
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            j = n if j == -1 else j
            blank(i + 2, j)
            i = j
            continue
        # block comment (nested)
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            depth = 1
            j = i + 2
            while j < n and depth:
                if src.startswith("/*", j):
                    depth += 1
                    j += 2
                elif src.startswith("*/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            blank(i + 2, j - 2 if depth == 0 else n)
            i = j
            continue
        # raw string, possibly byte-prefixed
        m = re.match(r'(?:b?r)(#*)"', src[i : i + 8])
        if m and (i == 0 or not (src[i - 1].isalnum() or src[i - 1] == "_")):
            hashes = m.group(1)
            body = i + m.end()
            close = src.find('"' + hashes, body)
            end = n if close == -1 else close
            blank(body, end)
            i = (end + 1 + len(hashes)) if close != -1 else n
            continue
        # ordinary / byte string
        if c == '"':
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == '"':
                    break
                j += 1
            blank(i + 1, j)
            i = min(j + 1, n)
            continue
        # char literal vs lifetime
        if c == "'":
            if i + 1 < n and src[i + 1] == "\\":
                j = i + 2
                while j < n and src[j] != "'":
                    j += 1
                blank(i + 1, j)
                i = min(j + 1, n)
                continue
            if i + 2 < n and src[i + 2] == "'":
                blank(i + 1, i + 2)
                i = i + 3
                continue
            i += 1  # lifetime, leave alone
            continue
        i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# 2. Score-site census (drift detector)
# ---------------------------------------------------------------------------

SCORE_SITE_RE = re.compile(r"(?<![A-Za-z0-9_])score\s*(:|\+=|-=|=(?!=))")


@dataclasses.dataclass(frozen=True)
class ScoreSite:
    line: int
    op: str
    text: str  # whitespace-normalised, comment/string-blanked source line

    def fingerprint(self) -> str:
        return sha256_bytes(f"{self.op}|{self.text}".encode())[:16]

    def as_dict(self) -> dict[str, Any]:
        return {
            "line": self.line,
            "op": self.op,
            "text": self.text,
            "fingerprint": self.fingerprint(),
        }


def census(src: str) -> list[ScoreSite]:
    """Enumerate textual score-assignment sites.

    SOUNDNESS: this is an *under*-approximation of the true set of score-producing
    expressions.  A score can be produced without the token ``score`` appearing on
    the line (e.g. by mutating a ``Candidate`` through a helper).  Its only sound
    use is comparison against a frozen, manually ratified ledger: an empty diff
    means nothing this pattern can see has moved.  A non-empty diff means the
    manual inventory (method packet S2.1) must be redone for the listed lines.
    """
    clean = blank_comments_and_strings(src)
    lines = clean.splitlines()
    raw_lines = src.splitlines()
    sites: list[ScoreSite] = []
    for idx, line in enumerate(lines, start=1):
        for m in SCORE_SITE_RE.finditer(line):
            op = m.group(1)
            text = re.sub(r"\s+", "", raw_lines[idx - 1])
            sites.append(ScoreSite(line=idx, op=op, text=text))
    return sites


def census_diff(
    current: list[ScoreSite], frozen: list[dict[str, Any]]
) -> dict[str, list[Any]]:
    """Compare a census against a frozen ledger by fingerprint (line-insensitive)
    and by line (to report pure moves)."""
    cur_by_fp: dict[str, list[ScoreSite]] = {}
    for s in current:
        cur_by_fp.setdefault(s.fingerprint(), []).append(s)
    frz_by_fp: dict[str, list[dict[str, Any]]] = {}
    for f in frozen:
        frz_by_fp.setdefault(f["fingerprint"], []).append(f)

    added, removed, moved = [], [], []
    for fp, sites in cur_by_fp.items():
        if fp not in frz_by_fp:
            added.extend(s.as_dict() for s in sites)
        else:
            frozen_lines = sorted(f["line"] for f in frz_by_fp[fp])
            current_lines = sorted(s.line for s in sites)
            if len(frozen_lines) != len(current_lines):
                if len(current_lines) > len(frozen_lines):
                    added.extend(
                        s.as_dict() for s in sites[: len(current_lines) - len(frozen_lines)]
                    )
                else:
                    removed.extend(frz_by_fp[fp][: len(frozen_lines) - len(current_lines)])
            elif frozen_lines != current_lines:
                moved.append({"fingerprint": fp, "was": frozen_lines, "now": current_lines})
    for fp, entries in frz_by_fp.items():
        if fp not in cur_by_fp:
            removed.extend(entries)
    return {"added": added, "removed": removed, "moved": moved}


# ---------------------------------------------------------------------------
# 3. Call-site binding enumeration
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class CallSite:
    line: int
    args: list[str]
    literal_args: dict[int, str]


@dataclasses.dataclass
class BindingReport:
    name: str
    definitions: list[int]
    calls: list[CallSite]
    bare_uses: list[int]

    @property
    def sound(self) -> bool:
        """The enumeration is sound only if the identifier never appears except as
        a definition or immediately before ``(``.  A bare use means the function
        may be taken as a value (function pointer / closure capture), in which
        case textual call sites do not bound the real call set."""
        return not self.bare_uses

    @property
    def status(self) -> str:
        if not self.sound:
            return "INCONCLUSIVE"
        return "OK"

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "definitions": self.definitions,
            "calls": [
                {"line": c.line, "args": c.args, "literal_args": c.literal_args}
                for c in self.calls
            ],
            "bare_uses": self.bare_uses,
            "status": self.status,
        }


NUMERIC_LITERAL_RE = re.compile(
    r"^[+-]?(?:\d[\d_]*\.?[\d_]*(?:[eE][+-]?\d+)?|\.\d[\d_]*)(?:f32|f64|i32|i64|u32|u64|usize|isize)?$"
)


def _split_args(src: str, open_paren: int) -> tuple[list[str], int]:
    """Split the argument list of a call whose ``(`` is at ``open_paren``.

    Balances ``()``, ``[]``, ``{}`` and ``<>`` is deliberately NOT balanced (Rust
    turbofish is rare here and ``<`` is ambiguous); commas inside angle brackets
    would therefore over-split.  The ledger records the arity it expects, so an
    arity mismatch surfaces as a failure rather than a silent wrong answer.
    """
    depth = 0
    args: list[str] = []
    cur: list[str] = []
    i = open_paren
    n = len(src)
    while i < n:
        c = src[i]
        if c in "([{":
            depth += 1
            if depth == 1:
                i += 1
                continue
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                arg = "".join(cur).strip()
                if arg:
                    args.append(arg)
                return args, i
        if depth == 1 and c == ",":
            args.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    raise ValueError("unbalanced call parentheses")


def call_sites(src: str, name: str) -> BindingReport:
    """Enumerate definitions, calls and bare uses of an inherent function ``name``.

    Side conditions (stated, not proved by this tool): no macro-generated calls,
    no trait-object dispatch to this name, no ``use ... as name`` renaming.  The
    subject is a single-file bot with inherent impls only; the method packet S3.1
    tells the auditor how to re-confirm this by hand when the code moves.
    """
    clean = blank_comments_and_strings(src)
    line_starts = [0]
    for m in re.finditer(r"\n", clean):
        line_starts.append(m.end())

    def line_of(off: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    definitions: list[int] = []
    calls: list[CallSite] = []
    bare: list[int] = []

    for m in re.finditer(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", clean):
        start, end = m.start(), m.end()
        before = clean[max(0, start - 40) : start]
        if re.search(r"\bfn\s+$", before):
            definitions.append(line_of(start))
            continue
        rest = clean[end:]
        stripped = rest.lstrip()
        if stripped.startswith("("):
            open_paren = end + (len(rest) - len(stripped))
            try:
                args, _ = _split_args(clean, open_paren)
            except ValueError:
                bare.append(line_of(start))
                continue
            literal = {
                i: a for i, a in enumerate(args) if NUMERIC_LITERAL_RE.match(a)
            }
            calls.append(CallSite(line=line_of(start), args=args, literal_args=literal))
        else:
            bare.append(line_of(start))

    return BindingReport(
        name=name, definitions=definitions, calls=calls, bare_uses=bare
    )


# ---------------------------------------------------------------------------
# 4. Interval arithmetic over a cited range model
# ---------------------------------------------------------------------------


class IntervalError(ValueError):
    pass


@dataclasses.dataclass(frozen=True)
class Interval:
    """A possibly-open real interval.  Infinite endpoints are always open."""

    lo: float
    hi: float
    lo_closed: bool = True
    hi_closed: bool = True

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise IntervalError(f"empty interval [{self.lo}, {self.hi}]")
        if math.isinf(self.lo):
            object.__setattr__(self, "lo_closed", False)
        if math.isinf(self.hi):
            object.__setattr__(self, "hi_closed", False)

    # -- construction --------------------------------------------------
    @staticmethod
    def point(x: float) -> "Interval":
        return Interval(x, x, True, True)

    @staticmethod
    def parse(spec: Any) -> "Interval":
        """Parse ``"(0, 2400]"``, ``"[2, inf)"``, ``[lo, hi]`` or a bare number."""
        if isinstance(spec, (int, float)):
            return Interval.point(float(spec))
        if isinstance(spec, list) and len(spec) == 2:
            return Interval(float(spec[0]), float(spec[1]))
        if not isinstance(spec, str):
            raise IntervalError(f"unparseable interval {spec!r}")
        s = spec.strip()
        m = re.match(r"^([\[\(])\s*([^,]+)\s*,\s*([^\]\)]+)\s*([\]\)])$", s)
        if not m:
            raise IntervalError(f"unparseable interval {spec!r}")

        def num(t: str) -> float:
            t = t.strip().replace("_", "")
            if t in ("inf", "+inf", "infinity"):
                return math.inf
            if t in ("-inf", "-infinity"):
                return -math.inf
            return float(t)

        return Interval(num(m.group(2)), num(m.group(3)), m.group(1) == "[", m.group(4) == "]")

    def __str__(self) -> str:
        def f(x: float) -> str:
            if math.isinf(x):
                return "inf" if x > 0 else "-inf"
            return f"{x:.12g}"

        return (
            f"{'[' if self.lo_closed else '('}{f(self.lo)}, "
            f"{f(self.hi)}{']' if self.hi_closed else ')'}"
        )

    def approx_equal(self, other: "Interval", tol: float = 1e-9) -> bool:
        def close(a: float, b: float) -> bool:
            if math.isinf(a) or math.isinf(b):
                return a == b
            return abs(a - b) <= tol * max(1.0, abs(a), abs(b))

        return (
            close(self.lo, other.lo)
            and close(self.hi, other.hi)
            and self.lo_closed == other.lo_closed
            and self.hi_closed == other.hi_closed
        )

    # -- arithmetic ----------------------------------------------------
    def __add__(self, o: "Interval") -> "Interval":
        return Interval(
            self.lo + o.lo,
            self.hi + o.hi,
            self.lo_closed and o.lo_closed,
            self.hi_closed and o.hi_closed,
        )

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo, self.hi_closed, self.lo_closed)

    def __sub__(self, o: "Interval") -> "Interval":
        return self + (-o)

    def __mul__(self, o: "Interval") -> "Interval":
        corners = []
        for a, ac in ((self.lo, self.lo_closed), (self.hi, self.hi_closed)):
            for b, bc in ((o.lo, o.lo_closed), (o.hi, o.hi_closed)):
                if math.isinf(a) and b == 0 or math.isinf(b) and a == 0:
                    raise IntervalError("0 * inf in interval product; refine the model")
                corners.append((a * b, ac and bc))
        lo = min(c[0] for c in corners)
        hi = max(c[0] for c in corners)
        lo_closed = all(c[1] for c in corners if c[0] == lo)
        hi_closed = all(c[1] for c in corners if c[0] == hi)
        return Interval(lo, hi, lo_closed, hi_closed)

    def reciprocal(self) -> "Interval":
        if self.lo <= 0 <= self.hi:
            raise IntervalError(f"reciprocal of {self} spans 0; refine the model")
        lo = 0.0 if math.isinf(self.hi) else 1.0 / self.hi
        hi = 0.0 if math.isinf(self.lo) else 1.0 / self.lo
        lo_closed = False if math.isinf(self.hi) else self.hi_closed
        hi_closed = False if math.isinf(self.lo) else self.lo_closed
        return Interval(lo, hi, lo_closed, hi_closed)

    def __truediv__(self, o: "Interval") -> "Interval":
        return self * o.reciprocal()

    def imax(self, o: "Interval") -> "Interval":
        """Range of ``max(x, y)`` for independent ``x in self``, ``y in o``.

        Also serves Rust's ``a.max(k)`` when ``o`` is a point interval.
        """
        if self.lo > o.lo:
            lo, lo_closed = self.lo, self.lo_closed
        elif o.lo > self.lo:
            lo, lo_closed = o.lo, o.lo_closed
        else:
            lo, lo_closed = self.lo, (self.lo_closed and o.lo_closed)
        if self.hi > o.hi:
            hi, hi_closed = self.hi, self.hi_closed
        elif o.hi > self.hi:
            hi, hi_closed = o.hi, o.hi_closed
        else:
            hi, hi_closed = self.hi, (self.hi_closed or o.hi_closed)
        return Interval(lo, hi, lo_closed, hi_closed)

    def imin(self, o: "Interval") -> "Interval":
        return (-((-self).imax(-o)))

    def clamp_low(self, k: float) -> "Interval":
        """Rust ``.max(k)``."""
        return self.imax(Interval.point(k))

    def clamp_high(self, k: float) -> "Interval":
        """Rust ``.min(k)``."""
        return self.imin(Interval.point(k))

    def clamp_low_is_dead(self, k: float) -> bool:
        """``.max(k)`` is provably a no-op iff every attainable value is >= k."""
        return self.lo >= k

    def clamp_high_is_dead(self, k: float) -> bool:
        return self.hi <= k


_OPS = {"+", "-", "*", "/", "max", "min"}


def _vars_in(expr: Any) -> list[str]:
    if isinstance(expr, str):
        return [expr]
    if isinstance(expr, (int, float)):
        return []
    if isinstance(expr, list) and expr:
        out: list[str] = []
        for sub in expr[1:]:
            out.extend(_vars_in(sub))
        return out
    raise IntervalError(f"malformed expression node {expr!r}")


def eval_expr(expr: Any, env: dict[str, Interval]) -> Interval:
    """Evaluate a prefix-list expression over intervals.

    ``["+", a, b]``, ``["-", a, b]``, ``["*", a, b]``, ``["/", a, b]``,
    ``["max", a, k]`` (Rust ``a.max(k)``), ``["min", a, k]``.  Leaves are variable
    names (looked up in ``env``) or numeric constants.
    """
    if isinstance(expr, (int, float)):
        return Interval.point(float(expr))
    if isinstance(expr, str):
        if expr not in env:
            raise IntervalError(f"unbound variable {expr!r}")
        return env[expr]
    if not isinstance(expr, list) or not expr or expr[0] not in _OPS:
        raise IntervalError(f"malformed expression {expr!r}")
    op = expr[0]
    if op in ("max", "min"):
        if len(expr) != 3:
            raise IntervalError(f"{op} takes exactly 2 operands: {expr!r}")
        a = eval_expr(expr[1], env)
        b = eval_expr(expr[2], env)
        return a.imax(b) if op == "max" else a.imin(b)
    if len(expr) < 3:
        raise IntervalError(f"{op} takes at least 2 operands: {expr!r}")
    acc = eval_expr(expr[1], env)
    for sub in expr[2:]:
        rhs = eval_expr(sub, env)
        acc = {"+": Interval.__add__, "-": Interval.__sub__,
               "*": Interval.__mul__, "/": Interval.__truediv__}[op](acc, rhs)
    return acc


def substitute(expr: Any, defs: dict[str, Any]) -> Any:
    """Inline ``derived`` definitions so that precision accounting (repeated-variable
    detection) is performed on the fully expanded, leaf-variable expression."""
    if isinstance(expr, str) and expr in defs:
        return substitute(defs[expr], defs)
    if isinstance(expr, list):
        return [expr[0]] + [substitute(sub, defs) for sub in expr[1:]]
    return expr


def range_model_report(model: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one ledger range model and compare with its claimed interval."""
    env = {
        name: Interval.parse(spec["range"])
        for name, spec in model.get("inputs", {}).items()
    }
    defs = {d["name"]: d["expr"] for d in model.get("derived", [])}
    model = dict(model)
    model["expr"] = substitute(model["expr"], defs)
    model["clamps"] = [
        {**c, "operand": substitute(c["operand"], defs)} for c in model.get("clamps", [])
    ]
    used = _vars_in(model["expr"])
    exact = len(used) == len(set(used))
    result = eval_expr(model["expr"], env)
    claimed = Interval.parse(model["attainable"]) if "attainable" in model else None
    ok = claimed is None or result.approx_equal(claimed)
    out: dict[str, Any] = {
        "id": model.get("id"),
        "site": model.get("site"),
        "computed": str(result),
        "claimed": str(claimed) if claimed else None,
        "agrees": ok,
        # Interval arithmetic is exact only when every variable occurs once;
        # otherwise it is a sound OVER-approximation of the attainable set.
        "precision": "EXACT" if exact else "OVER_APPROX",
        "unbound_vars": sorted(set(used) - set(env)),
    }
    for clamp in model.get("clamps", []):
        operand = eval_expr(clamp["operand"], env)
        k = float(clamp["bound"])
        dead = (
            operand.clamp_low_is_dead(k)
            if clamp["op"] == "max"
            else operand.clamp_high_is_dead(k)
        )
        verdict = "DEAD" if dead else "NOT_PROVED_DEAD"
        out.setdefault("clamps", []).append(
            {
                "site": clamp.get("site"),
                "op": clamp["op"],
                "bound": k,
                "operand_range": str(operand),
                "verdict": verdict,
                "claimed": clamp.get("expect"),
                "agrees": clamp.get("expect") in (None, verdict),
            }
        )
        if clamp.get("expect") not in (None, verdict):
            out["agrees"] = False
    return out


# ---------------------------------------------------------------------------
# 5. Driver
# ---------------------------------------------------------------------------


def run(ledger: dict[str, Any], subject_src: str, subject_sha: str,
        companion_sha: str | None) -> dict[str, Any]:
    report: dict[str, Any] = {"checks": {}, "ok": True}

    # --- identity ---
    subj = ledger["subject"]
    identity = {
        "subject_path": subj["path"],
        "subject_ref": subj.get("git_ref"),
        "expected_sha256": subj["sha256"],
        "actual_sha256": subject_sha,
        "match": subject_sha == subj["sha256"],
    }
    comp = ledger.get("companion")
    if comp is not None:
        identity["companion_path"] = comp["path"]
        identity["companion_expected_sha256"] = comp["sha256"]
        identity["companion_actual_sha256"] = companion_sha
        identity["companion_match"] = (
            companion_sha is None or companion_sha == comp["sha256"]
        )
        identity["divergence_note"] = comp.get("note")
    report["checks"]["identity"] = identity
    if not identity["match"]:
        report["ok"] = False
    if comp is not None and identity.get("companion_match") is False:
        report["ok"] = False

    # --- census drift ---
    sites = census(subject_src)
    diff = census_diff(sites, ledger.get("census", []))
    census_ok = not (diff["added"] or diff["removed"] or diff["moved"])
    report["checks"]["census"] = {
        "site_count": len(sites),
        "frozen_count": len(ledger.get("census", [])),
        "diff": diff,
        "ok": census_ok,
        "soundness": "UNDER_APPROXIMATION -- drift detector only, not a discovery tool",
    }
    if not census_ok:
        report["ok"] = False

    # --- call-site bindings ---
    bindings = []
    for spec in ledger.get("bindings", []):
        rep = call_sites(subject_src, spec["fn"])
        d = rep.as_dict()
        expected_calls = spec.get("expect_calls")
        expected_lits = spec.get("expect_literal_args")
        d["expected_call_lines"] = expected_calls
        d["expected_literal_args"] = expected_lits
        agrees = rep.sound
        if expected_calls is not None:
            agrees = agrees and sorted(c.line for c in rep.calls) == sorted(expected_calls)
        if expected_lits is not None:
            got = [c.literal_args.get(int(spec.get("arg_index", 0))) for c in rep.calls]
            agrees = agrees and sorted(x for x in got if x) == sorted(expected_lits)
        d["agrees"] = agrees
        if not rep.sound:
            d["verdict"] = "INCONCLUSIVE"
        elif len(rep.calls) == 1:
            idx = int(spec["arg_index"]) if "arg_index" in spec else None
            bound = idx is not None and idx in rep.calls[0].literal_args
            d["verdict"] = (
                "SINGLE_CALL_SITE_LITERAL_BINDING" if bound else "SINGLE_CALL_SITE"
            )
        else:
            d["verdict"] = "MULTI_CALL_SITE"
        bindings.append(d)
        if not agrees:
            report["ok"] = False
    report["checks"]["bindings"] = bindings

    # --- range models ---
    ranges = []
    for model in ledger.get("range_models", []):
        r = range_model_report(model)
        ranges.append(r)
        if not r["agrees"]:
            report["ok"] = False
    report["checks"]["ranges"] = ranges

    return report


def format_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    ident = report["checks"]["identity"]
    lines.append("== identity ==")
    lines.append(
        f"  subject {ident['subject_path']}\n"
        f"    expected {ident['expected_sha256']}\n"
        f"    actual   {ident['actual_sha256']}   "
        f"{'MATCH' if ident['match'] else 'DIVERGED'}"
    )
    if "companion_path" in ident:
        lines.append(
            f"  companion {ident['companion_path']}: "
            + (
                "not checked"
                if ident["companion_actual_sha256"] is None
                else ("MATCH" if ident["companion_match"] else "DIVERGED")
            )
        )
        if ident.get("divergence_note"):
            lines.append(f"    note: {ident['divergence_note']}")

    c = report["checks"]["census"]
    lines.append("== census (drift detector) ==")
    lines.append(f"  {c['site_count']} sites now, {c['frozen_count']} frozen -> "
                 f"{'NO DRIFT' if c['ok'] else 'DRIFT'}")
    for kind in ("added", "removed", "moved"):
        for item in c["diff"][kind]:
            lines.append(f"    {kind.upper():8} {item}")

    lines.append("== call-site bindings ==")
    for b in report["checks"]["bindings"]:
        lines.append(
            f"  {b['name']}: def@{b['definitions']} calls@"
            f"{[x['line'] for x in b['calls']]} bare@{b['bare_uses']} "
            f"-> {b['verdict']} ({'ok' if b['agrees'] else 'MISMATCH'})"
        )
        for call in b["calls"]:
            if call["literal_args"]:
                lines.append(f"      line {call['line']} literals {call['literal_args']}")

    lines.append("== attainable ranges ==")
    for r in report["checks"]["ranges"]:
        lines.append(
            f"  {r['id']} ({r['site']}): computed {r['computed']} "
            f"claimed {r['claimed']} [{r['precision']}] "
            f"{'ok' if r['agrees'] else 'MISMATCH'}"
        )
        for cl in r.get("clamps", []):
            lines.append(
                f"      clamp .{cl['op']}({cl['bound']:g}) at {cl['site']}: "
                f"operand {cl['operand_range']} -> {cl['verdict']} "
                f"{'ok' if cl['agrees'] else 'MISMATCH'}"
            )

    lines.append(f"== overall: {'PASS' if report['ok'] else 'FAIL'} ==")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--subject", type=Path, help="path to the subject .rs file")
    ap.add_argument(
        "--git-ref",
        help="read the subject as 'git show <ref>:<path>' (default: the ledger's own)",
    )
    ap.add_argument("--repo", type=Path, default=Path("."), help="git repo root")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    ledger = json.loads(args.ledger.read_text())

    if args.subject:
        data = args.subject.read_bytes()
    else:
        ref = args.git_ref or ledger["subject"]["git_ref"]
        try:
            data = read_from_git(args.repo, ref)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    subject_sha = sha256_bytes(data)
    src = data.decode("utf-8", errors="replace")

    companion_sha = None
    comp = ledger.get("companion")
    if comp is not None:
        cpath = args.repo / comp["path"]
        if cpath.exists():
            companion_sha = sha256_bytes(cpath.read_bytes())

    report = run(ledger, src, subject_sha, companion_sha)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
