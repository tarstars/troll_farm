#!/usr/bin/env python3
"""Figures for the 2026-09-01 edition of the neural-network line report:
the entropy gate (scouts, locked panel, training side) and the credit path / lever pricing.
Run with the math venv's Python (matplotlib):  python3 make_entropy_figs.py
Reads the pinned results under local_claude_1/nn-bot/results/entropy-gate-0901/ and
claude_1/results/nn-bot-lever-price/; writes PNGs next to this script."""
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
R = os.path.join(ROOT, "local_claude_1", "nn-bot", "results", "entropy-gate-0901")
OFF, ON, NEUTRAL, GRID = "#2a78d6", "#eb6834", "#52514e", "#e6e5e0"   # validated: dataviz palette slots 1, 2 + text
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": NEUTRAL, "axes.labelcolor": "#0b0b0b", "xtick.color": NEUTRAL,
                     "ytick.color": NEUTRAL, "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def bench(tag, age, locked=False):
    name = f"bench-{tag}{'-locked' if locked else ''}-u{age}.json"
    return json.load(open(os.path.join(R, name)))


def fig_scouts():
    ages = [500, 1000, 1500, 2000, 2500]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, (title, off, on) in zip(axes, [("Cluster pair (the gate's arms)", "e00b", "e01b"),
                                           ("Host pair (the replication)", "h00", "h01")]):
        for tag, color, label in ((off, OFF, "entropy bonus off (E00)"), (on, ON, "entropy bonus on (E01)")):
            wins = [bench(tag, a)["policy_wins"] for a in ages]
            ax.plot(ages, wins, color=color, linewidth=2, marker="o", markersize=6, label=label)
            ax.annotate(str(wins[-1]), (ages[-1], wins[-1]), textcoords="offset points", xytext=(6, 0),
                        va="center", color="#0b0b0b", fontsize=9)
        ax.axhline(9, color=NEUTRAL, linewidth=1, linestyle=":")
        ax.text(500, 9.3, "the clone's bar, 9 of 48", color=NEUTRAL, fontsize=8)
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_xlabel("training update")
        ax.set_xticks(ages)
        ax.set_ylim(0, 16)
    axes[0].set_ylabel("wins of 48 against the champion's file")
    axes[0].legend(frameon=False, fontsize=9, loc="upper right")
    fig.suptitle("Scout benches: no age separates the two arms, and both decay with depth", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(HERE, "entropy-scouts.png"), dpi=160)


def fig_gate():
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    groups = [("Cluster\nupdate 1,500", "e00b", "e01b", 1500), ("Cluster\nupdate 2,500", "e00b", "e01b", 2500),
              ("Host\nupdate 1,500", "h00", "h01", 1500), ("Host\nupdate 2,500", "h00", "h01", 2500)]
    clone = json.load(open(os.path.join(R, "bench-clone-locked.json")))["policy_wins"]
    x = range(len(groups))
    w = 0.36
    for i, (label, off, on, age) in enumerate(groups):
        a, b = bench(off, age, True)["policy_wins"], bench(on, age, True)["policy_wins"]
        ax.bar(i - w / 2, a, w - 0.04, color=OFF, label="entropy off (E00)" if i == 0 else None)
        ax.bar(i + w / 2, b, w - 0.04, color=ON, label="entropy on (E01)" if i == 0 else None)
        ax.text(i - w / 2, a + 0.6, str(a), ha="center", fontsize=9, color="#0b0b0b")
        ax.text(i + w / 2, b + 0.6, str(b), ha="center", fontsize=9, color="#0b0b0b")
    ax.axhline(clone, color=NEUTRAL, linewidth=1, linestyle=":")
    ax.text(-0.45, clone + 0.6, f"the clone on the same panel, {clone} of 144", color=NEUTRAL, fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([g[0] for g in groups], fontsize=9)
    ax.set_ylabel("wins of 144 on the locked panel")
    ax.set_ylim(0, 34)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title("Confirmation benches (the same 144 cells for every bar)", fontsize=10, loc="left")
    ax = axes[1]
    for i, (label, name) in enumerate([("Cluster pair", "gate1-verdict.json"), ("Host pair", "gate1-verdict-host-replication.json")]):
        v = json.load(open(os.path.join(R, name)))
        m, (lo, hi) = v["mean_effect"], v["ci95"]
        ax.plot([lo, hi], [i, i], color=NEUTRAL, linewidth=2)
        ax.plot([m], [i], marker="o", markersize=8, color=OFF)
        ax.text(hi + 0.004, i, f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]", va="center", fontsize=8, color="#0b0b0b")
    ax.axvline(0, color="#0b0b0b", linewidth=1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["cluster", "host"])
    ax.set_ylim(-0.7, 1.7)
    ax.set_xlim(-0.08, 0.12)
    ax.set_xlabel("paired effect of removing the bonus,\nwins per cell (95 % interval)")
    ax.set_title("The frozen gate: NOT CONFIRMED, twice", fontsize=10, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "entropy-gate.png"), dpi=160)


