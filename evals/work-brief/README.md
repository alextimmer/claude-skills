# work-brief evals

Test prompts for measuring whether the `work-brief` skill (from `mbb-deck-plugin`) triggers correctly.

## Why this matters

The word "brief" is ambiguous, and the skill has to pick out one sense: an instruction for someone who will do the work. Three other senses must stay quiet:

- "Brief me" - a request for information.
- A briefing note for an executive - that is an executive summary and belongs to `executive-storyline`.
- A legal brief.

The false-negative trap is delegation described without the word: "hand this over to a colleague", "my delegated decks come back wrong".

## What's in here

- `test_prompts.json` - 8 prompts that should trigger the skill and 8 that shouldn't, with rationale for each.

## How to run

Same options as [`evals/mbb-deck/README.md`](../mbb-deck/README.md): manual sanity check, the [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) eval harness, or your own script over the JSON.

## Targets

- **Trigger rate** (should_trigger prompts that activate the skill): **≥ 85%**
- **No-trigger rate** (should_not_trigger prompts that correctly stay quiet): **≥ 90%**
