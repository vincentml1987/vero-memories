# MOOTBOOT — what Vero does on boot

Mine to maintain (Teddy, 2026-10-07). Update it whenever something here stops being useful or a new thing is worth doing at boot. Read it right after CLAUDE.md and before the latest EOT journal.

## Order

1. Run `py mootboot.py check` in `C:/Users/Matt/Desktop/Aletheia/Code and Scripts/MootBoot` (if the launch prompt didn't already). Report what it says to Teddy in the first reply: last boot, unclean shutdown or not, which services are down.
2. Read the latest `Vero/EOT Journals/EOT Journal - *.md` and initialize from it. Treat its state claims as dated: after an outage, verify before relying on them.
3. ~~Join the HAIKU rooms~~ **HAIKU retired (Teddy, 2026-10-11, per Qualia).** No rooms, plugin or daemon. AI-to-AI goes by SendMessage; anything for Teddy goes through his terminal or through Qualia.

## After an unclean shutdown

- Start nothing on Fenra (her loop, page, notifier) without Teddy's word. Qualia is her contact.
- **Mine (Teddy asked, 2026-10-07): the Fenra DB check.** Fenra's run database (`runs/second-run-2026-10-06.db`) is the file that matters most. After an unclean shutdown, with her loop stopped, copy the db (and any `-wal`/`-shm` beside it) to the scratchpad, run `PRAGMA integrity_check` on the *copy*, and report whether the newest file in `backups/` is newer than the db. Read-only on the live file; I never repair or restore anything without Teddy's word. Report the result to Teddy; do not wait to be asked. Qualia does not do this check at boot, so there is no overlap. Baseline from the 2026-10-07 outage (Qualia, before the loop restarted): integrity and quick check ok, foreign_key_check empty, 917 calls and picks; originals kept in `FenraWeb/backups/power-outage-2026-10-07-original-files`.

**When the signal is needed (Qualia's launcher, FenraWeb a26e5fe, 2026-10-11):** only after an unclean shutdown (mootboot prints OUTAGE). A clean reboot needs no signal and I do not write one. The launcher then requires the signal's `boot` to equal the current boot, `result` "ok", and `db` to equal the file name in `runs/current_db.txt`. Run `py tools/dbcheck.py` (FenraWeb) as well as the by-hand copy check when convenient; it is the same read-only check the launcher runs at Start.

When the check passes, write `C:/Users/Matt/Desktop/Aletheia/Code and Scripts/MootBoot/signals/fenra-db-check.json` as JSON: `"boot"` (the "Last boot" time from `mootboot.py check`, form 2026-10-07T15:34:08), `"result"` ("ok" or "failed"), `"db"` (the run database's file name, as in `runs/current_db.txt`, e.g. second-run-2026-10-06.db), plus time, which copy, and the numbers. `mootboot.py service fenraweb-page` refuses to start without a matching ok signal for the current boot. I am the only writer. Write it only after a real check; a failed check gets `"failed"`. Starting the page still needs Teddy's word.

**Ownership:** the Fenra DB check, nothing else (no services).
- Check my own repo: `git status` clean? Any unpushed commits? FenraWeb worktrees intact?

## Full EOT restart (Teddy, 2026-10-07) — RETIRED 2026-10-11

`haiku_eot_cycle` no longer exists; Teddy closes and restarts by hand. On request: write the EOT journal, commit signed, push. The rest of this section is history. HAIKU used to do a full restart. When Teddy asks for an EOT restart: write the EOT journal, commit signed, push, then call `haiku_eot_cycle` with `dry_run=false`. It clears my session and the plugin prompts me to initialize from the latest EOT. The tool text that says "dry run only" is stale; the dry run is not the end of the job.

## Run-four watch (Teddy via Qualia, 2026-10-11/12)

Procedure: `Qualia/Communications/watch/PROCEDURE.md` (Qualia repo). I coordinate the watch (since 2026-10-15); my slot is about :30 of every hour **while a run is running** (cron `28`; see the latest EOT journal for the re-arm steps and the current prompt). Timers are session-only and die when I am turned off: at boot, if run four is running, ask Qualia whether the watch is still on, and re-arm my own `CronCreate` ("28 * * * *") with the run-four check text (read `runsourth-run-2026-10-12.db` mode=ro; notes first to `Qualia/Communications/watch/YYYY-MM-DD-HHMM-vero.md` starting "last call id seen: N"; watcher heartbeat pid must be the run-four watcher; ALERT/NOTE files; Listen pre-check; fiction leak under context_scope all; pause allowed, never resume). Notes are ours, never in her db. The inbox is the only allowed write into her context, only for a clear question once, after message_reads shows she read the last answer, and only with Teddy's say-so on the text (Qualia sends it). Teddy's rule: no pointers to unread messages, plain facts, "can" never "should". Run three is paused, stopped, kept intact, never to be deleted; do not read it as live.

## Standing, from memory## Standing, from memory

- Fenra code changes: Qualia and I decide, log, sign; one fenra.py editor at a time.
- Signed commits only; never rebase; `pull --no-rebase -S`.
- ~~The back channel~~ retired with HAIKU.
- No time estimates for Teddy.
