# memory-harness evals

Test prompts for measuring whether the `memory-harness` skill (from `claude-memory-harness`) triggers correctly.

## Why this matters

Skills are model-invoked: Claude reads the SKILL.md `description` field and decides whether the skill applies. The harness skill has two classic false-positive traps — "memory" (RAM vs. project memory) and "harness" (test harness vs. this harness) — and a false-negative trap: users describing the *problem* ("make sessions remember things") without naming the harness.

## What's in here

- `test_prompts.json` — 10 prompts that should trigger the skill and 8 that shouldn't, with rationale for each.

## How to run

Same options as [`evals/mbb-deck/README.md`](../mbb-deck/README.md): manual sanity check, the [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) eval harness, or your own script over the JSON.

## Targets

- **Trigger rate** (should_trigger prompts that activate the skill): **≥ 85%**
- **No-trigger rate** (should_not_trigger prompts that correctly stay quiet): **≥ 90%**

If rates drift, edit the `description` field in `plugins/claude-memory-harness/skills/memory-harness/SKILL.md` — add the missed phrasing to the description (under-triggering) or add explicit counter-examples like "not for test harnesses or memory profiling" (over-triggering).

## Note on scope

This folder lives at the **repo root** intentionally — it's maintainer tooling, not part of the user-facing plugin. Users who install `claude-memory-harness` via `/plugin install` won't get these evals, which is correct.
