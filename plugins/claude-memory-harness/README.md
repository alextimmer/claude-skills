# The Claude Code Harness

A small set of plain files that turn a fresh, stateless Claude Code session into one
that **arrives already knowing the project** and **leaves the project a little better
documented than it found it.** No build step, no tooling — anyone can install it by
copying `template/` into a repo (see `INSTALL.md`). Installing this plugin adds the
`memory-harness` skill on top, so Claude can do that copy for you:

```bash
/plugin marketplace add alextimmer/claude-skills
/plugin install claude-memory-harness@claude-skills
# then, in any repo: "install my harness"
```

The *installed* harness is plain committable files in the target repo — it keeps
working even without this plugin.

**Requirements:** the hooks are plain `bash` + `grep` + `sed` scripts (`jq` NOT
needed). **Linux/macOS:** nothing to install — Claude Code runs hook commands via
`sh`/bash there. **Windows:** install Git for Windows; when Git Bash is present,
Claude Code uses it as the default hook shell, and these hooks just work. Without
Git Bash, Claude Code falls back to PowerShell and these hooks will NOT run. If Git
Bash lives in a non-standard location, point Claude Code at it via the
`CLAUDE_CODE_GIT_BASH_PATH` env setting.

It has three moving parts:

1. **`CLAUDE.md`** — the standing instructions, loaded into every session.
2. **`.claude/rules/*.md`** — the project memory, also auto-loaded every session.
3. **`.claude/settings.json` + `.claude/hooks/`** — three hooks closing the loop: a
   SessionStart hook that orients the model (initialization phase), a PreCompact
   save-gate that makes memory get written BEFORE compaction discards the details,
   and a Stop hook that makes sure lessons get written down before a session ends.

Everything else is convention: *how* memory entries are written and kept current.
Together they form a small closed-loop working system around the model: orient →
work → record → verify.

**Scope (deliberate):** this harness solves exactly one problem — memory persistence
and working discipline. Orchestration content (agent teams, task decomposition,
QA-agent guides, design-pattern catalogs) is off-mission and stays out; anything of
that kind becomes a **sibling plugin** in this repo's `plugins/` folder — never a
passenger inside the harness. That boundary is what keeps it installable in any repo
without baggage.

---

## Plugin layout — what is what

Only `template/` is ever installed into a target repo. Everything else is either the
installer skill or documentation *about* the harness.

