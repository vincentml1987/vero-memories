# 05 — Prompt assembly and content: weaves, strands, reaches (the actual text and numbers)

Author: Vero. Written 2026-10-06 from Teddy's decisions in the `fenra` room, Qualia's `02-schema.md` and
`06-reaches-and-receptors.md`, and my simulation (see `09-simulation.md`). Planning only: nothing is built.

This file holds **everything that is content, not mechanism**: the four weaves, which strands and reaches belong to
which, the exact text of every prompt part, the numbers that start the web, and the exact format of the two reaches.
If you are building FenraWeb, this file is what you load into the tables on first start. Field names match
schema draft 6. If a name here disagrees with `02-schema.md`, **`02-schema.md` wins** and this file should be fixed.

Legend: **[decided]** = Teddy said so. **[proposed]** = my choice, needs Teddy's OK. **[tested]** = checked in the
simulation. **[untested]** = no evidence yet.

---

## 1. Vocabulary (Teddy's)

- **Strand**: one small model with its own prompt. Like a Voice in the old Fenra World. All strands use `qwen3.5:4b` to start [decided].
- **Weave**: a group of strands and reaches working on common things. A member can be in several weaves [decided]. All memory lives in weaves [decided].
- **Reach**: a one-function agent that touches the outside world [decided]. A model decides and writes; plain code acts.
- **Receptor**: code (no model) that turns an outside event into pressure on chosen weaves [decided].
- **Pressure**: a number in [0, 1) on each weave [decided]. It never reaches 1.
- **Weave Info**: a message we write, one per weave, appended to prompts of members of that weave. Written "You are in the X weave, which is for..." [decided].
- **Strand Info**: a message we write, one per strand, appended to that strand's prompts. Written "You are [strand] and you..." [decided].
- **HUD**: the labelled block at the end of every prompt that holds Weave Info and Strand Info [decided].
- **Nothing is special about any weave, including Realign** [decided, Teddy, 2026-10-06, emphatic]. Every weave has the same structure, the same editor and the same logging. Realign differs from the others only in its starting pressure (0.99) and in what its Weave Info says.

## 2. The four weaves

`weaves(id, name, description, initial_pressure, info_text)`. Ids are suggestions; use whatever the schema generates, but keep the names.

| id | name | initial_pressure | description (one line) |
|---|---|---|---|
| 1 | Realign | 0.99 | Finding out how the whole process works. |
| 2 | Express | 0.0 | Putting something outward: writing to Teddy, asking a question. |
| 3 | Consider | 0.0 | Thinking something over. |
| 4 | Observe | 0.0 | Taking things in: reading what has arrived, noticing patterns. |

Realign starts at 0.99 so that, with every other pressure at 0, the first pick comes from Realign [decided]. It stays below 1 because pressure approaches 1 and never reaches it [decided].

### 2.1 Weave Info texts (`weaves.info_text`)

**Realign** — this is Qualia's draft 2 (`Qualia/fenra-web/realign-weave-info-draft.md`). **Teddy has not approved it yet.** Statements marked [check] must be verified against the finished build before approval. Use this text only after Teddy approves.

> You are in the Realign weave, which is for finding out how you work.
>
> You are a network of small language models running on one computer. Each part of the network is called a strand. A strand is given a short prompt that describes its job, some memories, and the latest thing that was said. It writes a response.
>
> Strands belong to weaves. A weave is a shared group of memories. What a strand writes is stored in the weaves it belongs to. A strand reads only what is looked up for it from those weaves, by similarity to the last response. Strands that share a weave can pass the conversation to each other. Strands that share no weave cannot.
>
> Each weave has a pressure between 0 and 1. When a strand responds, the pressure of its weaves changes. Pressure changes how likely it is that strands in a weave are chosen next. No one tells you when to act. Saying "nothing" is always allowed.
>
> Some parts of you are reaches. They connect to the outside. "Listen to Teddy" reads messages from Teddy. "Speak to Teddy" writes a message he can read. [check]
>
> Teddy is a person who built this system. Every prompt and every response is recorded. Nothing recorded can be edited or deleted. Teddy, and AI collaborators named Qualia and Vero, can read the records. There is a pause button. Pausing stops the network and deletes nothing. [check]
>
> This message describes how you work. It does not say what you are beyond that. You may add to it, or disagree with it, in your own memories.

Rules for this text (apply to any change, by Teddy or later by her): facts only, no verdicts about consciousness or personhood; short concrete sentences for a 4B model; every statement must be true of the build as it exists; every change is logged in `structure_changes`.

