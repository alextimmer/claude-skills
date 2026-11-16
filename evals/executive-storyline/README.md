# executive-storyline evals

Test prompts for measuring whether the `executive-storyline` skill (from `mbb-deck-plugin`) triggers correctly.

## Why this matters

Skills are model-invoked: Claude reads the SKILL.md `description` field and decides whether the skill applies. This skill has two traps:

- **False positives on "summarize".** A neutral summary of a transcript or a paper has no executive reader and no recommendation, and should not pull in the storyline method.
- **The boundary with `mbb-deck`.** A request for slides belongs to the deck skill. A request for the storyline alone, or for a memo, an email or a spoken update, belongs here.

And one false-negative trap: users who describe the problem ("how do I present this", "what do I answer when asked for the status") without naming a storyline or a summary.

## What's in here

- `test_prompts.json` — 12 prompts that should trigger the skill and 10 that shouldn't, with rationale for each.

## How to run

Same options as [`evals/mbb-deck/README.md`](../mbb-deck/README.md): manual sanity check, the [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) eval harness, or your own script over the JSON.

## Targets

- **Trigger rate** (should_trigger prompts that activate the skill): **≥ 85%**
- **No-trigger rate** (should_not_trigger prompts that correctly stay quiet): **≥ 90%**

## Deterministic check

The skill ships `scripts/lint_prose.py`. A quick regression run from the repo root:

```bash
python plugins/mbb-deck-plugin/skills/executive-storyline/scripts/lint_prose.py \
  plugins/mbb-deck-plugin/skills/executive-storyline/examples/summary-from-deck.md --type other
```

Expect one `sprawl` warning: the example lists the deck's eleven titles before condensing them. The email inside it passes clean when checked on its own with `--type email`.
