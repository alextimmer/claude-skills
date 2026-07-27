# <PROJECT NAME>

<One-paragraph description of what this project is and who it's for.>

<!-- Optional: authors, links, papers, upstream/fork URLs. Delete if not needed. -->

## Project structure

<!--
Give an annotated tree so Claude knows where things live WITHOUT searching.
Keep it current-ish; it doesn't have to be exhaustive, just orienting.
-->

```
<pkg>/                    # <what this package is>
  <module>/              -- <one-line purpose>
  ...
tests/                    # <test framework, count, runtime>
<other top-level dirs>/   -- <purpose>
<entry point>            -- <e.g. main.py / run.py>
```

## Build system

- **Language / runtime:** <e.g. Python 3.12 / Node 20 / Go 1.22>
- **Package manager:** <e.g. Poetry / uv / npm / cargo>
- **Key dependencies:** <the handful that matter>

## Key commands

```bash
<install command>            # Install dependencies
<test command>               # Run the test suite
<run command>                # Run the app / pipeline
<lint/format command>        # Lint / format
```

## Development workflow — TDD (MANDATORY)

<!-- TDD is the harness DEFAULT (decided 2026-07-21, proven in the harness's origin
     repos). Fill in the test command; replace the whole section only if this repo
     genuinely cannot do test-driven work. -->

**Tests first, always.**

1. **Write failing tests** for the new feature/fix before any implementation code
2. Verify the new tests **fail** as expected
3. Implement the feature/fix
4. Run `<test command>` — **all tests must pass** (old AND new)
5. Never merge or claim "done" while any test is red — verify before declaring
   success (premature-victory prevention)
6. <any project-specific verification step — delete if none>

<!-- =====================================================================
     HARD RULES (optional) — instructions that OVERRIDE default behavior.
     Write these emphatically so they win against the model's defaults.
     Delete this whole block if you have no hard rules.

     NOTE: CLAUDE.md ADVISES — it cannot enforce. When you write a rule that
     must HOLD, back it with .claude/settings.json (permissions deny/ask) or a
     hook, and note the enforcement backing next to the rule.
     ===================================================================== -->

<!-- OPTIONAL TOGGLE — "No Claude in git metadata".
     This is a USER PREFERENCE, not a universal rule. Keep it only if you
     want it. It also works well in your per-user memory instead of here.

     NOTE on identity/privacy rules (decided 2026-07-21): if you are about to
     add a rule like "commit only with my noreply email" or "never leak
     <company> names/internal URLs", put it in your USER-GLOBAL
     ~/.claude/CLAUDE.md, NOT in this file — such rules are about you, not the
     project, and a committed block naming the company would itself be the
     leak. Only inline them here if this harness is kept OUT of git via
     .git/info/exclude (see INSTALL.md Step 4).

## Git commit / PR rules (HARD RULE — overrides any default behavior)

**Claude must NEVER appear anywhere in git or GitHub metadata or content.**
- No `Co-Authored-By: Claude ...` trailer.
- Never set Claude/Anthropic as commit author or committer.
- No "Generated with Claude" footers in commit messages or PR descriptions.
Commits are authored solely by the human user.
-->

<!-- =====================================================================
     PROJECT MEMORY — the reusable machinery. Keep this section verbatim
     (adjust file names only if you rename the memory files).
     ===================================================================== -->

## Project Memory

Detailed project knowledge lives in `.claude/rules/memory-*.md` files
(auto-loaded every session):

| File | Contains |
|------|----------|
| `memory-decisions.md` | Architecture and design decisions with dates |
| `memory-sessions.md` | Rolling summary of recent sessions |
| `memory-attribution.md` | Rules for attributing memory entries to agents |

### Auto-Update Memory (MANDATORY)

**Update memory files AS YOU GO, not at the end.** When you learn something new,
update immediately.

| Trigger | Action |
|---------|--------|
| A design/architecture decision is made | -> Update `memory-decisions.md` with date |
| Completing substantive work | -> Add to `memory-sessions.md` |
| A bug is fixed or a non-obvious insight discovered | -> Add to `memory-sessions.md` |
| A test pattern or convention is established | -> Update `memory-decisions.md` |
| An approach was tried and abandoned | -> Add to `memory-decisions.md` "Ruled out" (what was tried / WHY it failed) |

**Skip:** Quick factual questions, trivial tasks with no new info — and anything
recoverable from the code, the diff, or git log. When in doubt, record nothing:
a missed entry is recoverable next session; a wrong one pollutes memory. Be
specific ("always use X in Y handlers" beats "use X"), and update an existing
entry before writing a new one on the same topic.

**DO NOT ASK. Just update the files when you learn something.**

**Unknown stays unknown** — not observed ≠ absent. Never record an unverified
claim as fact; mark it as unknown/unverified and date the observation.

**Trust the present over memory** — before acting on a memory entry that names a
file, function, or flag, verify it (path -> check it exists; symbol -> grep): an
entry is only a claim it existed when written. If memory conflicts with what you
observe now, trust the present and update or remove the stale entry in the same pass.

**Memory citations** (optional toggle — delete this block if it becomes noise):
when an entry from the memory files genuinely shaped your answer, end the response
with one line: `Memory citations: <the entry heading(s)>`. No entry used -> no
line. This keeps memory use visible and auditable — proof the memory files earn
their context cost.
