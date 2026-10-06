"""Fenra web pressure simulation (throwaway, model-free). Spec: ../pressure-simulation-spec.md (draft 2).

Stdlib only. No models, no database, no network. Writes results next to this file.
Run:  python pressure_sim.py            (full sweep, a minute or two)
      python pressure_sim.py --trace    (one default run, first 300 steps, to trace.csv)
Everything marked ASSUMPTION in the spec is a parameter or a named constant here.
"""
import csv
import itertools
import random
import statistics
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).parent

WEAVES = ["R", "A", "B", "C"]          # Realign, Express, Consider, Observe
MAP = [("R", "B"), ("A", "B"), ("B", "C")]   # pressure map, two-way (Teddy)
STRANDS = {                              # first-strands-draft.md
    "Orienter": {"R", "B"}, "Recaller": {"R"}, "Checker": {"R"},
    "Composer": {"A"}, "Asker": {"A", "C"},
    "Weigher": {"B"}, "Doubter": {"B", "C"}, "Connector": {"A", "B"},
    "Reader": {"C"}, "Noticer": {"C", "B"},
}
WALK = [1.0, 0.75, 0.25]                 # direct, +1 jump, +2 jumps (Teddy)
R_START = 0.99


def adjacency():
    adj = {w: set() for w in WEAVES}
    for a, b in MAP:
        adj[a].add(b)
        adj[b].add(a)
    return adj


ADJ = adjacency()


def distances(src):
    d = {src: 0}
    q = deque([src])
    while q:
        w = q.popleft()
        for n in ADJ[w]:
            if n not in d:
                d[n] = d[w] + 1
                q.append(n)
    return d


DIST = {w: distances(w) for w in WEAVES}


def make_effects(scale, r_to_b, r_inflow):
    """fire_effects[from][to] = amount. Pattern from Teddy: A->C high (B ~0), C->B high, C->A a bit;
    R->B raises Consider; small inflow from A, B, C into R. B->A is ASSUMPTION ("think, then say")."""
    e = {w: {} for w in WEAVES}
    e["A"] = {"C": scale, "B": 0.0, "R": r_inflow}
    e["C"] = {"B": scale, "A": scale / 3, "R": r_inflow}
    e["B"] = {"A": scale * 0.8, "C": scale / 4, "R": r_inflow}
    e["R"] = {"B": r_to_b}
    return e


def effective(p, jumps):
    """Effective pressure of each weave: own p at 100%, plus pull from neighbours at 75% (1 jump) and 25% (2 jumps),
    capped at 1 (ASSUMPTION: pull can't exceed full pressure). jumps=0 means own p only."""
    out = {}
    for w in WEAVES:
        tot = p[w]
        for o in WEAVES:
            if o == w:
                continue
            d = DIST[w].get(o)
            if d is not None and 1 <= d <= jumps:
                tot += WALK[d] * p[o]
        out[w] = min(tot, 1.0)
    return out


def run(cfg, seed, steps):
    rng = random.Random(seed)
    eff_fx = make_effects(cfg["scale"], cfg["r_to_b"], cfg["r_inflow"])
    p = {w: 0.0 for w in WEAVES}
    p["R"] = R_START
    names = list(STRANDS)
    prev = None
    fires = {w: 0 for w in WEAVES}
    picks = {n: 0 for n in names}
    leave_step = None
    series = {w: [] for w in WEAVES}
    top_hist = []
    trace = []
    for t in range(steps):
        if prev is None:
            cands = [n for n in names if "R" in STRANDS[n]]
        else:
            # handoff: strands sharing a weave with the one that just ran (ASSUMPTION: not itself)
            cands = [n for n in names if n != prev and STRANDS[n] & STRANDS[prev]]
        if not cands:                    # stuck
            return {"stuck": True}
        eff = effective(p, cfg["jumps"])
        wts = [sum(eff[w] for w in STRANDS[n]) / (len(STRANDS[n]) if cfg.get("agg") == "mean" else 1) for n in cands]
        pick = rng.choices(cands, weights=wts)[0] if sum(wts) > 0 else rng.choice(cands)
        picks[pick] += 1
        firing = STRANDS[pick]
        for w in firing:
            fires[w] += 1
        if leave_step is None and "R" not in firing:
            leave_step = t
        # lowers first (self-lowering of each firing weave), then raises
        for w in firing:
            p[w] -= cfg["self_low"] * p[w]
        for w in firing:
            for tgt, a in eff_fx[w].items():
                p[tgt] += a * (1 - p[tgt])
        if cfg["rec_every"] and t % cfg["rec_every"] == cfg["rec_every"] - 1:
            p["C"] += cfg["rec_amt"] * (1 - p["C"])     # receptor: Teddy speaks
        for w in WEAVES:
            series[w].append(p[w])
        top = max(("A", "B", "C"), key=lambda w: p[w])
        top_hist.append(top)
        if len(trace) < 300:
            trace.append([t, pick, "+".join(sorted(firing))] + [round(p[w], 4) for w in WEAVES])
        prev = pick
    return {"stuck": False, "fires": fires, "picks": picks, "leave": leave_step,
            "series": series, "top": top_hist, "trace": trace}


