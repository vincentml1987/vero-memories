# 09 — The pressure simulation

Author: Vero. Written 2026-10-06. Status: done for v1 of the question, with known gaps (section 7). Planning-phase artifact: a throwaway script with **no models, no database, no network**.
The rules it tests are the ones in `03-loop-pick-and-pressure.md`; starting numbers it suggests are in `05-prompt-assembly-and-content.md` §3.

Files (copies are in `09-simulation-files/` next to this document; the signed originals are in Vero's repo at `Claude Code AIs\Vero\Vero\fenra-web\sim\`, commit `5b77cdf`, plus later edits noted below):

| File | What it is |
|---|---|
| `09-simulation-files/pressure_sim.py` | The script. Stdlib Python 3. About 235 lines. |
| `09-simulation-files/results.csv` | One row per setting (324 rows): the settings and the results over 8 seeds. |
| `09-simulation-files/results.md` | The plain-language write-up of the sweep (what Teddy read). |
| `09-simulation-files/trace.csv` | The first 300 steps of one default run: step, strand picked, weaves fired, pressure of each weave. |
| `09-simulation-files/pressure-simulation-spec.md` | The spec the script was written from (draft 2). |

## 1. The question

Teddy's design is a web in which weaves hold pressure, pressure decides which member runs next, and each run changes pressure. Teddy expected a "rocking motion" (Express → Consider → Observe → Consider → Express) "like pushing a spider web". Before any model does real thinking, the simulation asks:

1. Does the web leave Realign (which starts at 0.99), or get stuck there?
2. Does it swing (rock), or lock onto one weave, or go quiet or flat?
3. Does Realign come back into play without dominating?
4. Which starting numbers give good behaviour, and how sensitive is that to each number?

## 2. What the script simulates (exactly)

Matches `03-loop-pick-and-pressure.md` unless noted.

- **Weaves:** Realign (R), Express (A), Consider (B), Observe (C). Pressure map: R–B, A–B, B–C. Starting pressure: R = 0.99, others 0.
- **Members:** the ten strands of `05` §4 with their weaves. **Reaches are not simulated.**
- **Handoff:** the next member must share a weave with the one that just ran, and may not be the same member twice in a row (`no_repeat_last`). The first step picks among Realign's members.
- **Effective pressure:** own pressure at 100%, weaves one line away at 75%, two lines away at 25%, capped at 1.0 (`jumps = 2`); or own pressure only (`jumps = 0`).
- **Weight:** the **sum** of a member's weaves' effective pressures (default in the script). The `agg='mean'` option (the **average**, which Teddy chose) was added afterwards and run only at the single suggested setting (section 4).
- **Pick:** weighted random; uniform random if all weights are 0. Seeds `1000 … 1007` for the 8 seeds of every setting (`random.Random(seed)`).
- **Firing:** all weaves of the picked member fire. Each firing weave first lowers its own pressure by `self_low × p`; then every fire effect applies (remaining-gap rule: raise `p + a(1−p)`, lower `p − a·p`). Lowers before raises.
- **Fire effects** (`make_effects(scale, r_to_b, r_inflow)`): A→C = scale, A→B = 0, A→R = inflow; C→B = scale, C→A = scale/3, C→R = inflow; B→A = 0.8×scale, B→C = scale/4, B→R = inflow; R→B = `r_to_b`. (B's effects are my assumptions.)
- **Receptor:** optionally, every 200 steps raise C by 0.4 (a stand-in for "Teddy speaks"). In the sweep this is "on" or "off".
- **Steps per run:** 3000. Seeds per setting: 8. Settings: 324.

## 3. The sweep

All combinations of:

| parameter | values |
|---|---|
| `scale` (strength of fire effects) | 0.1, 0.3, 0.5 |
| `self_low` (how much a firing weave lowers itself) | 0.1, 0.3, 0.6 |
| `r_inflow` (A, B, C → Realign) | 0.0, 0.02, 0.1 |
| `r_to_b` (Realign → Consider) | 0.1, 0.3, 0.6 |
| `rec_every` (receptor kick period) | none, 200 |
| `jumps` (walk) | 0, 2 |

Metrics per run (medians over seeds in `results.csv`):

| column | meaning |
|---|---|
| `leave` | step at which a member **not** in Realign is first picked |
| `R_share`, `A_share`, `B_share`, `C_share` | fraction of all weave-fires belonging to each weave |
| `switch_rate` | how often the highest-pressure weave among A, B, C changes, per step |
| `rock_peak` | highest autocorrelation of Consider's pressure at lags 3-80 over steps 1500-2700. **My stand-in for "rocking"**; above 0.2 counts as swinging. |
| `lock` | number of seeds in which one of A, B, C was the **highest-pressure** weave in more than 90% of some 500-step window |
| `silent` / `flat` | number of seeds where the tail mean of A, B, C all fell below 0.02 / all rose above 0.97 |
| `never_left` | number of seeds that never left Realign |
| `min_strand_share` | share of picks of the least-picked strand |
| `pass_seeds` | seeds (of 8) that meet the pass condition |

**Pass condition** for a seed: leaves Realign within 60 steps, never stuck, no lock, not silent, not flat, Realign fires in 3-40% of fires, and `rock_peak > 0.2`. A **setting** is counted as passing if at least 6 of 8 seeds pass.

## 4. Results

**Headline:** 147 of 324 settings pass. The web leaves Realign in about 3 steps (median 3, maximum 4.5 over settings). No run was stuck, silent or flat. Realign fires in 3-18% of fires (never above 18%).

**What matters most** (passing settings out of 147 / mean passing seeds):

| parameter | result |
|---|---|
| `self_low` | **the biggest lever.** 0.1: 95 passing settings; 0.3: 52; **0.6: 0**. At 0.6 pressure slams between near 0 and near 1 and never swings. |
| `scale` | gentle is better. 0.1: 69 passing; 0.3: 52; 0.5: 26. |
| `jumps` | the walk helps a little. 2: 81 passing (of 162); 0: 66. |
| `r_to_b` | smaller is slightly better. 0.1: 57; 0.3: 54; 0.6: 36. All work. |
| `r_inflow` | matters little for passing (0: 49; 0.02: 52; 0.1: 46), but changes Realign's share (below). |
| `rec_every` | **no measurable effect** (see section 7). |

**Realign's share vs inflow** (median `R_share`): inflow 0 → 6.3%; 0.02 → 10.4%; 0.1 → 11.4%. Most of Realign's firing comes from **Orienter** (in Realign and Consider, so it fires Realign every time it is picked), not from the inflow.

**Ranges inside the passing settings:** A fires in 18-25% of fires, B 38-43%, C 25-34%, Realign 3.5-17%. Leaving Realign takes 2.5-4.5 steps.

**Lock:** flagged only in 10 of the gentlest settings, in 1-3 of 8 seeds. The measure uses the highest-pressure weave, not who fires; fire shares in those runs are still balanced, so I read it as slow drifting rather than locking. It should be watched in real runs.

**Strand share under `sum` vs `mean`** (suggested setting, 8 seeds × 3000 steps):

| strand | sum | mean |
|---|---|---|
| Connector (A,B) | 17.0% | 14.2% |
| Noticer (C,B) | 16.9% | 14.3% |
| Doubter (B,C) | 16.8% | 14.0% |
| Orienter (R,B) | 15.3% | 14.5% |
| Asker (A,C) | 13.6% | 11.7% |
| Weigher (B) | 6.9% | 9.7% |
| Reader (C) | 5.2% | 7.2% |
| **Composer (A)** | **3.4%** | **4.7%** |
| Recaller (R) | 2.5% | 4.8% |
| Checker (R) | 2.5% | 5.0% |

At the suggested setting both rules passed 8 of 8 seeds (`mean`: median `rock_peak` 0.71, Realign share 14.4%, leaves Realign at step 6). Teddy chose **average** (2026-10-06).

### Suggested starting values (proposed, tested at this one point under `sum` and `mean`)

- Fire-effect strength 0.1 (so A→C 0.10, C→B 0.10, C→A 0.033, B→A 0.08, B→C 0.025).
- `self_low` = 0.1 → `web_config.self_lowering = 0.1`.
- Realign inflow 0.02 from each of A, B, C.
- Realign → Consider 0.3.
- Walk on (100/75/25, 2 jumps).
- Realign starts at 0.99.
These are in `05` §3.3 as the proposed values. They are **starting points for real runs**, not decisions.

Reading the trace (`trace.csv`, default setting: scale 0.3, self_low 0.3, inflow 0.02, R→B 0.3, walk on): step 0 Checker (Realign), step 1 Recaller, step 2 Orienter (B+R), then strands in A, B and C alternate; A and C swing between 0.2 and 0.97 with B in the middle. This default is a stronger setting than the suggested one and swings harder.

## 5. How to run it again

Requires Python 3 only (no packages). From `09-simulation-files/`:

```
python pressure_sim.py --trace      # writes trace.csv: first 300 steps of one default run (seconds)
python pressure_sim.py              # full sweep: 324 settings x 8 seeds x 3000 steps; about 1.5 minutes; writes results.csv
```

To try one setting from Python:

```python
import pressure_sim as S
cfg = {"scale":0.1, "self_low":0.1, "r_inflow":0.02, "r_to_b":0.3,
       "rec_every":200, "jumps":2, "rec_amt":0.4, "agg":"mean"}   # agg: "sum" (default) or "mean"
res = S.run(cfg, seed=1000, steps=3000)
print(S.metrics(res, 3000), S.passes(S.metrics(res, 3000)))
```

Edit the membership in `STRANDS`, the map in `MAP`, the effects in `make_effects`, and the start values to test a changed design. The pass condition is `passes()`; the metric definitions are in `metrics()`.

Mapping from script names to `web_config` keys (`02` §9): `self_low` → `self_lowering`; `jumps` → `pressure_walk_jumps`; `WALK` → `pressure_walk_pct`; `agg` → `weave_combine`; `no_repeat_last` is fixed true in the script; the cap of 1.0 is `pull_cap`.

## 6. How to use the results (what each outcome would change)

If a rerun, or the first real runs, show:

| observation | change to try |
|---|---|
| One weave takes over | lower the pushes into it (`fire_effects`) or raise `self_lowering`; if it still locks, the walk is too strong (lower the 75/25). |
| Pressures slam to 0 and 1, no steady swing | lower the effect strengths (the sweep's 0.5 and `self_low` 0.6 did this) |
| Everything goes quiet or flat near 1 | lower the effect strengths, raise `self_lowering`; check the inflow into Realign |
| Realign dominates or the web never leaves it | lower the inflow into Realign or raise Realign → Consider so Orienter is picked sooner; if still stuck, add a second bridge strand |
| Realign fades and never returns | raise the inflow (`r_inflow`); if "who am I" should recur, keep it nonzero |
| The swing exists only in a narrow band of numbers | the design is fragile: widen the margin with more self-lowering, or accept the band and record it |
| A member is almost never picked | give it a better-connected weave or a link (the sweep showed single-weave members get fewer picks, especially under `sum`) |
| Recovery after Teddy speaks is slow | lower Observe's push to Consider, or shorten the walk |

Every change to numbers is recorded in `structure_changes` (with a "why") so a run can be compared with an earlier setting.

## 7. What was not tested, and what to do about it

1. **Speaking into a quiet web.** The receptor test (0.4 on Observe every 200 steps) changed nothing measurable because Observe was already high. The case that matters, a quiet web and then a message, was not tested. Follow-up: start from a quiet state (all pressures low, long silence), apply one kick, and measure how many steps until Observe's members are picked and how long the web takes to settle. Try kicks of 0.05, 0.1, 0.3.
2. **The exact swing order.** `rock_peak` measures that Consider's pressure repeats with a period; it does not prove the order A → B → C → B → A. A direct measure would count transitions between the highest-pressure weave of each step and compare them to the expected order.
3. **Reaches in the pick.** The simulation counted only strands. Speak to Teddy (Express) and Listen to Teddy (Observe) are candidates in the real loop (`06` §1). Add them with their weaves and see whether the shares and the swing change.
4. **"Nothing" firing.** Every pick fired in the simulation. If Teddy decides "nothing" does not fire, rerun with that rule: pressure would stop changing on those steps.
5. **Consider's fire effects** (B→A 0.8×scale, B→C scale/4) are my assumptions. Teddy gave none for Consider. A sweep over these two numbers would show how much they matter.
6. **The mean at other settings.** `mean` was run only at the one suggested setting, not across the sweep.
7. **The cap** (`pull_cap`) and "not the same member twice" (`no_repeat_last`) were assumptions and were not varied.
8. **No time.** The simulation counts steps. Steps per minute depends on the real models (qwen3.5:4b and embeddinggemma on this GPU) and is unmeasured.
9. **No real text.** Nothing in this simulation says anything about whether the strands' outputs make sense. That is for the first real run, with Qualia and Teddy watching.

## 8. Decisions that are Teddy's (from the simulation)

- Done: sum vs average → **average**. Pause granularity → global only.
- Open: does "nothing" fire the weaves? (`03` §9 and §15; recommendation yes.)
- Open: the receptor amount (0.1 proposed; untested).

## 9. Checking the real engine against the simulation (for `10` M3)

`10` M3 says the real engine should reproduce the simulation's recorded seeds, with "the same pick sequence for the same seed and settings (or a documented, explained difference)". **An identical pick sequence is possible only in a special parity mode**, because the two programs make random choices differently:

| | Simulation | Real engine (`03` §7) |
|---|---|---|
| Random numbers | one generator per run, `random.Random(seed)`, used for every pick in order | a fresh stored seed for every pick (`picks.seed`) |
| Members | the ten strands only | ten strands plus two reaches |
| Weight | sum (default); `mean` available | average |
| Candidate order | the order of the `STRANDS` list | by id |
| Effects | built from three numbers (`scale`, `r_to_b`, `r_inflow`) | rows in `fire_effects` |

So M3 should have **two checks**:

1. **Parity check (exact).** In a test mode, the engine uses the simulation's membership (no reaches), the simulation's candidate order, `weave_combine = sum` or `mean` to match `agg`, one `random.Random(run_seed)` stream consumed once per step with the same call (`rng.choices(candidates, weights)`), and the same effects, and it must reproduce the first 300 steps of `trace.csv` (strand, weaves fired, and pressures to 4 decimals). This proves the update rule, the walk, handoff, firing order and the weights are implemented as simulated.
2. **Behaviour check (statistical).** In the real configuration (ten strands plus two reaches, average, per-step stored seeds), over at least 8 seeds × 3000 steps at the suggested setting: no run stuck, silent or flat; Realign left within 60 steps; Realign's fire share between 3% and 40%; each strand picked at least once; `rock_peak` above 0.2 on Consider's pressure in most seeds. Differences from the simulation's numbers are expected (the reaches add candidates) and should be written up.

A separate **replay check** (`10` §5) verifies that any real pick can be recomputed from its stored `seed`, `pool_json`, `pressures_json` and `effective_json`.