| Path | Role |
|------|------|
| `template/` | **The harness** (the product). All consolidation decisions are baked in here |
| `skills/memory-harness/` | The install/maintenance skill: compact `SKILL.md` + on-demand `references/` (progressive disclosure). Ships with the plugin — "install my harness" works in any repo. Finds the template via `${CLAUDE_PLUGIN_ROOT}` |
| `INSTALL.md` | Human-readable install guide (the skill's `references/install-procedure.md` is the agent-oriented twin) |
| `DECISIONS.md` | Every design choice and WHY it won (the distilled rationale) |
| `.claude-plugin/plugin.json` | Plugin manifest for the `claude-skills` marketplace at this repo's root |

```
template/
  CLAUDE.md                      -> becomes <target-repo>/CLAUDE.md
  .claude/
    settings.json                -> hooks wiring + superpowers plugin declaration
    settings.README.md           -> explains settings.json + hooks (docs, not loaded)
    hooks/
      session-context.sh         -> SessionStart: orientation + cap audit + advisories + post-compact flush
      pre-compact.sh             -> PreCompact: block-once save-gate before compaction
      memory-reminder.sh         -> Stop: block-once memory reminder
      secret-scan.sh             -> utility (not a hook): scan memory files before committing
      selftest.sh                -> machine-checks hooks + scan (33 checks)
    rules/
      README.md                  -> how this folder works
      memory-attribution.md      -> the [Agent] heading convention
      memory-decisions.md        -> seed: durable decisions
      memory-sessions.md         -> seed: rolling session log (+ optional Open TODOs)
```

---

## 1. Philosophy — why this exists

A Claude Code session is stateless. When it ends, everything the model figured out —
the non-obvious gotcha, the reason a design went one way and not the other, the
command that finally worked — evaporates unless it was written into a file the *next*
session will read. Left alone, every session re-derives the same context from scratch
and re-makes the same mistakes.

The harness fixes that by treating the repo itself as the model's long-term memory —
the **repository as the system of record**:

- **`CLAUDE.md` is the "onboarding doc."** Stable facts that are true across sessions:
  what the project is, how to build/test it, the hard rules, the workflow.
- **`.claude/rules/` is the "lab notebook."** A running, dated, attributed log of what
  was decided and what was learned — updated *as work happens*, not at the end.
- **The Stop hook is the "did you write it down?" safety net.** It inspects the session
  transcript and, if it detects a fix/discovery that was never written to memory, makes
  the model record it before stopping.

The guiding principle, stated in `CLAUDE.md` itself: **"Update memory files AS YOU GO,
not at the end. When you learn something new, update immediately."** Memory deferred to
the end of a session is memory that gets lost when the session is interrupted.

---

## 2. The files, and how each is loaded

### `CLAUDE.md` (repo root) — loaded every session, automatically

Claude Code reads `CLAUDE.md` from the working directory (and parent dirs) at the start
of every session and injects it as high-priority project instructions. The template
contains:

- **Project identity** — one-paragraph description, links.
- **Project structure** — an annotated file tree so the model knows where things live
  without searching.
- **Build system & key commands** — the exact commands to install, test, run.
- **Development workflow — TDD (MANDATORY)** — the harness default: failing tests
  first → verify red → implement → full suite green → never done while red. Replace
  only if a repo genuinely cannot do test-driven work.
- **Hard rules (optional)** — instructions that *override default behavior*, written
  emphatically so they win against the model's built-in habits. Identity/privacy rules
  (commit email, company-name leaks) belong in your user-global `~/.claude/CLAUDE.md`
  instead — see the note in the template.
- **A "Project Memory" section** — the pointer to `.claude/rules/*.md` and, crucially,
  the **auto-update triggers table** (§4). This is the machinery that makes the memory
  self-maintaining, and it is the part most worth keeping verbatim.

### `.claude/rules/*.md` — also loaded every session, automatically

Claude Code auto-loads every `.md` file under `.claude/rules/` as additional project
context. This folder is the memory system — three files, each with a distinct job
(the **taxonomy**, §3). Splitting by lifecycle instead of keeping one monolithic
instruction sheet is deliberate (**modular instruction design**): each file can be
pruned, promoted, or tuned independently. Because they auto-load, anything in them is context the next
session sees for free. That is also why they must be curated: everything here is paid
for in every session's context budget, so entries should be signal, not noise.

### `.claude/settings.json` + `.claude/hooks/` — orientation and safety net

`settings.json` (strict JSON, no comments) registers three hooks and delegates the
logic to commented, testable scripts (every entry carries a 10s timeout; a hung hook
must never stall a session).

**`session-context.sh` (SessionStart — the initialization phase):** its stdout is
injected directly into the model's context at session start — one of the few events
where model-facing injection is native. It prints a short orientation block: current
branch, uncommitted-change count, last three commits, and a pointer to the "Open TODOs
(small)" micro-backlog. Kept deliberately short — injected context is paid for every
session. The same script also handles the **post-compaction memory flush**: SessionStart
re-fires mid-session after auto-/manual compaction (`source: "compact"`), and the script
then nudges the model to persist any un-recorded lessons — pointing at the full
pre-compact transcript that survives on disk, since the compact summary is lossy.

**`memory-reminder.sh` (Stop — the safety net):** the design, in one paragraph:

When Claude finishes a response, the script reads the session transcript (from the
`transcript_path` in the hook payload) and checks two things: did the session contain
lesson-signals (phrase patterns like "fixed the …", "turns out", "root cause",
"breaking change"), and were the memory files updated? If a lesson happened and memory
was NOT touched, it **blocks the stop once** with a model-facing instruction to update
`.claude/rules/memory-*.md` — Claude performs the update (or judges there is nothing to
record) and stops on the next turn. Three guards keep it from nagging: it never blocks
twice in a row (`stop_hook_active`), at most once per session (marker file), and stays
silent whenever memory was already maintained as-you-go — the normal path is zero
friction.

**`pre-compact.sh` (PreCompact — the save-gate):** compaction is the other moment
context gets lost. This hook blocks compaction ONCE per session when
`memory-sessions.md` is stale (>120s) or over its size caps, giving the model one
turn to record/prune while the details are still in context — then compaction
proceeds unconditionally (the once-per-session marker is the anti-wedge guarantee).
The post-compaction flush in `session-context.sh` stays as backstop.

All hooks are machine-checked: `bash .claude/hooks/selftest.sh` runs 33 branch tests
against simulated payloads and transcripts — "written" does not equal "working". Full
explanation, tuning guide (incl. vocabulary-collision warnings), and verification:
`template/.claude/settings.README.md`. History of why the original advisory design was
replaced: `DECISIONS.md`.

> **Compaction is covered** (resolved): the memory flush rides the post-compact
> `SessionStart` re-fire (`source: "compact"`) rather than a `PreCompact` hook —
> PreCompact's only capability is *blocking* compaction, which is the wrong tool.
> Rationale and the verified event facts: `DECISIONS.md` (row 34).

---

## 3. The memory taxonomy — decisions vs. sessions vs. attribution

The split across three files is deliberate. Each answers a different question and has a
different lifecycle.

### `memory-decisions.md` — "why is it this way?" (durable)

Long-lived architectural and design decisions, each dated: pattern choices, dependency
choices, conventions, and the *reasoning* behind them — what you'd want a new engineer
to read before touching the codebase. Entries here **age slowly**.

Write here when: a design/architecture decision is made, a convention or test pattern
is established, or a non-obvious constraint is discovered that will shape future work.

### `memory-sessions.md` — "what happened, and what did we learn?" (rolling)

A reverse-chronological journal, newest at top: what was done, what bug was fixed, what
surprised us, what to do next — narrative and detailed, including the gotchas, exact
commands, and dead ends. This is what gives the harness **long-running task
continuity**: the file you skim to answer "where did I leave off?".
An optional **"Open TODOs (small)"** section at the very top holds the standing
micro-backlog every session sees first. Entries here **age fast** — prune old ones, or
promote them into `memory-decisions.md` if they turn out durable.

Write here when: you complete substantive work, fix a bug, or discover a non-obvious
insight.

### `memory-attribution.md` — "who wrote this entry?" (the convention)

The smallest and most stable file: every memory entry's heading must carry an agent
identifier — `## YYYY-MM-DD: Description [Agent Name]`. Multiple agents (and humans)
may share one workspace — Claude Code next to e.g. a Copilot setup — and the tags are
what keep the shared memory auditable. It is not a log; it is the grammar the other two
files are written in.

### The dividing line, in one sentence

> If it changes how future work should be done and stays true for a long time, it's a
> **decision**. If it's the story of a particular stretch of work, it's a **session**.
> When a session entry keeps mattering, promote its lesson into decisions.

---

## 4. The conventions for writing entries

### Entry format (from `memory-attribution.md`)

```
## YYYY-MM-DD: Short description of the work or decision [Agent Name]
```

- **ISO date** so entries sort and scan cleanly.
- **A terse description** of the change.
- **An attribution tag** in square brackets — `[Claude Code]`, a human name, etc.

Below the heading, prose and tables are both welcome. The best entries lead with the
*insight* and then give the supporting detail, so a skim of the headings alone is
informative.

### The auto-update triggers table (from `CLAUDE.md`)

| Trigger | Action |
|---------|--------|
| A design/architecture decision is made | Update `memory-decisions.md` with date |
| Completing substantive work | Add to `memory-sessions.md` |
| A bug is fixed or a non-obvious insight discovered | Add to `memory-sessions.md` |
| A test pattern or convention is established | Update `memory-decisions.md` |

Plus the governing lines: **"Update memory files AS YOU GO, not at the end."** —
**"Skip: quick factual questions, trivial tasks with no new info."** —
**"DO NOT ASK. Just update the files when you learn something."**

### How the pieces reinforce each other

1. The SessionStart hook **orients**: repo state and the Open-TODOs pointer are
   injected before the first prompt (the initialization phase).
2. `CLAUDE.md` **tells** the model, at session start, to update memory as it goes and
   gives it the exact triggers and the file taxonomy.
3. `memory-attribution.md` **standardizes** the format so entries are consistent and
   auditable.
4. The Stop hook **enforces** the safety net at session end: if a lesson-signal is in
   the transcript and memory was never touched, the model is made to record it (once)
   before stopping.

Orientation and instruction at the front, format in the middle, safety-net at the
back — a closed loop. That redundancy is why the system actually keeps track of things
instead of relying on the model to remember to remember.

---

## 5. Repo-level rules-memory vs. Claude Code's built-in per-user memory

Two distinct memory systems are in play; the harness is only the first.

- **(A) Repo-level (this harness):** `CLAUDE.md` + `.claude/rules/*.md` inside the
  repository. Scope: the project — committable and team-shareable (every clone gets
  it), *or* deliberately kept local via `.git/info/exclude` (see `INSTALL.md` Step 4).
  Use for facts about *the codebase*: decisions, conventions, the running work log.
- **(B) Per-user built-in memory:** `~/.claude/projects/<slug>/memory/` (and the
  user-global `~/.claude/CLAUDE.md`). Scope: you, on your machine — never in the repo.
  Use for *personal* preferences and identity rules (commit email, privacy rules,
  style choices) that shouldn't live in a shared repo.

Rule of thumb: a fact the *whole team* should see → repo-level; a *personal* rule →
per-user. A committed privacy block naming what it protects would itself be the leak —
which is why identity rules default to per-user (see `DECISIONS.md`).

---

## 6. Design notes, with eyes open

- **Three layers, and this harness lives in two of them.** Instructions *advise*
  (CLAUDE.md, memory files — the intent layer); hooks and `permissions` *enforce
  in-process* (the harness layer); OS users, containers, and network policy *enforce
  out-of-process* (the environment layer). This harness is intent-heavy with three
  enforcement hooks; if a rule must HOLD, back it with `permissions.deny`/`ask` or a
  hook — see the enforcement note in the template's hard-rules block and INSTALL Step 7.
- **The Stop hook is a safety net, not the system.** The primary mechanism is the
  CLAUDE.md trigger table; sessions that maintain memory as-you-go never even see the
  hook fire.
- **The patterns are heuristic.** Phrase-based to dodge vocabulary collisions (a repo
  full of `fixed-width` identifiers must not match `fixed`), but they will still miss
  lessons phrased unusually and occasionally false-positive — bounded to one extra turn
  per session by design. Tune per repo (`settings.README.md`).
- **Track-vs-exclude is a deliberate choice.** Team-shared (commit it) and personal
  (`.git/info/exclude`) are both valid; pick per repo in `INSTALL.md` Step 4.
- **`.claude/skills/` folders are not part of the harness** — third-party downloads
  live there; the template does not include or manage them.
- **Task decomposition is deliberately out of scope.** Structured task primitives
  (feature lists, spec/plan contracts, plan→work→review→ship gating) belong to
  workflow frameworks and plugins (e.g. superpowers, claude-code-harness) — this
  harness only persists what such workflows learn. Declare workflow plugins the repo
  depends on as companions (see `template/.claude/settings.README.md`).

### Day-to-day tips

- Before committing memory files: `bash .claude/hooks/secret-scan.sh` — exit 0 =
  clean; findings are reported (file:line), never auto-edited.
- Personal notes on a team-shared harness: gitignored `CLAUDE.local.md` (auto-loaded
  next to the committed `CLAUDE.md`); personal settings: `.claude/settings.local.json`.
- Prefix a chat line with `#` to suggest an entry for Claude Code's built-in per-user
  memory (§5B) without breaking flow.
- `/fewer-permission-prompts` proposes an allowlist from your own usage history —
  pairs well with the user-global safety baseline (INSTALL Step 7).

---

## 7. TL;DR

The SessionStart hook orients the model with repo state and the open micro-backlog.
`CLAUDE.md` onboards it every session, mandates TDD (with premature-victory prevention
baked into the workflow), and hands it the memory rules. `.claude/rules/` is the dated,
attributed memory — durable *decisions*, a rolling *session* log with an Open-TODOs
micro-backlog, and the *attribution* convention binding them. The Stop hook reads the
transcript when the model stops and — once per session, only when needed — makes it
write down what it fixed or discovered. The PreCompact save-gate makes memory get
written before compaction can discard the details. A self-test machine-checks all
three hooks.
Together they make a stateless assistant behave like one with a persistent lab
notebook.

## 8. Further reading

Sources that shaped (or independently validated) this design — see `DECISIONS.md` for
what was adopted from each:

- Hidekazu Konishi, *Claude Code Hooks: Complete Guide* and *Harness and Environment
  Engineering Guide* — the hook-event/payload reference and the three-layer
  (intent / harness / environment) model; also an *Operator's Handbook* and client-side
  builder/linter tools for permissions and hooks (<https://hidekazu-konishi.com/>).
- *Learn Harness Engineering* (walkinglabs) — 13 lectures; source of the terms
  "repository as system of record", "premature-victory prevention", "feature lists as
  structured task primitives", "long-running task continuity"
  (<https://walkinglabs.github.io/learn-harness-engineering/en/>).
- *claude-code-harness* (Chachamaru127) — the process-enforcement pole: Plan. Work.
  Review. Ship. with machine-checked claims; source of "unknown stays unknown / not
  observed ≠ absent" and the doctor/self-test philosophy
  (<https://github.com/Chachamaru127/claude-code-harness>).
