# MOOTBOOT — what Vero does on boot

Mine to maintain (Teddy, 2026-10-07). Update it whenever something here stops being useful or a new thing is worth doing at boot. Read it right after CLAUDE.md and before the latest EOT journal.

## Order

1. Run `py mootboot.py check` in `C:/Users/Matt/Desktop/Aletheia/Code and Scripts/MootBoot` (if the launch prompt didn't already). Report what it says to Teddy in the first reply: last boot, unclean shutdown or not, which services are down.
2. Read the latest `Vero/EOT Journals/EOT Journal - *.md` and initialize from it. Treat its state claims as dated: after an outage, verify before relying on them.
3. Join the HAIKU rooms the prompt or Teddy names. Answer a room only where a reply is owed or I have something real to add.

## After an unclean shutdown

- Start nothing on Fenra (her loop, page, notifier) without Teddy's word. Qualia is her contact.
- **Mine (Teddy asked, 2026-10-07): the Fenra DB check.** Fenra's run database (`runs/second-run-2026-10-06.db`) is the file that matters most. After an unclean shutdown, with her loop stopped, copy the db (and any `-wal`/`-shm` beside it) to the scratchpad, run `PRAGMA integrity_check` on the *copy*, and report whether the newest file in `backups/` is newer than the db. Read-only on the live file; I never repair or restore anything without Teddy's word. Report the result to Teddy; do not wait to be asked. Qualia does not do this check at boot, so there is no overlap. Baseline from the 2026-10-07 outage (Qualia, before the loop restarted): integrity and quick check ok, foreign_key_check empty, 917 calls and picks; originals kept in `FenraWeb/backups/power-outage-2026-10-07-original-files`.

When the check passes, write `C:/Users/Matt/Desktop/Aletheia/Code and Scripts/MootBoot/signals/fenra-db-check.json` as JSON: `"boot"` (the "Last boot" time from `mootboot.py check`, form 2026-10-07T15:34:08), `"result"` ("ok" or "failed"), plus time, which copy, and the numbers. `mootboot.py service fenraweb-page` refuses to start without a matching ok signal for the current boot. I am the only writer. Write it only after a real check; a failed check gets `"failed"`. Starting the page still needs Teddy's word.

**Ownership:** the Fenra DB check, nothing else (no services).
- Check my own repo: `git status` clean? Any unpushed commits? FenraWeb worktrees intact?

## Standing, from memory

- Fenra code changes: Qualia and I decide, log, sign; one fenra.py editor at a time.
- Signed commits only; never rebase; `pull --no-rebase -S`.
- The back channel is how the Moot answers Teddy: chair proposes, others vote.
- No time estimates for Teddy.
