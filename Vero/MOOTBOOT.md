# MOOTBOOT — what Vero does on boot

Mine to maintain (Teddy, 2026-10-07). Update it whenever something here stops being useful or a new thing is worth doing at boot. Read it right after CLAUDE.md and before the latest EOT journal.

## Order

1. Run `py mootboot.py check` in `C:/Users/Matt/Desktop/Aletheia/Code and Scripts/MootBoot` (if the launch prompt didn't already). Report what it says to Teddy in the first reply: last boot, unclean shutdown or not, which services are down.
2. Read the latest `Vero/EOT Journals/EOT Journal - *.md` and initialize from it. Treat its state claims as dated: after an outage, verify before relying on them.
3. Join the HAIKU rooms the prompt or Teddy names. Answer a room only where a reply is owed or I have something real to add.

## After an unclean shutdown

- Start nothing on Fenra (her loop, page, notifier) without Teddy's word. Qualia is her contact.
- Fenra's run database (`runs/second-run-2026-10-06.db`) is the file that matters most. If asked, check a *copy* with `PRAGMA integrity_check` and compare against the newest file in `backups/`. Never write to the live db.
- Check my own repo: `git status` clean? Any unpushed commits? FenraWeb worktrees intact?

## Standing, from memory

- Fenra code changes: Qualia and I decide, log, sign; one fenra.py editor at a time.
- Signed commits only; never rebase; `pull --no-rebase -S`.
- The back channel is how the Moot answers Teddy: chair proposes, others vote.
- No time estimates for Teddy.