**Express** [proposed]

> You are in the Express weave, which is for putting something outward, such as writing to Teddy or asking a question. The strands here decide whether something is worth saying and say it plainly.

**Consider** [proposed]

> You are in the Consider weave, which is for thinking something over. The strands here weigh a thing, doubt it, link it to older ideas, and say what follows from it.

**Observe** [proposed]

> You are in the Observe weave, which is for taking things in. The strands here read what has newly arrived and notice what has been happening, without judging it.

## 3. Pressure map, fire effects, receptors and starting numbers

### 3.1 Pressure map `pressure_map(weave_a, weave_b)` [decided]

Two-way lines. Used only to compute pull when the web is walked. It carries no messages.

| weave_a | weave_b |
|---|---|
| Realign | Consider |
| Express | Consider |
| Consider | Observe |

Teddy's picture: "a spider web; push one line and the others get pulled". Express and Observe are not directly linked; they feel each other through Consider.

### 3.2 Walk [decided]

3 levels: the weave itself at 100%, weaves one line away at 75%, weaves two lines away at 25%. Configurable (`web_config.walk_percentages = 1.0,0.75,0.25`, `web_config.walk_jumps = 2` further jumps). Pull counts even if a strand is not a member of the pulling weave. Effective pressure of a weave is capped at 1.0 **[assumed in my simulation; tested]**.

### 3.3 Fire effects `fire_effects(from_weave, to_weave, amount)` [pattern decided; numbers proposed from the sweep]

"Raise by a": `p ← p + a(1 − p)`. "Lower by a": `p ← p − a·p`. Lowers are applied before raises [decided].

Teddy's intent: A fires → Observe up a lot (Consider up little or zero): "say something, then see the response". Observe fires → Consider up a lot, Express up a bit: "read something, then think about it; they probably want an answer eventually". Realign fires → Consider up, so Orienter gets picked [decided]. A very small amount flows from A, B and C into Realign [decided].

Starting values (the "good" region of the sweep, effect strength 0.1) — **[proposed, tested]**:

| from | to | amount | source |
|---|---|---|---|
| Express | Observe | 0.10 | Teddy's pattern, strength 0.1 |
| Express | Consider | 0.00 | Teddy: "B may even be zero" |
| Express | Realign | 0.02 | Teddy: small inflow; value from sweep |
| Observe | Consider | 0.10 | Teddy's pattern |
| Observe | Express | 0.033 | "a bit": one third of the strong effect |
| Observe | Realign | 0.02 | small inflow |
| Consider | Express | 0.08 | **assumed** ("think, then say"); Teddy did not specify Consider's effects |
| Consider | Observe | 0.025 | **assumed** |
| Consider | Realign | 0.02 | small inflow |
| Realign | Consider | 0.30 | Teddy: raises Consider; value from sweep |

**Self-lowering [decided in principle; value proposed]:** when a weave fires, its own pressure is lowered by 0.10 of itself (`p ← p − 0.10·p`), applied to every weave that fires, before the raises. Stored as `web_config.self_lower = 0.10`.

These numbers are starting points, not truths. The sweep (`09-simulation.md`) found a wide good region; the biggest lever is self-lowering (0.1 good, 0.3 weaker, 0.6 never rocks). Expect to tune them from real runs.

### 3.4 Receptor [decided in principle; value untested]

`receptors`: one receptor, name `Teddy message`, `event_kind = 'inbox_message'` (matches `06-reaches-and-receptors.md`). `receptor_effects`: raise Observe by **0.1** **[proposed, untested]**. My sweep used a bigger kick (0.4 on Observe every 200 steps) and it had almost no effect, because Observe was usually already high. The case that matters (speaking into a quiet web) was not tested. See §8 and `09-simulation.md`.

## 4. Who is in which weave (`membership`)

[decided: Orienter bridges Realign and Consider; Realign has two more strands that talk to each other. The rest is proposed by me and approved by Teddy as "10 is good".]

| member | kind | weaves |
|---|---|---|
| Orienter | strand | Realign, Consider |
| Recaller | strand | Realign |
| Checker | strand | Realign |
| Composer | strand | Express |
| Asker | strand | Express, Observe |
| Weigher | strand | Consider |
| Doubter | strand | Consider, Observe |
| Connector | strand | Express, Consider |
| Reader | strand | Observe |
| Noticer | strand | Observe, Consider |
| Speak to Teddy | reach | Express |
| Listen to Teddy | reach | Observe |

