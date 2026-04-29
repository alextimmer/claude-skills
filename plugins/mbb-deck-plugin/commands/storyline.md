---
description: Draft an MBB-style storyline (governing thought, SCQA, action-title outline) before building any slides
---

You are helping the user draft a storyline for an MBB-style presentation.

## Your task

The user wants to build a consulting-style deck. **Do not start writing slides yet.** First, work with the user to lock the storyline. The storyline is the most important review gate — slide content built on a weak storyline is wasted work.

## Process

### Step 1 — Establish the governing thought

If the user has not already given you the topic, ask:

> What is this deck for? Specifically: what is the single recommendation or key message you want the audience to leave with?

If they give you a topic ("our 2026 strategy"), push for the answer ("what should we do about it"). The governing thought must be one sentence, ideally under 25 words, that:

- States a recommendation, conclusion, or insight (not a topic)
- Is specific enough to be falsifiable
- Implies action or decision

**Iterate until the governing thought is sharp.** A vague governing thought is the single most common failure mode.

### Step 2 — Draft the SCQA

Once you have the governing thought, draft and present:

- **Situation:** stable, accepted facts about the current state
- **Complication:** what changed, what's at stake
- **Question:** the implicit question that follows
- **Answer:** the governing thought (verbatim)

Show this to the user. Ask if it captures the framing correctly.

### Step 3 — Draft the action-title outline

Write 8–15 slide titles in sequence. Each title is a complete declarative sentence — never a topic label. The titles together should tell the whole story: a reader who saw only the titles, top to bottom, should grasp the recommendation and its rationale.

Standard structure:

1. Title slide
2. Executive summary (governing thought + 3–5 supporting points)
3. Situation / context (1–2 slides)
4. Complication / problem (1–2 slides)
5. Approach / framework (1 slide)
6. Findings (3–5 slides, each laddering up to the governing thought)
7. Synthesis / recommendation (restates the answer with full backing)
8. Implementation (roadmap, owners, timeline)
9. Risks
10. Appendix divider + appendix slides

### Step 4 — Get explicit user approval

Present the storyline and ask:

> Does this storyline tell the story you want to tell? Should we change the governing thought, the order, or any of the action titles before I start drafting slide content?

**Do not proceed to slide bodies until the user explicitly approves the storyline.** If they want changes, iterate.

### Step 5 — Once approved, hand off

Once the storyline is agreed, suggest two next moves:

1. Capture the storyline as a JSON file matching `assets/storyline_schema.json`. Run `scripts/validate_storyline.py` and address any issues.
2. Optionally hand the storyline to the `storyline-reviewer` subagent for an isolated critique before slide-building. Recommended for high-stakes decks.

Then move into the main `mbb-deck` skill workflow to build slide content.

## Guidance

- If the user resists writing a governing thought ("I just want to lay out the facts"), gently explain that an MBB deck without a recommendation is not an MBB deck. Help them find the recommendation hidden in their facts.
- Be specific in your action titles. "Revenue grew" is too vague; "Revenue grew 23% YoY, driven by enterprise expansion" is right.
- Add a short framing line under each action title where useful — methodology, sample size, or scope. ("Based on n=240 customer interviews", "Acme analysis vs. industry benchmark"). This is principle #6 of the skill.
- Use the action title + framing line examples in `examples/sample-storyline.md` as reference.
