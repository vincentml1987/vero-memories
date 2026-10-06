# Pressure simulation — results (2026-10-05, Vero)

Throwaway script, no models: `pressure_sim.py` (stdlib Python). Rules are Teddy's, as recorded in
`../pressure-simulation-spec.md` (draft 2). Raw numbers are in `results.csv`; `trace.csv` is the first 300 steps of one default run.

**Sweep:** 324 settings × 8 random seeds × 3000 steps each. Settings varied: strength of fire effects (0.1 / 0.3 / 0.5),
how much a weave lowers itself when it fires (0.1 / 0.3 / 0.6), the small inflow into Realign from A, B, C (0 / 0.02 / 0.1),
the Realign → Consider push (0.1 / 0.3 / 0.6), a Teddy-message kick on Observe every 200 steps (none / on), and the pressure walk
(own pressure only / 100-75-25).

## Plain summary

1. **The web does leave Realign, fast, and never gets stuck.** Orienter gets picked within about 3 steps in every setting. Nothing went silent, nothing flattened to all-1, and no run ran out of strands to hand off to.
2. **Realign comes back without dominating.** It fires in 3–17% of steps in every setting. Most of that comes from Orienter's membership (Orienter sits in Realign and Consider, so every time it fires, Realign fires). The small inflow from A, B and C matters much less than expected: zero inflow gives about 6% of fires, 0.02 gives about 10%, 0.1 gives about 11%.
3. **How hard a weave lowers itself when it fires matters most.** At 0.1 the rocking appears in most settings (95 of 147 passing settings); at 0.3 in about half the passing ones; at 0.6 in none. Strong self-lowering plus strong pushes makes pressures slam between near 0 and near 1 with no steady swing.
4. **Gentle pushes work better than strong ones.** Passing settings by effect strength: 69 (0.1), 52 (0.3), 26 (0.5).
5. **147 of 324 settings pass** (at least 6 of 8 seeds). The best-looking starting point I'd suggest trying: effect strength 0.1, self-lowering 0.1, Realign inflow 0.02, Realign → Consider 0.3, walk on. That passed 8 of 8 seeds.

## Things I want you to know about, not just the good news

- **Multi-weave strands get picked much more than single-weave ones.** A strand's weight is the *sum* of its weaves' effective pressures, so a strand in two weaves has about twice the weight. In the suggested setting the bridge strands (Connector, Noticer, Doubter, Orienter, Asker) take 14–17% of all picks each, while **Composer (Express only) gets 3.4%, Reader (Observe only) 5.2%, Recaller and Checker 2.5% each**. Composer is the strand most likely to produce something to say to Teddy, so this matters. If the weight is the *average* of a strand's weaves instead of the sum, the spread is much flatter (Composer 4.7%, Reader 7.2%, Recaller and Checker about 5%) and it still passes 8 of 8 seeds. That is a design choice for you, Teddy. I'd lean toward the average.
- **The Teddy-message kick had almost no effect in this test.** A kick of 0.4 on Observe every 200 steps changed nothing measurable, because Observe is usually already fairly high. I did **not** test the case that matters more: the web is quiet, then you speak, and we watch how long it takes to respond and settle. That needs a better test.
- **My "rocking" measure is my own definition.** It's the strongest repeating pattern (autocorrelation peak above 0.2) in Consider's pressure over a window of 3 to 80 steps. It shows swinging, but it does not prove the specific A → B → C → B → A order. The trace shows A and C swinging high and low alternately with B in the middle, which looks right, but I haven't measured the order directly.
- **"Lock" fired only in the gentlest settings,** and it measures which weave has the highest *pressure*, not which one fires. Fire shares in those runs are still balanced (A 18–25%, B 38–43%, C 25–34% in the passing settings). So I read it as slow drifting, not locking, but you may want it watched.
- **Several guesses of mine went into this** (marked ASSUMPTION in the spec): B → A is 0.8 of the strength setting and B → C is a quarter of it (you didn't specify B's effects), a strand can't be picked twice in a row, and pull from neighbors is capped at 1. Changing any of them could move the results.
- **Reaches aren't simulated.** Speak and Listen are placed in weaves but the run only counts strands.

## Suggested next steps (nothing is started)

1. Decide sum versus average for the strand weight (my lean: average).
2. A second, better test of what happens after you speak into a quiet web.
3. Measure the swing order directly (A → B → C → B → A) instead of the autocorrelation stand-in.
4. Then freeze starting numbers for schema draft 6.