def blocks(path, field, block=250):
    xs, ys = [], []
    rows = [json.loads(l) for l in open(path) if l.startswith("{")]
    rows = [r for r in rows if "update" in r and isinstance(r.get(field), (int, float))]
    for start in range(0, 2709, block):
        chunk = [r[field] for r in rows if start < r["update"] <= start + block]
        if chunk:
            xs.append(start + block)
            ys.append(statistics.fmean(chunk))
    return xs, ys


def fig_training():
    logs = {"e00b": os.path.join(ROOT, "yt_work/ppo/ppo-yt-e00b-output/extracted/outputs/train.log"),
            "e01b": os.path.join(ROOT, "yt_work/ppo/ppo-yt-e01b-output/extracted/outputs/train.log")}
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, field, title in zip(axes, ("entropy", "win_rate"),
                                ("Policy entropy (the knob works: +0.068)", "Training win rate, sampled play (no difference)")):
        for tag, color, label in (("e00b", OFF, "entropy off (E00)"), ("e01b", ON, "entropy on (E01)")):
            xs, ys = blocks(logs[tag], field)
            ax.plot(xs, ys, color=color, linewidth=2, marker="o", markersize=4, label=label)
        ax.set_xlabel("training update (means of 250-update blocks)")
        ax.set_title(title, fontsize=10, loc="left")
    axes[0].set_ylabel("entropy of the action distribution")
    axes[1].set_ylabel("win rate against the training opponent")
    axes[1].set_ylim(0.1, 0.3)
    axes[0].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "entropy-training.png"), dpi=160)


