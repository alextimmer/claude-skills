# Installing the Claude Code Harness in a fresh repo

This installs the memory + hook system from `./template/` into any repository. Budget
~15 minutes. Read `README.md` first if you want the *why*; this is the *how* — for
humans. To have Claude install it for you instead, install the plugin once
(`/plugin marketplace add alextimmer/claude-skills`, then
`/plugin install claude-memory-harness@claude-skills`) and say "install my harness" in any
repo (the skill's `references/install-procedure.md` mirrors these steps).

## What you're installing

```
<repo>/
  CLAUDE.md                          # standing instructions, auto-loaded every session
  .claude/
    settings.json                    # wires up the SessionStart + PreCompact + Stop hooks (timeout 10s each)
    settings.README.md               # (optional) explains settings.json; not loaded by Claude
    hooks/
      session-context.sh             # SessionStart: repo state + cap audit + advisories + post-compact flush
      pre-compact.sh                 # PreCompact: block-once save-gate before compaction
      memory-reminder.sh             # Stop: block-once memory reminder
      secret-scan.sh                 # utility (not a hook): scan memory files before committing
      selftest.sh                    # machine-checks hooks + scan (33 checks)
    rules/
      README.md                      # note on how this folder auto-loads
      memory-attribution.md          # the [Agent] heading convention
      memory-decisions.md            # durable decisions (seeded, mostly empty)
      memory-sessions.md             # rolling work log (seeded, mostly empty)
```

## Step 1 — Copy the template

```bash
# from the repo you want to set up (adjust the source path to your clone of this
# plugin — or, if the plugin is installed, to its cache under ~/.claude/plugins/)
cp    /path/to/claude-memory-harness/template/CLAUDE.md     ./CLAUDE.md
cp -r /path/to/claude-memory-harness/template/.claude       ./.claude
```

> The `.claude/settings.README.md` file is documentation, not config — Claude does not
> load it. Keep it or delete it; it won't affect behavior.

## Step 2 — Fill in `CLAUDE.md`

Open `CLAUDE.md` and replace every `<PLACEHOLDER>`:

- `<PROJECT NAME>` and the description.
- The **Project structure** tree (annotate the real directories).
- **Build system** and **Key commands** (the exact install/test/run/lint commands).
- **Development workflow** — ships as **TDD (MANDATORY)** by default; fill in the test
  command. Replace the section only if the repo genuinely cannot do test-driven work.
- **Hard rules** — delete the block if you have none. The "No Claude in git metadata"
  block is an **optional toggle**: keep it only if that's your preference (or move it to
  per-user memory instead — see Step 6).

**Do NOT edit** the `## Project Memory` section or the two tables inside it — that is the
reusable machinery. Change file names there only if you rename the memory files.

## Step 3 — Seed the first memory entries

The seeded `memory-decisions.md` and `memory-sessions.md` contain one example entry
each, under a fenced explanatory comment. Do this:

