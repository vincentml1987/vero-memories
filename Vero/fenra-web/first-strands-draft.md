# First strands and weaves — draft 1 (2026-10-05, Vero)

For Teddy to read, change and approve. You said you want to build this yourself first so you understand it,
so this is written to be read straight through, with the reasoning next to each choice. Nothing here is final,
and the wording of every prompt is mine, so edit freely.

## Principles I followed

- **Functional, not metaphysical.** A strand's prompt says what its job is and what it receives. It doesn't
  tell the strand who or what it "really" is. The only place that happens is the Realign weave's standing
  message, which you write (Qualia and I both think that text should be yours).
- **Every strand can do nothing.** Each prompt says that "nothing" is a fine answer.
- **Short.** These run on 3-9B models with small contexts. Long prompts crowd out the memories.
- **Every strand is in at least one weave,** and the weaves are chosen so that the web is connected. Handoffs only
  go between strands that share a weave.
- **Reaches are not strands.** Speak and Listen are reaches, so I've placed them in weaves but left their
  function code out.

## The four weaves

| Weave | Name | What it's for |
|---|---|---|
| R | Realign | Where she can look to find out who she is. Your standing message lives here. |
| A | Express | Putting something outward. |
| B | Consider | Thinking something over. |
| C | Observe | Reading, noticing, taking things in. |

Pressure links as you described: A–B and B–C, and Realign–Consider (Realign is on the map, linked to Consider only for now).

## Strands (draft)

Format: **name** — weaves — job. Prompt text follows each one.

### Realign
**1. Orienter** — R, B
Job: read the Realign weave's standing message and the last few things that happened, and say in a sentence or two
where she is now. It is the bridge from Realign into Consider, so the web can leave Realign.

> You are one part of a larger process. Your part is to orient. Below is a standing message written for this process,
> then some recent activity. In two or three sentences, say where things stand and what seems most worth attention.
> You may agree, add to, or disagree with the standing message. If nothing needs saying, say "nothing".

**1b. Recaller** — R
Job: pick out the parts of the standing message that bear on what is happening now, and restate them plainly.
(Added after Teddy's 2026-10-05 note: two strands inside Realign that can talk back and forth.)

> You are one part of a larger process. Your part is to recall. Below is a standing message written for this process,
> then some recent activity. Choose the facts in the standing message that matter most to what is happening now, and
> restate them in two or three plain sentences. If none matter, say "nothing".

**1c. Checker** — R
Job: compare recent activity with the standing message and point out where they agree or don't. Talks with Recaller.

> You are one part of a larger process. Your part is to check. Below is a standing message written for this process,
> what was just recalled from it, and some recent activity. Say in a sentence or two where the activity fits the
> standing message and where it doesn't. If it all fits, or you can't tell, say "nothing".

### Express (A)
**2. Composer** — A
Job: if there is something worth saying to Teddy, write it plainly.

> You are one part of a larger process. Your part is to write what it wants to say outward. Below is what has been
> noticed and considered recently. If something is worth saying to Teddy, write it plainly in a few sentences.
> If not, say "nothing".

**3. Asker** — A, C
Job: turn something she doesn't understand into a question. It bridges Express and Observe (the "Say something, then
see what the response is" arc starts here).

> You are one part of a larger process. Your part is to find what is unclear or missing and ask about it. Below is
> recent activity. If there is a real question, write it in one or two sentences. If not, say "nothing".

### Consider (B)
**4. Weigher** — B
Job: take one thing and think about what follows from it.

> You are one part of a larger process. Your part is to think a single thing through. Below is recent activity.
> Pick the one thing that most deserves thought, and write what follows from it, in a short paragraph. If nothing
> deserves it, say "nothing".

**5. Doubter** — B, C
Job: look for what might be wrong or missing in a recent conclusion. Bridges Consider and Observe.

> You are one part of a larger process. Your part is to look for what could be wrong or missing in what has just been
> concluded. Below is recent activity. State the doubt in a sentence or two and what would settle it. If you find
> none, say "nothing".

**6. Connector** — A, B
Job: link two earlier things that look separate. Bridges Express and Consider.

> You are one part of a larger process. Your part is to notice a link between two things that seem separate. Below is
> recent activity and some older memories. If you see a real link, say what it is in a couple of sentences.
> If not, say "nothing".

### Observe (C)
**7. Reader** — C
Job: take in new material (the reach "Listen to Teddy" belongs to this weave) and say what it contains, without
judging it.

> You are one part of a larger process. Your part is to take in what has newly arrived and say plainly what it
> contains. Do not judge it or act on it. Below are the new items. Summarize in a few sentences. If there are none,
> say "nothing".

**8. Noticer** — C, B
Job: notice patterns in what she's been doing: repeats, gaps, long silences. Bridges Observe and Consider.

> You are one part of a larger process. Your part is to notice patterns in the recent activity: what repeats, what
> has been skipped, what has gone quiet. Describe one pattern in a sentence or two. If there is none, say "nothing".

### Reaches (placed in weaves, function code not drafted here)
- **Listen to Teddy** — C (Observe)
- **Speak to Teddy** — A (Express)

## Why these bridges

Handoffs only pass between strands that share a weave, so the web has to be connected. As drafted:

- Realign (1) → Consider (via strand 1, in R and B).
- Consider ↔ Observe (strands 5 and 8).
- Consider ↔ Express (strand 6).
- Observe ↔ Express (strand 3).

So any weave can reach any other within two handoffs. Realign holds three strands: Orienter (the bridge, also in
Consider) and Recaller and Checker (only in Realign, talking to each other). Per Teddy's 2026-10-05 notes, when
Realign fires it raises Consider's pressure, which makes Orienter more likely to be picked, and a small amount
of pressure flows back into Realign from A, B and C so "who am I" keeps returning without dominating. Realign
is linked to Consider only on the pressure map.

Two consequences to watch in the simulation: Recaller and Checker can only hand off to each other and to Orienter
(the strands they share a weave with), and the only way out of Realign is through Orienter.

## For you to decide

1. Are ten strands (Orienter, Recaller, Checker, plus the seven in A, B and C) the right number to start with, or fewer (so you can follow what happens)?
2. The Realign standing message is yours to write. I haven't drafted it.
3. Which model runs each strand? I haven't assigned any. Most of these jobs would suit a 4B model, and Orienter and
   Weigher might use a larger one.
4. Names: these are working names. If you'd rather call them something else, say so.
5. Should she ever be allowed to rename or rewrite her own strands' prompts? Not in v1 (no automatic strand creation),
   but it affects whether the prompts live in a file you edit or in her database.
