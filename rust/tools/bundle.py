#!/usr/bin/env python3
"""Bundle the library bot back into ONE CG-submittable source file (Phase R).

The bot's logic lives in library modules (src/botmain.rs and, as the refactor proceeds,
the files it declares) so tests and the equality harness can reach it; CodinGame however
accepts a single file. This tool re-inlines the module tree: it starts from src/botmain.rs,
recursively replaces any `mod x;` declaration with `mod x { <contents of x.rs> }`, and
appends a `fn main()` trampoline calling `run()`.

The caller MUST gate the output (see docs/refactor-goal.md):
  1. rustc --edition 2021 -O <copy with dot-free name>   # compiles
  2. equality <bundled-bin> <target/release/bot> N ... # stream-identical to the lib build
  3. tools/minify.py → < 100 KB

Usage: bundle.py [src/botmain.rs] [out.rs]
"""
import os, re, sys


def inline(path: str, seen: set) -> str:
    if path in seen:
        raise SystemExit(f"module cycle at {path}")
    seen.add(path)
    src = open(path).read()
    base = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]

    def repl(m):
        vis, name = m.group(1) or "", m.group(2)
        # module file: <dir>/<name>.rs or <dir>/<stem>/<name>.rs (non-root layout)
        cands = [os.path.join(base, f"{name}.rs"), os.path.join(base, stem, f"{name}.rs")]
        for c in cands:
            if os.path.exists(c):
                body = inline(c, seen)
                # strip inner attributes (only legal at crate/module top; keep code)
                body = re.sub(r"^#!\[[^\]]*\]\s*\n", "", body, flags=re.M)
                return f"{vis}mod {name} {{\n{body}\n}}"
        raise SystemExit(f"cannot find module file for `mod {name};` (tried {cands})")

    return re.sub(r"^(pub )?mod (\w+);\s*$", repl, src, flags=re.M)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "src/botmain.rs"
    out = sys.argv[2] if len(sys.argv) > 2 else "target/refactor/bundled.rs"
    code = inline(src, set())
    code += "\n\nfn main() {\n    run();\n}\n"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(code)
    print(f"{src} -> {out}: {len(code)} chars (gate with rustc + equality + minify)")


if __name__ == "__main__":
    main()