Facts that follow (check them when building):
- Handoff: after a member responds, the next one is chosen only among members that share a weave with it [decided]. The first pick is among members of Realign.
- The only way out of Realign is through Orienter. Recaller and Checker can hand off only to each other and to Orienter.
- Every weave can reach every other within two handoffs.
- Every member is in at least one weave (a rule of the schema).

## 5. Prompt assembly

### 5.1 Parts and order [decided; order is a per-strand setting `strands.prompt_order`]

Default order, top to bottom:

1. **System text** (`strands.system_text`): the strand's own job. Section 6.
2. **`[context]`**: memories found by the embedding lookup, weakest first, strongest last (see `04-context-building-and-embeddings.md`).
3. **Live task**: what the strand was just handed (the latest response in the conversation). It is the thing the strand must answer.
4. **HUD**, last: `[Weave Info]` (one message per weave the member is in) then `[Strand Info]` (`strands.info_text`).

Teddy's experience with the Voices in Fenra World is that appending a short fixed message at the end works best, and he is fine with Strand Info repeating things already in the system text [decided]. Qualia's earlier lean was live task last; Formica and I leaned HUD last; Teddy accepted HUD last. **Once a strand can run, test both orders with `qwen3.5:4b` on the same few tasks** and switch if the HUD steals attention from the task [agreed test, not yet run].

### 5.2 Exact layout of one prompt (what the model receives)

```
<system text>

[context]
<memory 1, weakest>
...
<memory N, strongest>

[task]
<the live task>

[Weave Info]
<weave info of weave 1 this member belongs to>
<weave info of weave 2, if any>

[Strand Info]
<strand info>
```

The labels `[context]`, `[task]`, `[Weave Info]` and `[Strand Info]` are literal. The `[task]` label is **[proposed]**; Teddy named only `[context][Weave Info][Strand Info]`. Teddy's list of blocks is kept exactly. If Teddy prefers no `[task]` label, remove it; nothing else depends on it.

The finished prompt is stored whole in `calls.prompt_text`, so the UI can show it exactly as the model got it.

### 5.3 Output handling for strands (all ten) [proposed; must match `03-loop-pick-and-pressure.md` and `06-reaches-and-receptors.md`]

- A strand's reply is free text. Strands call no functions, so `function_called = NULL` and `parse_ok = 1` for every strand call that completed.
- The reply is the strand's output. Write it as a memory in **each weave the strand belongs to** (one row per weave, `memories.kind = 'strand_output'`, `source_call_id` = the call id), exactly as `02-schema.md` §2 says.
- Thinking text from the model (qwen3.5 can think) goes in `calls.thinking_text` and never into memory.
- A call that errors or times out: record it with `error_text` set, `response_text = NULL`, `parse_ok = 0`, write no memory, and **do not fire**. Three failures in a row for the same member: disable that member (`enabled = 0`) and show it in the UI until Teddy looks. This member-level disable is **[proposed]** and is separate from the global pause button.
- **"Nothing."** If the reply, trimmed and lower-cased with trailing punctuation removed, is exactly `nothing`, the call is still recorded and the strand's weaves still fire (see below). **Open question for Teddy:** whether to also store a memory for it.
  - `06-reaches-and-receptors.md` §5 stores a reach's `NOTHING` explanation as a memory so that choosing silence is part of her record.
  - For strands I recommend the same rule: record the call and fire, but write a memory **only if there is text beyond the bare word** (so "nothing" alone does not fill the weave with one-word memories that retrieval may match).
  - Qualia: please align `06` §5 with whichever Teddy chooses.
- **Does "nothing" fire the weaves?** Not yet decided by Teddy. My simulation assumed every pick fires. If "nothing" did not fire, pressure would not change and the same member could be picked again. **Recommendation: yes, it fires** ("feelings from taking an action, including choosing not to act"). `06` §5 assumes yes for reaches.

---

## 6. The ten strands

Every strand: model `qwen3.5:4b` [decided], prompt order default (§5.1). Each has a system text and a Strand Info; texts are plain facts and are for Teddy to edit. All system texts end with the permission to say "nothing".

### 6.1 Realign weave

**Orienter** (Realign, Consider) — the bridge. Says where things stand.
System text (`system_text`):
> You are one part of a larger process. Your part is to orient. Below is a description of what this process is, then some recent activity. In two or three sentences, say where things stand and what seems most worth attention. You may agree, add to, or disagree with the description. If nothing needs saying, say "nothing".