def autocorr_peak(x, lo=3, hi=80):
    n = len(x)
    m = sum(x) / n
    v = sum((a - m) ** 2 for a in x)
    if v < 1e-12:
        return 0.0, 0
    best, lag_best = -1.0, 0
    for lag in range(lo, hi + 1):
        c = sum((x[i] - m) * (x[i + lag] - m) for i in range(n - lag)) / v
        if c > best:
            best, lag_best = c, lag
    return best, lag_best


def metrics(res, steps):
    if res["stuck"]:
        return {"stuck": 1}
    f = res["fires"]
    total = sum(f.values())
    share = {w: f[w] / total for w in WEAVES}
    top = res["top"]
    switches = sum(1 for i in range(1, len(top)) if top[i] != top[i - 1]) / len(top)
    # lock: any 500-step window where one of A,B,C accounts for > 90% of A/B/C fires -- approximated by
    # dominance of the top-pressure weave over windows
    lock = 0
    W = 500
    for s in range(0, len(top) - W + 1, W):
        win = top[s:s + W]
        for w in ("A", "B", "C"):
            if win.count(w) / W > 0.9:
                lock = 1
    tail = {w: statistics.mean(res["series"][w][steps // 2:]) for w in WEAVES}
    silent = 1 if max(tail[w] for w in ("A", "B", "C")) < 0.02 else 0
    flat = 1 if min(tail[w] for w in ("A", "B", "C")) > 0.97 else 0
    pk, lag = autocorr_peak(res["series"]["B"][steps // 2:][:1200])
    return {"stuck": 0, "leave": res["leave"] if res["leave"] is not None else steps,
            "R_share": share["R"], "A_share": share["A"], "B_share": share["B"], "C_share": share["C"],
            "switch_rate": switches, "lock": lock, "silent": silent, "flat": flat,
            "rock_peak": pk, "rock_lag": lag, "never_left": 1 if res["leave"] is None else 0,
            "min_strand_share": min(res["picks"].values()) / sum(res["picks"].values()),
            "tail_R": tail["R"], "tail_A": tail["A"], "tail_B": tail["B"], "tail_C": tail["C"]}


def passes(m):
    """Pass condition (spec): leaves Realign promptly, doesn't lock, doesn't die/flatten, Realign comes back without
    dominating (3%..40% of fires), and shows rocking (autocorrelation peak > 0.2 on B's pressure)."""
    return int(m["stuck"] == 0 and m["never_left"] == 0 and m["leave"] <= 60 and m["lock"] == 0
               and m["silent"] == 0 and m["flat"] == 0 and 0.03 <= m["R_share"] <= 0.40 and m["rock_peak"] > 0.2)


def sweep(steps=3000, seeds=8):
    grid = {
        "scale": [0.1, 0.3, 0.5],
        "self_low": [0.1, 0.3, 0.6],
        "r_inflow": [0.0, 0.02, 0.1],
        "r_to_b": [0.1, 0.3, 0.6],
        "rec_every": [0, 200],
        "jumps": [0, 2],
    }
    keys = list(grid)
    rows = []
    for vals in itertools.product(*[grid[k] for k in keys]):
        cfg = dict(zip(keys, vals))
        cfg["rec_amt"] = 0.4
        ms = [metrics(run(cfg, 1000 + s, steps), steps) for s in range(seeds)]
        ok = [m for m in ms if m.get("stuck", 0) == 0]
        row = dict(cfg)
        row["seeds"] = seeds
        row["stuck_runs"] = seeds - len(ok)
        if ok:
            for k in ("leave", "R_share", "A_share", "B_share", "C_share", "switch_rate", "rock_peak", "min_strand_share"):
                row[k] = round(statistics.median(m[k] for m in ok), 4)
            for k in ("lock", "silent", "flat", "never_left"):
                row[k] = sum(m[k] for m in ok)
            row["pass_seeds"] = sum(passes(m) for m in ok)
        rows.append(row)
    return rows


def main():
    if "--trace" in sys.argv:
        cfg = {"scale": 0.3, "self_low": 0.3, "r_inflow": 0.02, "r_to_b": 0.3, "rec_every": 0, "jumps": 2, "rec_amt": 0.4}
        res = run(cfg, 1000, 400)
        with open(HERE / "trace.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["step", "strand", "weaves_fired", "p_R", "p_A", "p_B", "p_C"])
            w.writerows(res["trace"])
        print("wrote trace.csv")
        return
    rows = sweep()
    cols = list(rows[0].keys())
    for r in rows:
        for c in r:
            if c not in cols:
                cols.append(c)
    with open(HERE / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(rows)
    print("wrote results.csv:", len(rows), "configs")


if __name__ == "__main__":
    main()
