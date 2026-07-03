#!/usr/bin/env python3
"""Safe Rust source minifier for CG submissions: strips comments and blank
lines while respecting string literals (incl. raw strings) and char literals.
No identifier renaming (too risky). Usage: minify.py in.rs out.rs
The caller MUST compile-check the output before submitting.
"""
import sys

def minify(src: str) -> str:
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        # raw strings r", r#", r##" ...
        if c == 'r' and i + 1 < n and src[i + 1] in '"#':
            j = i + 1
            hashes = 0
            while j < n and src[j] == '#':
                hashes += 1
                j += 1
            if j < n and src[j] == '"':
                end_marker = '"' + '#' * hashes
                k = src.find(end_marker, j + 1)
                k = n if k == -1 else k + len(end_marker)
                out.append(src[i:k])
                i = k
                continue
        if c == '"':
            j = i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == '"':
                    j += 1
                    break
                j += 1
            out.append(src[i:j])
            i = j
            continue
        if c == "'":
            # char literal or lifetime; char literals are short — copy up to 5
            # chars conservatively when it closes with ' within 4.
            seg = src[i:i + 6]
            close = seg.find("'", 1)
            if close != -1 and (seg[1] != '\\' or close >= 3):
                out.append(src[i:i + close + 1])
                i += close + 1
                continue
            out.append(c)  # lifetime tick
            i += 1
            continue
        if c == '/' and i + 1 < n and src[i + 1] == '/':
            j = src.find('\n', i)
            i = n if j == -1 else j  # keep the newline
            continue
        if c == '/' and i + 1 < n and src[i + 1] == '*':
            depth = 1
            j = i + 2
            while j < n - 1 and depth:
                if src[j] == '/' and src[j + 1] == '*':
                    depth += 1
                    j += 2
                elif src[j] == '*' and src[j + 1] == '/':
                    depth -= 1
                    j += 2
                else:
                    j += 1
            i = j
            continue
        out.append(c)
        i += 1
    text = ''.join(out)
    # drop blank lines + trailing spaces
    lines = [l.rstrip() for l in text.split('\n')]
    lines = [l for l in lines if l.strip()]
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    src = open(sys.argv[1]).read()
    m = minify(src)
    open(sys.argv[2], 'w').write(m)
    print(f"{len(src)} -> {len(m)} chars ({100*len(m)//max(1,len(src))}%)")
