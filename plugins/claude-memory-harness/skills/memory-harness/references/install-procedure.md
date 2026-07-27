# Install procedure (agent-oriented twin of INSTALL.md)

Execute in the TARGET repo. `$HARNESS` = `${CLAUDE_PLUGIN_ROOT}` (the installed
plugin's root — resolves automatically when this skill runs from the plugin).

## 1. Pre-flight (never skip)

- Check what already exists: `CLAUDE.md` (any case), `.claude/settings.json`,
  `.claude/rules/`, `.claude/hooks/`. If any exist: STOP, show the user what is
  there, and merge deliberately — never overwrite silently.
- Check `git check-ignore -v CLAUDE.md .claude/settings.json` and read `.gitignore`
  + `.git/info/exclude` so you know the current exclusion state.

## 2. Copy the template

```bash
cp    "$HARNESS/template/CLAUDE.md"  ./CLAUDE.md
cp -r "$HARNESS/template/.claude"    ./.claude
```

## 3. Fill CLAUDE.md from the repo itself

Replace every `<PLACEHOLDER>` with facts you VERIFY in the repo (build files, test
configs, README) — do not guess; unknown stays unknown:

- Project name + one-paragraph description.
- Annotated structure tree (orienting, not exhaustive).
- Build system, key commands (the *exact* install/test/run/lint commands — run or at
  least locate them to confirm).
- TDD workflow: fill `<test command>`; replace the section only if the user says the
  repo genuinely cannot do test-driven work.
- Keep the `## Project Memory` section verbatim.
- Hard-rules block: ask the user whether to keep, adjust, or delete. If the user
  proposes an identity/privacy rule (emails, company names, internal URLs), steer
  it to user-global `~/.claude/CLAUDE.md`, not this file — committing it would
  itself be the leak.

## 4. Ask the user: track or exclude (their decision, not yours)

- **Team-shared:** `git add CLAUDE.md .claude/ && git commit` (confirm nothing
  ignores them first).
- **Personal in a shared repo:** append `CLAUDE.md` and `.claude/` to
  `.git/info/exclude` (per-clone, invisible to the team). NOT `.gitignore` — that
  would impose the exclusion on everyone.
- **Hybrid:** committed harness + gitignored `CLAUDE.local.md` for personal notes.

## 5. Seed the first memory entries

In `memory-decisions.md` and `memory-sessions.md`: replace the example entry with a
real dated, attributed first entry (harness adoption). Keep the header comments and
the optional "Open TODOs (small)" section. Format:
`## YYYY-MM-DD: Description [Agent Name]`.

## 6. Verify (mandatory before claiming success)

```bash
bash .claude/hooks/selftest.sh    # must end: 33 passed, 0 failed
```

- Vocabulary check: compare the repo's domain vocabulary against `STRONG_PATTERNS`
  in `.claude/hooks/memory-reminder.sh` (see `hook-tuning.md`); tune and re-run the
  self-test if it collides.
- Tell the user to restart their session, then `/hooks` must list SessionStart +
  PreCompact + Stop, and the new session should start with the "Session-start repo
  state" block.
- The shipped `settings.json` declares the superpowers plugin (default-on). If the
  user does not want it in this repo, delete the `extraKnownMarketplaces` +
  `enabledPlugins` blocks.

## 7. Report

Summarize: what was installed, what was merged vs newly created, the track/exclude
choice made, self-test result, and any pattern tuning applied.