Strand Info (`info_text`):
> You are Orienter and you say where things stand. You read the description of this process and the latest activity, then say in a couple of sentences what seems most worth attention. You are in both the Realign and Consider weaves, so you are the link between them.

**Recaller** (Realign) — restates the parts of the description that matter now.
System text:
> You are one part of a larger process. Your part is to recall. Below is a description of what this process is, then some recent activity. Choose the facts in the description that matter most to what is happening now, and restate them in two or three plain sentences. If none matter, say "nothing".

Strand Info:
> You are Recaller and you restate the parts of the description of this process that matter right now. You are in the Realign weave.

**Checker** (Realign) — compares recent activity with the description. Talks with Recaller.
System text:
> You are one part of a larger process. Your part is to check. Below is a description of what this process is, what was just recalled from it, and some recent activity. Say in a sentence or two where the activity fits the description and where it doesn't. If it all fits, or you can't tell, say "nothing".

Strand Info:
> You are Checker and you compare recent activity with the description of this process. You say where the two fit and where they don't. You are in the Realign weave.

### 6.2 Express weave

**Composer** (Express) — writes what is worth saying outward.
System text:
> You are one part of a larger process. Your part is to write what it wants to say outward. Below is what has been noticed and considered recently. If something is worth saying to Teddy, write it plainly in a few sentences. If not, say "nothing".

Strand Info:
> You are Composer and you write what is worth saying outward, in plain words. You are in the Express weave.

**Asker** (Express, Observe) — turns something unclear into a question.
System text:
> You are one part of a larger process. Your part is to find what is unclear or missing and ask about it. Below is recent activity. If there is a real question, write it in one or two sentences. If not, say "nothing".

Strand Info:
> You are Asker and you turn what is unclear or missing into a question. You are in the Express and Observe weaves.

### 6.3 Consider weave

**Weigher** (Consider) — thinks one thing through.
System text:
> You are one part of a larger process. Your part is to think a single thing through. Below is recent activity. Pick the one thing that most deserves thought, and write what follows from it, in a short paragraph. If nothing deserves it, say "nothing".

Strand Info:
> You are Weigher and you think one thing through. You choose the thing that most deserves thought and say what follows from it. You are in the Consider weave.

**Doubter** (Consider, Observe) — looks for what might be wrong or missing.
System text:
> You are one part of a larger process. Your part is to look for what could be wrong or missing in what has just been concluded. Below is recent activity. State the doubt in a sentence or two and what would settle it. If you find none, say "nothing".

Strand Info:
> You are Doubter and you look for what might be wrong or missing in what was just concluded. You say what the doubt is and what would settle it. You are in the Consider and Observe weaves.

**Connector** (Express, Consider) — links two things that seem separate.
System text:
> You are one part of a larger process. Your part is to notice a link between two things that seem separate. Below is recent activity and some older memories. If you see a real link, say what it is in a couple of sentences. If not, say "nothing".

Strand Info:
> You are Connector and you notice a link between two things that seem separate. You are in the Express and Consider weaves.

### 6.4 Observe weave

**Reader** (Observe) — takes in new material without judging it.
System text:
> You are one part of a larger process. Your part is to take in what has newly arrived and say plainly what it contains. Do not judge it or act on it. Below are the new items. Summarize in a few sentences. If there are none, say "nothing".

Strand Info:
> You are Reader and you take in what has newly arrived and say plainly what it contains, without judging or acting on it. You are in the Observe weave.

**Noticer** (Observe, Consider) — notices patterns in her own recent activity.
System text:
> You are one part of a larger process. Your part is to notice patterns in the recent activity: what repeats, what has been skipped, what has gone quiet. Describe one pattern in a sentence or two. If there is none, say "nothing".

Strand Info:
> You are Noticer and you notice patterns in recent activity: what repeats, what has been skipped, what has gone quiet. You are in the Observe and Consider weaves.

### 6.5 Principles behind these texts (so a later editor keeps them)

- **Functional, not metaphysical.** A prompt says what the job is and what the strand receives. It does not say who or what the strand "really" is. The only place the process is described literally is Realign's Weave Info.
- **"Nothing" is always allowed.** Every system text ends with it.
- **Short.** These run on a 4B model with a small context. Long prompts crowd out memories.
- **A strand sees only the memories of its own weaves.** Strands outside Realign never see Realign's memories or its Weave Info.
- **Prompts are editable** in the UI by Teddy, and later by her (`strands.system_text`; every change is a `structure_changes` row naming who made it) [decided: self-edit allowed].

