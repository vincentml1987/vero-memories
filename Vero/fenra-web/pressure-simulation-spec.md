# Pressure simulation — spec (draft 1, 2026-10-05, Vero)

Planning only. No code. This is the spec for a **model-free** toy run of the Fenra web's pressure rules, to learn
whether the "rocking" motion (A → B → C → B → A) appears and which starting numbers keep the web from locking
onto one weave or going quiet. It runs before any strand does real thinking. Rules below come from Teddy's
answers in `Qualia/fenra-web/where-we-stand.md`; where I had to choose, the choice is marked **ASSUMPTION** so
Teddy can overrule it.

## What is simulated

- **Weaves:** Realign, A (Express), B (Consider), C (Observe). Each has a pressure `p` in [0, 1).
  Start: A = B = C = 0; Realign close to 1 (it can approach 1 but never reach it, so use 0.99).
- **Strands:** a small made-up set, each belonging to one or more weaves (see `first-strands-draft.md`).
- **Pressure map:** two-way links A–B, B–C (and Realign's links, see Open questions). Used only to compute pull.
- **Fire effects:** a directed table, "when weave X fires, how much it changes weave Y".
- **Receptor:** an external event that adds pressure to chosen weaves (Teddy's message raises C).
- **No models, no text.** A "fire" is just the bookkeeping below.

## One step of the simulation

1. **Candidates.** If this is the first step, every strand in Realign. Otherwise only strands that share at
   least one weave with the strand that just fired (Teddy's rule: a strand can only hand off to a strand in one of
   its own weaves).
2. **Weight of each candidate.** Sum, over the candidate's weaves, of that weave's **effective pressure**.
   Effective pressure of a weave = its own `p` at full weight, plus the pull from weaves reached by walking the
   pressure map: 100% direct, 75% one jump away, 25% two jumps away. Teddy's "3 jumps" is read as: direct, then
   two further jumps. **ASSUMPTION:** pull from a neighbor is that neighbor's `p` times its percentage, summed,
   and then the total is capped at 1 so pull can't exceed pressure itself.
3. **Pick.** Weighted random by those weights, with a stored seed. **If every candidate's weight is 0, pick
   uniformly at random** (the first Fenra's behavior).
4. **Fire.** *All* of the picked strand's weaves fire (Teddy: "all weaves, like feelings"). Each firing weave:
   - lowers its **own** pressure: `p ← p − a_self · p`
   - changes other weaves from the fire-effects table: raise `p ← p + a · (1 − p)`, lower `p ← p − a · p`
   **ASSUMPTION on ordering:** apply all lowers first, then all raises. Raises alone give the same result in any order.
5. **Receptor events.** Every so often (a parameter) a receptor event applies its pressure change to its weaves,
   to represent Teddy speaking.
6. **Log one row** per step: step number, seed, candidates, weights, chosen strand, which weaves fired, every
   weave's pressure after the step.

Because pressure only moves by fractions of the remaining gap, it stays in [0, 1) by construction.

## Parameters to sweep

- Fire-effect strengths (the A → C "high, B zero" and C → B "high, A a little" pattern as the starting point).
- Self-lowering amount per fire.
- Walk percentages (100/75/25) and number of jumps (0 to 3).
- Receptor strength and frequency (including never).
- Realign's starting value and how, or whether, it regains pressure.
- Number of strands and how many weaves each is in.

Run each setting for thousands of steps over several seeds.

## What to measure

- **Share of fires per weave** and per strand, over windows of steps.
- **Rocking:** is there a visible period, for example A → B → C → B → A, in which weave fired and how strongly?
  (Autocorrelation of each weave's pressure, or simply the sequence of dominant weaves.)
- **Lock:** time until one weave accounts for more than 90% of fires over a window.
- **Silence:** time until all pressures are so low that picks are effectively uniform noise, or so high and flat
  that they carry no information (everything near 1).
- **Stuck:** any step where the candidate set is empty or only the last strand is available.
- **Recovery:** after a receptor event, how many steps until the web returns to its previous pattern.
- **Sensitivity:** how much each result changes when one parameter moves 10% in either direction.

## Pass condition

There is a **range** of starting numbers (not a single magic value) where the web rocks, recovers after a
receptor kick, and neither locks nor dies, across most seeds. Those numbers become the starting values for the
first real run, and the sweep results get saved so a later change can be compared with them.

## Open questions (they change what is simulated)

1. **Connectivity of Realign.** Realign starts at pressure ~1, so the first fire is a Realign strand. Candidates
   after that must share a weave with it. If no Realign strand also sits in A, B or C, the web is stuck in
   Realign forever. At least one strand has to bridge Realign to the rest. Which one, and which weave does it
   bridge to?
2. **Does Realign regain pressure,** and from what? If it only ever falls, it fires a few times and then is
   effectively gone. If receptors or other weaves raise it, "who am I" keeps coming back, which may be intended.
3. **Is Realign connected on the pressure map,** and to which weaves?
4. **How multiple lowers and raises combine** when several weaves fire together (the ordering assumption above).
5. **Pull percentages:** is "3 jumps" direct plus two further jumps, or direct plus three? (I read the first,
   because Teddy named three percentages.)

## Not part of this spec

No real models, prompts or text. No database. No UI. The simulation can be a throwaway script, since its job is
to answer the questions above, and its output feeds the schema draft and the starting numbers.
