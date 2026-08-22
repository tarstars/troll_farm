#!/usr/bin/env python3
"""Systematic dead/constant-code scan for the minified E7a source.

Hunts the classes that the iterative programme has been consuming, plus the
ones a fresh cascade would open: single-valued function parameters, constant
local bindings, single-call functions, never-read struct fields, unconstructed
enum variants, and constant-comparison guards.
"""
import re
import sys
from collections import defaultdict

src = open(sys.argv[1]).read()


def match_brace(text, open_idx):
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_args(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '(<[':
            depth += 1
        elif ch in ')>]':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


# ---- functions: signature, body, call sites -------------------------------
funcs = {}
for m in re.finditer(r'fn (\w+)\(', src):
    name = m.group(1)
    popen = m.end() - 1
    depth, pclose = 0, -1
    for i in range(popen, len(src)):
        if src[i] == '(':
            depth += 1
        elif src[i] == ')':
            depth -= 1
            if depth == 0:
                pclose = i
                break
    params = split_args(src[popen + 1:pclose])
    bopen = src.find('{', pclose)
    bclose = match_brace(src, bopen)
    funcs[name] = {
        'params': [p for p in params if p and p not in ('&self', '&mut self', 'self')],
        'has_self': any(p in ('&self', '&mut self', 'self') for p in params),
        'body': src[bopen:bclose + 1],
        'span': (m.start(), bclose + 1),
    }

calls = defaultdict(list)
for name in funcs:
    for m in re.finditer(r'(?:(?:\w+::|self\.)+)?\b' + re.escape(name) + r'\(', src):
        start = m.end() - 1
        depth, close = 0, -1
        for i in range(start, len(src)):
            if src[i] == '(':
                depth += 1
            elif src[i] == ')':
                depth -= 1
                if depth == 0:
                    close = i
                    break
        if src[m.start():m.end()].startswith('fn '):
            continue
        # skip the definition itself
        if src[max(0, m.start() - 3):m.start()] == 'fn ':
            continue
        calls[name].append(split_args(src[start + 1:close]))

print('=== SINGLE-VALUED PARAMETERS (same literal/expr at every call site) ===')
LIT = re.compile(r'^(-?\d+|true|false|None|"[^"]*")$')
for name, info in sorted(funcs.items()):
    sites = calls.get(name, [])
    if not sites or not info['params']:
        continue
    n = len(info['params'])
    usable = [s for s in sites if len(s) == n]
    if not usable:
        continue
    for idx, param in enumerate(info['params']):
        vals = {s[idx] for s in usable}
        if len(vals) == 1 and LIT.match(next(iter(vals))):
            pname = param.split(':')[0]
            reads = len(re.findall(r'\b' + re.escape(pname) + r'\b', info['body']))
            print(f'  {name}(param {pname}) = {next(iter(vals))} at all {len(usable)} sites; '
                  f'{reads} body occurrences')

print()
print('=== CONSTANT LOCAL BINDINGS ===')
for m in re.finditer(r'let (?:mut )?(\w+)=([^;]{1,60});', src):
    name, val = m.group(1), m.group(2)
    if LIT.match(val) or re.match(r'^-?\d+i32\.clamp\(\d+,\d+\)$', val):
        print(f'  let {name}={val};  (reads: {len(re.findall(chr(92)+"b"+name+chr(92)+"b", src)) - 1})')

print()
print('=== SINGLE-CALL FUNCTIONS (candidate wrappers) ===')
for name, info in sorted(funcs.items()):
    n = len(calls.get(name, []))
    if n == 1 and name not in ('main',):
        print(f'  {name}: 1 call site, body {len(info["body"])} bytes, params {len(info["params"])}')

print()
print('=== UNCALLED FUNCTIONS ===')
for name, info in sorted(funcs.items()):
    if not calls.get(name) and name != 'main':
        print(f'  {name}: 0 call sites, body {len(info["body"])} bytes')

print()
print('=== STRUCT FIELDS: write-only or unread ===')
for m in re.finditer(r'(?:pub )?struct (\w+)\{([^}]*)\}', src):
    sname, fields = m.group(1), m.group(2)
    for f in split_args(fields):
        if ':' not in f:
            continue
        fname = f.split(':')[0].replace('pub ', '').strip()
        if not fname.isidentifier():
            continue
        total = len(re.findall(r'\b' + re.escape(fname) + r'\b', src))
        reads = len(re.findall(r'(?:self|inner|bot)\.' + re.escape(fname) + r'\b', src))
        if total <= 2:
            print(f'  {sname}.{fname}: {total} total occurrences, {reads} dotted reads')

print()
print('=== ENUM VARIANTS NEVER CONSTRUCTED ===')
for m in re.finditer(r'enum (\w+)\{([^}]*)\}', src):
    ename, variants = m.group(1), m.group(2)
    for v in split_args(variants):
        v = v.split('(')[0].strip()
        if not v:
            continue
        uses = len(re.findall(re.escape(ename) + r'::' + re.escape(v) + r'\b', src))
        if uses <= 1:
            print(f'  {ename}::{v}: {uses} uses')

print()
print('=== CONSTANT COMPARISONS / GUARDS ===')
for m in re.finditer(r'(?:if|while)\s*\(?\s*(-?\d+)\s*(<=|>=|<|>|==|!=)\s*(-?\d+)\b', src):
    print(f'  {m.group(0)}')
for m in re.finditer(r'\b(true|false)\s*(&&|\|\|)', src):
    print(f'  {src[max(0,m.start()-40):m.end()+20]}')