def fig_levers():
    lp = json.load(open(os.path.join(ROOT, "claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json")))
    total = lp.get("rows_total") or 65536
    splits = [("0 + 4\nevery run so far", lp["splits"]["0+4"]["nonzero_reward_rows"]),
              ("0.5 + 3.5\nthe environment's\ndefault", lp["splits"]["0.5+3.5"]["nonzero_reward_rows"]),
              ("2 + 2\nthe arm now\ntraining", lp["splits"]["2+2"]["nonzero_reward_rows"])]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    for i, (label, n) in enumerate(splits):
        ax.bar(i, 100 * n / total, 0.55, color=OFF)
        ax.text(i, 100 * n / total + 0.08, f"{n:,} rows\n{100 * n / total:.2f} %", ha="center", fontsize=9, color="#0b0b0b")
    ax.set_xticks(range(3))
    ax.set_xticklabels([s[0] for s in splits], fontsize=9)
    ax.set_ylabel("% of rows carrying any observed reward")
    ax.set_ylim(0, 3.6)
    ax.set_title("Lever 1 — where wood's value is paid", fontsize=10, loc="left")
    ax = axes[1]
    w32 = 100 * lp["splits"]["0+4"]["windows"]["32"]["plan"]["terminal_traced_fraction"]
    w128 = 100 * lp["splits"]["0+4"]["windows"]["128"]["plan"]["terminal_traced_fraction"]
    for i, (label, v) in enumerate([("32 steps\n(every run so far)", w32), ("128 steps\n(the next lever)", w128)]):
        ax.bar(i, v, 0.55, color=OFF)
        ax.text(i, v + 0.15, f"{v:.2f} %", ha="center", fontsize=9, color="#0b0b0b")
    ax.set_xticks(range(2))
    ax.set_xticklabels(["32 steps\nevery run so far", "128 steps\nthe next lever"], fontsize=9)
    ax.set_ylabel("% of plan rows whose trace\nreaches a real ending")
    ax.set_ylim(0, 8)
    ax.set_title("Lever 2 — how far the trainer looks ahead", fontsize=10, loc="left")
    fig.suptitle("The credit path, priced offline on one set of games (claude_1, three seeds agree)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(HERE, "credit-levers.png"), dpi=160)




def fig_ledger():
    """The campaign ledger: every 2026-09-01/02 arm on the locked 144-cell panel, both ages."""
    arms = [
        ("the clone (no training)", None, None, "clone"),
        ("entropy off (E00, cluster)", "e00b", None, None),
        ("entropy on (E01, cluster)", "e01b", None, None),
        ("entropy off (h00, host)", "h00", None, None),
        ("entropy on (h01, host)", "h01", None, None),
        ("rollout 128 alone (host)", "hl128", None, None),
        ("wood 0.5 + 3.5 (host)", "r0535", None, None),
        ("wood 2 + 2 (host)", "hr22", None, None),
        ("wood 2 + 2 (r22, cluster)", "r22", None, None),
        ("the stack: 2 + 2 + rollout 128 (s22)", "s22", None, None),
    ]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    clone = json.load(open(os.path.join(R, "bench-clone-locked.json")))["policy_wins"]
    ax.axvline(clone, color=NEUTRAL, linewidth=1, linestyle=":")
    ax.text(clone + 0.3, -0.62, f"the clone's bar, {clone}", color=NEUTRAL, fontsize=8)
    for i, (label, tag, _, kind) in enumerate(arms):
        y = len(arms) - 1 - i
        if kind == "clone":
            ax.plot([clone], [y], marker="D", markersize=7, color=NEUTRAL)
            continue
        w1 = bench(tag, 1500, True)["policy_wins"]
        w2 = bench(tag, 2500, True)["policy_wins"]
        ax.plot([w1, w2], [y, y], color=GRID, linewidth=2, zorder=1)
        ax.plot([w1], [y], marker="o", markersize=8, color=OFF, zorder=2)
        ax.plot([w2], [y], marker="o", markersize=8, color=ON, zorder=2)
        lo, hi = (w1, w2) if w1 <= w2 else (w2, w1)
        ax.text(hi + 0.6, y, f"{w1} → {w2}", va="center", fontsize=9, color="#0b0b0b")
        p2709 = os.path.join(R, "bench-s22-locked-u2709.json")
        if tag == "s22" and os.path.exists(p2709):
            w3 = json.load(open(p2709))["policy_wins"]
            ax.plot([w3], [y], marker="s", markersize=7, color="#1baf7a", zorder=3)
            ax.text(w3 + 0.5, y - 0.5, f"update 2,709: {w3} (exploratory)", fontsize=8, color="#1baf7a", ha="center")
    ax.set_yticks(range(len(arms)))
    ax.set_yticklabels([a[0] for a in reversed(arms)], fontsize=9)
    ax.set_xlabel("wins of 144 on the locked panel, against the champion's file (parity = 72)")
    ax.set_xlim(14, 42)
    ax.set_ylim(-1.0, len(arms) - 0.4)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", color=OFF, linestyle="none", label="at update 1,500"),
                       Line2D([], [], marker="o", color=ON, linestyle="none", label="at update 2,500"),
                       Line2D([], [], marker="D", color=NEUTRAL, linestyle="none", label="the clone (the starting point)")],
              frameon=False, fontsize=9, loc="lower left")
    ax.set_title("Training now improves the bot: the whole campaign on one axis", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "campaign-ledger.png"), dpi=160)


if __name__ == "__main__":
    fig_scouts()
    fig_gate()
    fig_training()
    fig_levers()
    fig_ledger()
    print("wrote entropy-scouts.png entropy-gate.png entropy-training.png credit-levers.png campaign-ledger.png")