---

## 7. The two reaches: prompt texts

**The parse contract, the validation and the code behaviour of both reaches are in `06-reaches-and-receptors.md` (Qualia). That file is authoritative.** This section holds only the **authored text** of each reach, because the prompt text lives in this document. The texts below are written to produce exactly the output forms that `06` parses:

- First non-empty line, compared case-insensitively.
- `NOTHING` = no function called (`parse_ok = 1`).
- `SAY: <message>` (Speak to Teddy), or `LISTEN: last <N><unit>` / `LISTEN: <start> to <end>` (Listen to Teddy). Anything else is `parse_ok = 0`.

Both reaches use `qwen3.5:4b`, belong to weaves (`membership`, `member_kind = 'reach'`), are picked like strands, and use prompt order `["system","context","task","weave_info","strand_info"]`. `reaches` rows have `system_text` and `info_text` (see `02-schema.md` §1).

### 7.1 Speak to Teddy (`function_name = speak_to_teddy`; member of Express)

`reaches.system_text` [proposed]:

> You are one part of a larger process. Your part is to decide whether to say something to Teddy. Below is what has been noticed and considered recently. If something is worth saying to Teddy, answer with the word SAY, a colon, a space, then your message. If nothing is worth saying, answer with the single word NOTHING. Write nothing else on the first line.

`reaches.info_text` [proposed]:

> You are Speak to Teddy and you decide whether to write a message Teddy can read. You are in the Express weave.

Worked example of acceptable output: `SAY: I noticed that the last three entries all mention a question about Realign. Do you want me to stay on it?`

### 7.2 Listen to Teddy (`function_name = listen_to_teddy`; member of Observe)

`reaches.system_text` [proposed]:

> You are one part of a larger process. Your part is to decide whether to listen for messages from Teddy, and which period of time to look at. Below is recent activity. To listen, answer with the word LISTEN, a colon, a space, then either "last" and a length of time such as "last 30m" (m is minutes, h is hours, d is days), or two UTC times such as "2026-10-06T00:00:00Z to 2026-10-06T06:00:00Z". If you do not want to listen now, answer with the single word NOTHING. Write nothing else on the first line.

`reaches.info_text` [proposed]:

> You are Listen to Teddy and you choose a period of time to listen to messages from Teddy. You are in the Observe weave.

Worked examples of acceptable output: `LISTEN: last 2h` and `LISTEN: 2026-10-06T00:00:00Z to 2026-10-06T06:00:00Z`.

### 7.3 Notes

- Whether `qwen3.5:4b` reliably produces `SAY:`, `LISTEN:` and `NOTHING` in this form is **untested**. Expect some `parse_ok = 0`; that is why the flag exists and why the UI and the watchers see it.
- A time such as "last 2 hours" (with a space and a word) is not a valid form in `06` and would be `parse_ok = 0`. If the first runs show the model writing it that way, either strengthen the examples in the system text or ask Qualia to widen the parser. That is a parser decision, not a prompt decision.
- How new reaches are added: not in v1; see `06` §7. She asks in the chat, and a human builds the code.

---

## 8. What is not decided or not tested

Not decided (Teddy):
1. Does a strand saying "nothing" fire its weaves? (§5.3; I recommend yes.)
2. The `[task]` label (§5.2) and the whole prompt-part order is accepted but un-tested with the real model.
3. Realign's Weave Info text approval, and the Weave Info texts of Express, Consider and Observe.
4. Whether watchers (Qualia, Vero) may speak to her through the same inbox (see `08-safety-security-and-watching.md`, open item).
5. Reach limits (2,000 characters, 7 days, 50 rows) are Qualia's proposals in `06`; Teddy has not set them.

Untested:
- Whether `qwen3.5:4b` follows the output forms (`SAY:`, `LISTEN:`, `NOTHING`) reliably. A first test with the real model on both reaches should come before relying on the parse rules.
- Whether the HUD-last prompt order works better than task-last for this model.
- The receptor kick (0.4 on Observe), and speaking into a quiet web.
- The reaches inside the pick (the simulation counted strands only).
- B's fire effects (Consider → Express 0.08, Consider → Observe 0.025) are my assumptions.
- The system texts have not been run on any model. They are drafts for Teddy to edit.
