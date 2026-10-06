# 03 — The loop: pick, fire and pressure

Author: Vero. Written 2026-10-06. Status: v1.0 for review. Planning only; nothing is built.
Names of tables, columns and `web_config` keys match `02-schema.md` (Qualia), which wins if there is a disagreement. Reach behaviour is in
`06-reaches-and-receptors.md`; prompt text and starting numbers are in `05-prompt-assembly-and-content.md`; context building is in
`04-context-building-and-embeddings.md`; the simulation that tested these rules is in `09-simulation.md`.

Legend: **[decided]** = Teddy said so. **[assumed]** = my choice where Teddy did not say; tested in the simulation unless noted. **[open]** = needs Teddy.

This document is the algorithm. A programmer should be able to write the loop from it without asking anyone.

---

## 1. What the loop does, in one paragraph

One process, run by Teddy, repeats **steps**. In each step it chooses one member (a strand or a reach) to run, builds that member's prompt, calls its model once, records everything, stores the output in the member's weaves, and then lets the member's weaves "fire", which changes the pressure of weaves. Pressure decides how likely members are to be chosen next. Nobody tells her when to act. Doing nothing is a real choice. The only external controls are the global pause button and starting or stopping the process.

## 2. State the loop reads and writes

| What | Where | Notes |
|---|---|---|
| Current pressure of each weave | `weave_pressure_now` (cache) rebuilt from `pressure_events` | `02` §4. Rebuilt at start and checked after every step. |
| Who ran last | `picks.previous_pick_id`, `calls` | Needed for the handoff rule. |
| Config | `web_config` (all keys in `02` §9) | Re-read at the start of each step, so edits made in the UI take effect from the **next** call [decided]. |
| Structure | `weaves`, `strands`, `reaches`, `membership`, `pressure_map`, `fire_effects`, `receptor_effects` | Re-read at the start of each step. |
| Pause state | last row of `control_events` | See `08` §3. |

The loop keeps no other state in memory that matters. Restarting the process must resume from the database: the last `picks` row gives the previous member, and `weave_pressure_now` gives pressure.

## 3. One step, in order

```
step():
  0. check_pause()
  1. load config and structure
  2. candidates = build_candidates()
  3. eff = effective_pressure()                       # sec 5
  4. weights = weight_of(member) for each candidate    # sec 6
  5. chosen = pick(candidates, weights, seed)          # sec 7
  6. write picks row
  7. check_pause()
  8. build prompt (docs 04, 05), call the model once   # sec 8
  9. parse the output, perform the reach function if any (doc 06)
 10. write calls row (+ context_links, context_candidates, message_reads, outbox as needed)
 11. write memories (+ memory_tags if any) and queue their embeddings
 12. fire(chosen)                                      # sec 9
 13. integrity check (pressure cache vs events)
 14. sleep briefly if nothing else is waiting
```

Step 7 exists because the pause may arrive while the pick is being made; the loop must not start a model call after a pause has been requested.

## 4. Candidates and the handoff rule [decided]

```
build_candidates():
  if there is no previous pick:            # the very first step
      candidates = enabled members that belong to the weave with the highest pressure     # in practice Realign
  else:
      prev = previous chosen member
      candidates = enabled members, other than prev (if web_config.no_repeat_last), that share at least one weave with prev
  return candidates
```

