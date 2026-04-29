# mbb-deck evals

Test prompts for measuring whether the `mbb-deck` skill triggers correctly.

## Why this matters

Skills are model-invoked: Claude reads the SKILL.md `description` field and decides whether the skill applies based on the user's prompt. If the description is too narrow, the skill won't fire when it should. If it's too broad, it'll fire on irrelevant requests and slow Claude down.

These evals let you measure trigger accuracy and refine the description with data instead of guessing.

## What's in here

- `test_prompts.json` — 15 prompts that should trigger the skill and 12 that shouldn't, with rationale for each.

## How to run

There's no built-in eval runner shipped with this skill, but here are three ways to use these prompts:

### Option 1 — Manual sanity check

Pick 5 prompts from each list. In Claude Code or Claude.ai with the skill installed, paste each prompt and observe whether the skill activates (Claude will mention pulling in the `mbb-deck` skill, or reference its concepts).

### Option 2 — `skill-creator` eval harness

Anthropic's [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill includes an eval workflow. Point it at this `test_prompts.json` and it will run the prompts in parallel and grade trigger accuracy.

### Option 3 — Roll your own

The JSON is structured for easy scripting:

```python
import json
import anthropic

client = anthropic.Anthropic()
prompts = json.loads(open("test_prompts.json").read())

for p in prompts["should_trigger"]:
    # Send p["prompt"] to a Claude API call with the skill registered,
    # check whether the response references the skill or its concepts.
    pass
```

## Targets

- **Trigger rate** (should_trigger prompts that activate the skill): **≥ 85%**
- **No-trigger rate** (should_not_trigger prompts that correctly stay quiet): **≥ 90%**

## When trigger rate is low

The skill is under-triggering. Edit `plugins/mbb-deck-plugin/skills/mbb-deck/SKILL.md`'s `description` field to be more specific about linguistic cues:

- Board / executive / leadership audiences
- Words like "recommendation", "strategy", "consulting"
- Mentions of "MBB", "McKinsey", "Bain", "BCG", "pyramid principle", "MECE"
- Requests for an "executive summary up front"

## When false-positive rate is high

The skill is over-triggering. Add explicit counter-examples to the description:

- "Do not trigger for casual or creative presentations"
- "Do not trigger for lecture slides, training decks, photo slideshows"
- "Do not trigger for definitional questions about consulting frameworks"

## Note on scope

This folder lives at the **repo root** intentionally — it's maintainer tooling, not part of the user-facing plugin. Users who install `mbb-deck-plugin` via `/plugin install` won't get these evals, which is correct: they're for you to refine the skill, not for them to run.
