"""Render an A2C learning curve (rl/runs/<tag>/curve.csv) as an ASCII chart.

Dependency-free (stdlib only) so it never needs matplotlib. Shows the raw
per-iteration margin (my_score - opp_score) and a moving average, plus win-rate.

    uv run python -m rl.plot_curve rl/runs/a2c_chopper/curve.csv
"""

import csv
import sys


def moving_avg(xs, k=10):
    out = []
    for i in range(len(xs)):
        lo = max(0, i - k + 1)
        out.append(sum(xs[lo:i + 1]) / (i - lo + 1))
    return out


def ascii_chart(xs, ys, width=68, height=18, label="margin"):
    if not ys:
        return "(no data)"
    lo, hi = min(ys), max(ys)
    if hi == lo:
        hi = lo + 1.0
    # bucket x into `width` columns, take the mean y per column
    n = len(ys)
    cols = [[] for _ in range(width)]
    for i in range(n):
        c = int(i * width / n)
        c = min(c, width - 1)
        cols[c].append(ys[i])
    colmean = [(sum(c) / len(c)) if c else None for c in cols]

    grid = [[" "] * width for _ in range(height)]

    def row_of(v):
        frac = (v - lo) / (hi - lo)
        r = int(round((1 - frac) * (height - 1)))
        return min(max(r, 0), height - 1)

    # zero line
    if lo <= 0 <= hi:
        zr = row_of(0.0)
        for x in range(width):
            grid[zr][x] = "-"
    for x, v in enumerate(colmean):
        if v is None:
            continue
        grid[row_of(v)][x] = "*"

    lines = []
    for r in range(height):
        # y-axis label at top/mid/bottom
        yval = hi - (hi - lo) * r / (height - 1)
        axis = f"{yval:7.1f} |"
        lines.append(axis + "".join(grid[r]))
    lines.append(" " * 8 + "+" + "-" * width)
    lines.append(" " * 9 + f"iter 0{' ' * (width - 12)}iter {len(ys)}")
    lines.append(f"        ({label}; '*' = per-column mean, '-' = 0 line; "
                 f"range {lo:.1f}..{hi:.1f})")
    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "rl/runs/a2c_chopper/curve.csv"
    rows = list(csv.DictReader(open(path)))
    it = [int(r["iter"]) for r in rows]
    margin = [float(r["margin"]) for r in rows]
    win = [float(r["win_rate"]) for r in rows]
    ma = moving_avg(margin, 10)

    print(f"== {path} ({len(rows)} iters) ==")
    print(ascii_chart(it, margin, label="margin (per-iter mean)"))
    k = max(1, len(rows) // 10)
    print("\niter |  margin | ma10   | win  | mywood | oppwood | trolls")
    for i in range(0, len(rows), k):
        r = rows[i]
        print(f"{r['iter']:>4} | {float(r['margin']):7.1f} | {ma[i]:6.1f} | "
              f"{float(r['win_rate']):4.2f} | {float(r['my_wood']):6.1f} | "
              f"{float(r['opp_wood']):7.1f} | {float(r['n_trolls']):.2f}")
    r = rows[-1]
    print(f"{r['iter']:>4} | {float(r['margin']):7.1f} | {ma[-1]:6.1f} | "
          f"{float(r['win_rate']):4.2f} | {float(r['my_wood']):6.1f} | "
          f"{float(r['opp_wood']):7.1f} | {float(r['n_trolls']):.2f}")
    first = sum(margin[:10]) / min(10, len(margin))
    last = sum(margin[-10:]) / min(10, len(margin))
    print(f"\nmargin: first10={first:.1f} -> last10={last:.1f}  (Δ {last - first:+.1f})")


if __name__ == "__main__":
    main()