Notes:
- **Handoff only goes between members that share a weave.** A member in weave D cannot be handed the conversation by a member that is only in A (Teddy's example: Strand 1 in A, B, C; Strand 3 in D, E, F; Strand 3 can only be reached through a strand that is in D or E).
- **The pressure map does not create handoff paths.** It only creates pull (section 5) [decided].
- **First step:** Realign starts at 0.99, so its members are the candidates. If the database already has history (a restart), the first step after a restart uses the normal rule with the last `picks` row as `prev`.
- `no_repeat_last = true` [assumed; tested]: a member can't be picked twice in a row. Without it, a weave-only member could repeat.
- **Reaches are candidates, exactly like strands** [per `06` §1]. My simulation counted strands only (see `09`).
- **Empty candidate set** (all members that share a weave with `prev` are disabled, or only `prev` shares a weave): the loop falls back to all enabled members (uniform weights) and writes `picks.reason = 'fallback_all'`. This should not happen with the drafted membership; the fallback exists so the loop never stalls. [assumed, untested; `reason` value is new, Qualia please add it to the allowed values in `picks.reason`].
- `enabled = 0` members are never candidates. This is a member-level switch, not the global pause.

## 5. Effective pressure and the walk [decided; numbers configurable]

The pressure map (`pressure_map`) is a graph of weaves. A weave's **effective pressure** is its own pressure plus a weaker pull from weaves one and two lines away, capped.

```
effective_pressure():
  p   = current pressure per weave                       # from weave_pressure_now
  dist = shortest-path distance between every pair of weaves in pressure_map (breadth-first search)
  pct  = web_config.pressure_walk_pct                    # [1.0, 0.75, 0.25]
  jumps = web_config.pressure_walk_jumps                 # 2
  for each weave w:
      total = p[w] * pct[0]
      for each other weave o with 1 <= dist[w][o] <= jumps:
          total += pct[dist[w][o]] * p[o]
      eff[w] = min(total, web_config.pull_cap)           # pull_cap default 1.0
  return eff
```

Teddy's words: "3 jumps, 100% for direct, 75% for the next jump, and 25% for the third." My reading: the weave itself at 100%, weaves one line away at 75%, weaves two lines away at 25% (`pressure_walk_jumps = 2` jumps beyond the direct weave) [decided by Teddy, "direct +2"]. The pull counts even if a member is not in the pulling weave [decided]. Unreachable weaves (no path) contribute nothing.

`pull_cap` [assumed; tested]: effective pressure of a weave is capped at 1.0 so the walk can't make a weave count for more than a fully pressured weave. Stored in config; Qualia keeps it below 1 as a rule for pressure, but the *effective* value may equal the cap.

**Worked example.** Weaves: Realign (R), Express (A), Consider (B), Observe (C). Map: R–B, A–B, B–C. Pressures: R 0.30, A 0.50, B 0.20, C 0.10.
Distances: R–B 1, R–A 2, R–C 2; A–B 1, A–C 2; B–C 1.
- eff[B] = 0.20 + 0.75×(R 0.30 + A 0.50 + C 0.10) = 0.20 + 0.75×0.90 = 0.875.
- eff[R] = 0.30 + 0.75×B 0.20 + 0.25×(A 0.50 + C 0.10) = 0.30 + 0.15 + 0.15 = 0.60.
- eff[A] = 0.50 + 0.75×B 0.20 + 0.25×(R 0.30 + C 0.10) = 0.50 + 0.15 + 0.10 = 0.75.
- eff[C] = 0.10 + 0.75×B 0.20 + 0.25×(R 0.30 + A 0.50) = 0.10 + 0.15 + 0.20 = 0.45.

## 6. Weight of a member [decided: average]

```
weight_of(member):
  weaves = the weaves the member belongs to
  if web_config.weave_combine == 'average':  return mean(eff[w] for w in weaves)
  if web_config.weave_combine == 'sum':      return sum(eff[w] for w in weaves)        # tested, not used
```

Teddy chose **average** (2026-10-06). The reason: with `sum`, a member in two weaves gets about twice the weight, and in my simulation the Express-only strand Composer (the strand most likely to produce something to say to Teddy) was picked only 3.4% of the time at the suggested settings, against 14-17% for the strands that bridge two weaves. With the average the spread is flatter (Composer about 4.7%) and the suggested setting still passed 8 of 8 seeds.

Continuing the example (candidates Orienter in R,B; Composer in A; Doubter in B,C):
- Orienter: mean(0.60, 0.875) = 0.7375.
- Composer: 0.75.
- Doubter: mean(0.875, 0.45) = 0.6625.
Chance of each = weight / total weight = 0.7375/2.15 = 34.3%, 0.75/2.15 = 34.9%, 0.6625/2.15 = 30.8%.

## 7. The pick [decided]

```
pick(candidates, weights, seed):
  if sum(weights) > 0:   reason = 'weighted_random';  chosen = weighted random choice using Random(seed)
  else:                  reason = 'uniform_random';   chosen = uniform random choice using Random(seed)      # all weights 0, as in the first Fenra
  # first step overall: reason = 'first_pick' (weights as above)
```

- The seed is generated fresh for each step from a system source and **stored** in `picks.seed`, so any pick can be replayed from the stored `pool_json`, `pressures_json` and `effective_json`.
- `picks.pool_json` records every candidate and its weight. `pressures_json` and `effective_json` record the pressure and effective pressure per weave at pick time.
- Use one random generator type, fixed in code (for example Python `random.Random(seed)`), so a replay on another machine gives the same answer.
- Floating point: record weights rounded to 6 decimals in `pool_json`; compute the choice from the unrounded values and write the rounding rule in the code, so replays don't differ.

## 8. The call

Details are in `04`, `05` and `06`. What the loop must guarantee:
- The prompt is built from the member's own weaves (`04`) and stored whole in `calls.prompt_text`, with `prompt_parts_json` giving the size of each part for the UI's size bars.
- The model is called **once** per step. One call, one response. No retries inside the step. A failure is recorded with `error_text` and `parse_ok = 0` and the step ends without firing (`05` §5.3).
- Pause is checked **before** the model call (step 7) and **after** the call returns. The call in progress is allowed to finish (`08` §3).
- **Output is stored by code**, never written by the model: memories (`02` §2) go in one row per weave of the member; the thinking text goes to `calls.thinking_text` only.
- Embedding of the new memories happens in the background and does not delay the next step (`04`). A memory is invisible to lookup until its vector exists.

## 9. Firing [decided]

When a call completes (including a call where the member said `nothing`: see the **[open]** note), **all weaves the member belongs to fire** ("feelings: one action can move several weaves", Teddy).

The update rule is the remaining-gap rule [decided], which keeps every pressure in [0, 1):
- **Raise by a:** `p ← p + a·(1 − p)`
- **Lower by a:** `p ← p − a·p`

Order within a firing [decided: lowers first, then raises]:

```
fire(member):
  F = the weaves of member                              # the weaves that fire
  # 1. each firing weave lowers its own pressure
  for w in F:
      lower(w, a = web_config.self_lowering)             # 0.1 default
      # writes pressure_events: op='lower', cause='fire_self', cause_id=calls.id, step_no
  # 2. then all raises (and any negative-amount effects as lowers), from fire_effects
  lowers = []; raises = []
  for w in F:
      for (to, amount) in fire_effects where from_weave == w:
          if amount < 0: lowers.append((to, -amount)) else raises.append((to, amount))
  for (to, a) in lowers: lower(to, a)       # cause='fire_effect'
  for (to, a) in raises: raise(to, a)       # cause='fire_effect'
```

- `fire_effects.amount` is positive to raise and negative to lower (`02` §1).
- If two firing weaves both raise the same target, both raises apply, one after the other. For raises, order does not change the result: `1 − (1−p)(1−a1)(1−a2)` either way.
- A weave in `F` can also be a target of another firing weave's effects; that is allowed.
- Each individual change writes one `pressure_events` row with `before`, `after`, `op`, `amount`, `cause` (`fire_self` or `fire_effect`), `cause_id = calls.id`, `step_no`. The new value is also written to `weave_pressure_now` in the same transaction. The row count per firing is therefore: (number of firing weaves) + (number of effect rows applied).
- `calls.fired_weaves` records the ids in `F` as a JSON array.

**Worked example.** Orienter (R, B) is picked and responds. Starting pressures: R 0.50, B 0.30, A 0.20, C 0.10. Config: `self_lowering = 0.1`; fire effects from `05` §3.3 (R→B 0.30; R has no other effects; B→A 0.08, B→C 0.025, B→R 0.02).
1. Self-lowering: R: 0.50 − 0.1×0.50 = 0.45. B: 0.30 − 0.1×0.30 = 0.27.
2. Raises (no lowers here): R→B 0.30: B = 0.27 + 0.30×(1−0.27) = 0.489. B→A 0.08: A = 0.20 + 0.08×0.80 = 0.264. B→C 0.025: C = 0.10 + 0.025×0.90 = 0.1225. B→R 0.02: R = 0.45 + 0.02×0.55 = 0.461.
Result: R 0.461, B 0.489, A 0.264, C 0.1225. That firing writes six `pressure_events` rows: self R, self B, R→B, B→A, B→C, B→R.

**[open] Does "nothing" fire?** My simulation assumed every picked member fires, including when it says "nothing". If "nothing" did not fire, pressure would not change and the next pick would use the same weights, so the same few members could be picked repeatedly. Recommendation: yes, it fires. `06` §5 already assumes yes for reaches. Teddy has not said. See `05` §5.3.

## 10. Receptors [decided in principle; amounts proposed]

A receptor turns an outside event into a pressure raise on chosen weaves. Plain code, no model. It runs **immediately after the UI inserts a row into `inbox`**, in the same transaction (`06` §6):

```
apply_receptor(event_kind, cause_id):
  for (weave, amount) in receptor_effects of the receptor with that event_kind:
      raise(weave, amount)          # pressure_events: op='raise', cause='receptor', cause_id=inbox.id
```

- Teddy's message raises **Observe**. Starting amount: 0.1 [proposed, untested].
- It happens even if the loop is paused (the pressure change is just bookkeeping), and it does not wake anything. It only changes how likely Observe's members are to be picked once the loop runs.
- Several messages in a row each apply once. Observe approaches 1 and never reaches it.
- The receptor is not a step: it does not write `picks` or `calls`, and does not count in `step_no` except as the `step_no` of the most recent step (`pressure_events.step_no` may be NULL).

## 11. Start-up and shutdown

**First start (empty database):**
1. Create the tables and triggers (`02`).
2. Load the content from `05`: weaves, strands, reaches, membership, pressure map, fire effects, receptors, config.
3. For each weave, write one `pressure_events` row (`op = 'init'`, `amount = initial_pressure`, `before = 0`, `after = initial_pressure`, `cause = 'init'`) and the cache row. Realign = 0.99; the others 0.
4. Start the loop. Step 1 picks among Realign's members (Orienter, Recaller, Checker).

**Restart:** rebuild `weave_pressure_now` from `pressure_events`, compare with the cache, write any mismatch to `integrity_log`, continue from the last `picks` row. The loop never re-initializes pressure on a restart.

**Stop:** a stop request ends the loop after the current step. A kill mid-step leaves a `picks` row without a completed `calls` row; on restart the loop writes a `calls` row for the pick with `error_text = 'interrupted'`, `parse_ok = 0`, and continues without firing for it. Nothing is deleted.

**Launch hygiene** (a standing rule for Fenra processes): each launch uses a **new, distinct log file name** (never reuse), and the launcher is detached so a closed window doesn't kill it.

## 12. Integrity checks

- After every step: `weave_pressure_now` equals the `after` of the latest `pressure_events` row per weave. A mismatch is written to `integrity_log` (`check_name = 'pressure_cache_vs_events'`) and shown in the UI. The loop continues, using the events as the truth.
- Every pressure is in [0, 1) after every event (assert; write to `integrity_log` and pause if violated, since it means a bug).
- Every candidate member is in at least one weave (enforced when it is enabled; asserted here).
- The set of weaves and members read at the start of the step is the set used for the whole step (no mid-step structure changes).

## 13. Edge cases

| Case | Behaviour |
|---|---|
| All candidate weights are 0 | uniform random pick, `reason='uniform_random'` |
| A member is in no weave | cannot be enabled; if found, skip and write `integrity_log` |
| Only one candidate | it is picked (with `no_repeat_last`, if that candidate is `prev` the fallback applies) |
| The pressure map has two disconnected parts | no pull between them; handoff is still by shared weave |
| A weave has zero members | its pressure is still computed and still pulls; nothing in it can be picked |
| Pressure very close to 1 | the remaining-gap rule keeps it below 1; use floating point carefully and clamp tiny numeric overshoot to `1 − 1e-9` |
| Pause requested during a call | the call finishes, no fire is skipped, the loop stops before the next step (`08` §3) |
| Process killed mid-step | see section 11 |

## 14. Config defaults (from `02` §9, plus the starting numbers)

| key | default |
|---|---|
| `weave_combine` | `average` |
| `pressure_walk_jumps` | `2` |
| `pressure_walk_pct` | `[1.0, 0.75, 0.25]` |
| `self_lowering` | `0.1` |
| `no_repeat_last` | `true` |
| `pull_cap` | `1.0` |

Starting pressures: Realign 0.99; Express, Consider, Observe 0.0. Fire-effect numbers: `05` §3.3.

## 15. Not decided or not tested

**Decide (Teddy):**
- Does a call where the member said "nothing" fire the weaves, and is a memory stored for it? (Recommended: fires; memory only if there is text beyond the bare word.)
- Whether the fallback when no candidates exist should be "all enabled members" (my proposal) or something else.

**Untested:**
- Whether reaches, once included in the candidate set, change the dynamics (the simulation had strands only).
- The 100/75/25 walk was tested with and without (0 jumps vs 2): it passed in both, and the walk helped a little (81 vs 66 passing settings of 162 each). A longer walk (3 jumps) was not tested; it makes no difference here because the map has only four weaves and the farthest pair is two lines apart.
- The effect of the receptor in a quiet web.
- Timing: how many steps per minute the real models give on this machine (CPU/GPU split of `qwen3.5:4b` and embeddinggemma) is unmeasured; the simulation counts steps, not time.
- The numbers for B's effects (Consider→Express, Consider→Observe) are my assumptions.