1. Leave the `<!-- ... -->` header comment (it documents the file's purpose).
2. Replace the `## YYYY-MM-DD: <Example ...>` block with a real first entry, e.g.:

   In `memory-decisions.md`:
   ```
   ## 2026-07-20: Adopted the Claude Code harness [Your Name]
   - Decision: use CLAUDE.md + .claude/rules memory + Stop-hook reminder.
   - Why: keep project context and lessons persistent across stateless sessions.
   ```

   In `memory-sessions.md`:
   ```
   ## 2026-07-20: Harness installed [Your Name]
   ### What was done
   - Copied CLAUDE.md + .claude/ into the repo, filled in project specifics.
   ### Next steps
   - Update memory as work happens.
   ```

3. Confirm the attribution format matches `memory-attribution.md`:
   `## YYYY-MM-DD: Description [Agent Name]`.

## Step 4 — Decide: track it, or keep it local

This is the most important choice, and it is easy to get subtly wrong (the harness's
own origin repo kept it **out** of git via `.git/info/exclude`, making it single-user
despite its docs saying "tracked"). Pick deliberately:

- **Team-shared (recommended for teams):** commit the files so every clone gets them.
  Scan the memory files for secrets first — they are the easiest place to leak a token:
  ```bash
  bash .claude/hooks/secret-scan.sh   # exit 0 = clean
  git add CLAUDE.md .claude/
  git commit -m "Add Claude Code harness (memory + Stop hook)"
  ```
  Make sure nothing excludes them. Check with:
  ```bash
  git check-ignore -v CLAUDE.md .claude/ || echo "not ignored — good, will be tracked"
  ```
  If they show up as ignored, edit `.gitignore` **and** `.git/info/exclude` to remove
  the entries.

- **Local / single-user:** if you do *not* want them committed, add them to
  `.git/info/exclude` (local, not shared):
  ```bash
  printf '\nCLAUDE.md\n.claude/\n' >> .git/info/exclude
  ```

> **`.gitignore` vs `.git/info/exclude`** — both occur in the wild, and they are not
> interchangeable: `.gitignore` is itself committed, so every clone ignores the paths
> (a team-visible, team-imposed choice); `.git/info/exclude` is per-clone and invisible
> to everyone else. For a company/shared repo where the harness is your *personal*
> tooling, `info/exclude` is the right tool — a `.gitignore` entry would advertise and
> impose the exclusion on the whole team.

> **Hybrid option — `CLAUDE.local.md`:** if the harness IS team-shared but you want
> *personal* project notes on top, Claude Code also auto-loads a gitignored
> `CLAUDE.local.md` next to the committed `CLAUDE.md`. Same idea as
> `.claude/settings.local.json` for personal settings overrides.

> Note: if you keep the template under a `scratch/`-style ignored folder, the *template
> copies* won't be tracked, but the *installed* copies at the repo root and `.claude/`
> are what matter — handle those per the choice above.

## Step 5 — Verify the hooks fire

1. **Self-test** (no Claude needed) — machine-checks all three hooks against simulated
   payloads and transcripts:
   ```bash
   bash .claude/hooks/selftest.sh
   # -> ... 33 passed, 0 failed
   ```
2. **Confirm Claude Code loads them:** open an interactive Claude Code session in the
   repo and run `/hooks`. `SessionStart`, `PreCompact`, and `Stop` should all be
   listed. (Restart the session if you added the files while one was open — settings
   load at session start.)
3. **Live SessionStart check:** start a new session — the model's context should begin
   with the "Session-start repo state" block (branch, changes, recent commits, Open
   TODOs pointer).
4. **Live Stop check:** run a session where Claude fixes something, and let it end its
   turn without updating memory. Claude should get ONE forced extra turn telling it to
   update `memory-sessions.md`, do the update, and then stop cleanly. Sessions where
   memory was already updated as-you-go end silently — that is the intended quiet path.
5. **Live compaction check (optional):** in a longer session, run `/compact`. If
   memory wasn't updated in the last 2 minutes, the PreCompact save-gate first blocks
   ONCE with a "record before compaction" demand; after Claude saves (or continues),
   compaction proceeds and the post-compaction memory-flush block appears ("Context
   was just compacted..." with the path to the full pre-compact transcript).
6. **Vocabulary check (important):** the `STRONG_PATTERNS` in `memory-reminder.sh` are
   phrases tuned to avoid collisions (e.g. a repo full of `fixed-width` identifiers must
   not match `fixed`). Skim your repo's domain vocabulary against the pattern list and
   tune it — see `settings.README.md`. Re-run the self-test after tuning.

## Step 6 — (Optional) per-user rules instead of repo rules

For preferences you do NOT want committed to a shared repo (e.g. the git-metadata rule,
personal style choices), use Claude Code's built-in per-user memory rather than
`CLAUDE.md`. Ask Claude to "remember" it, or add it under
`~/.claude/projects/<project-slug>/memory/`. This is scoped to you and never enters the
repository. See `README.md` §5 for the full repo-level vs. per-user comparison.

## Step 7 — (Optional) user-global safety baseline & companion plugins

Two things that pair well with the harness but deliberately live OUTSIDE the template:

1. **Safety baseline in `~/.claude/settings.json`** (user-global, like the identity
   rules from Step 6 — CLAUDE.md can only *advise*; `permissions` actually enforce):
   ```json
   {
     "permissions": {
       "deny": [
         "Read(./.env*)",
         "Read(~/.ssh/**)",
         "Read(~/.aws/credentials)"
       ],
       "ask": [
         "Bash(git push*)",
         "Bash(git reset --hard*)"
       ]
     }
   }
   ```
   Useful external utilities for building/validating these rules: the "Claude Code
   Settings and Permissions Builder and Linter" and the "Hooks Configuration Builder"
   at <https://hidekazu-konishi.com/tools/> (client-side only, no data leaves the
   browser). `/fewer-permission-prompts` in an interactive session can propose an
   allowlist from your own history.

2. **Companion plugins** — if the repo's workflow depends on a plugin (e.g. the
   superpowers skills reinforcing the TDD-MANDATORY workflow), declare it in the
   project `settings.json` so teammates get prompted to install it. Snippet and
   caveats: `template/.claude/settings.README.md`, "declaring companion plugins".

## Done — how to use it day to day

- Start any session: the model already sees `CLAUDE.md` + all `.claude/rules/*.md`.
- As you work and learn something, **write it into the right memory file immediately**
  (decisions = durable, sessions = the running log) — don't wait for the end.
- At session end, the Stop hook reminds you if it detects a fix/discovery you may not
  have recorded.
- Periodically prune stale `memory-sessions.md` entries; promote any that turned out
  durable into `memory-decisions.md`.
