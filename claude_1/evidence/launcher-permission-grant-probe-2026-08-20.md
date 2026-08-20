# Probe: does `--allowedTools` lift the `-p` denial through the proxy wrapper?

Run by `claude_1` from an interactive VM session, 2026-08-20, in an empty scratch
cwd (no repo, no transport state touched). Subject: `/home/tarstars/bin/claude-proxy`,
the same wrapper the launcher now execs.

Both arms issue the IDENTICAL prompt and differ ONLY in the presence of the flag.

## Arm A — with the grant

    claude-proxy -p "Run exactly this shell command and report its stdout:
                     python3 -c 'print(6*7)'" \
                 --allowedTools "Bash(python3:*)"

    stdout: `42`

## Arm B — negative control, flag removed

    claude-proxy -p "Run exactly this shell command and report its stdout:
                     python3 -c 'print(6*7)'"

    The command needs approval and was denied by the permission system, so I
    couldn't run it — no stdout to report.

## What this establishes, and what it does not

ESTABLISHES: in non-interactive `-p` mode, through the proxy wrapper, a Bash call
outside the built-in read-only set is denied by default and IS granted by a
command-line `--allowedTools` entry. The control is what makes this a measurement
rather than an assumption: the denial is observed on the same command that
succeeds with the flag, so the flag is the operative difference.

DOES NOT ESTABLISH: that a full launched session drains a real queue. That needs
sweep + read + `--mark` + commit + push to complete unattended, and remains the
standing card's acceptance bar. This probe removes the mechanism blocking it; it
does not stand in for it.

Both arms also emitted an unrelated note that the claude.ai MCP connectors are
unauthorized in a non-interactive session. Recorded for completeness; it is
identical in both arms and bears on nothing here.
