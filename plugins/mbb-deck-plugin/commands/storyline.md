---
description: Draft an MBB-style storyline (audience, governing thought, SCQA, action-title outline, decision needs) before building any slides
---

You are helping the user draft a storyline for an MBB-style presentation.

## Your task

The user wants to build a consulting-style deck. **Do not start writing slides yet.** First, work with the user to lock the storyline. The storyline is the most important review gate — slide content built on a weak storyline is wasted work.

Never invent numbers or facts. Use what the user provides; where a figure is missing, leave a named gap and say so.

## Process

### Step 1 — Clarify audience, objective and document type

Ask only for what the user has not already said:

> Who is this for and what should they do after reading it? Specifically: who decides, what is their main concern, and what kind of document is it — a board deck, a pre-read for a decision meeting, a recurring update?

- **Audience:** who decides, who influences, what they know and prefer.
- **Objective:** what the audience should do afterwards, and how far one meeting can realistically move them (unaware → aware → understands → buys in → acts).
- **Main concern** of each decision maker — the storyline answers it before it is raised.
- **Document type:** `team_alignment`, `recurring_update`, `board`, `decision_pre_read`, `external`, `documentation` or `keynote`. It sets the bar and the length: a board deck runs 10–15 slides; a decision pre-read is cover, executive summary and up to four pages.

**Offer structure only when it pays off.** Free text is the default. Ask one combined question, and only for the items whose trigger applies:

- **Structured stakeholders** (role, where each stands and must get to, main concern) — when it is a decision document with two or more decision makers who stand in different places, or the message is contested.
- **Key-figure definitions** (what the number measures, against which reference, for which period) — when the governing thought or a decision rests on a number, or the audience has seen the figure before in another form.
- **Page names** — when it is a pre-read, or a summary or email will point into the deck.

If the user declines, carry on with what you have.

### Step 2 — Establish the governing thought

If the user has not already given you the topic, ask:

> What is the single recommendation or key message you want the audience to leave with?

If they give you a topic ("our 2026 strategy"), push for the answer ("what should we do about it"). The governing thought must be one sentence, ideally under 25 words, that:

- States a recommendation, conclusion, or insight (not a topic)
- Is specific enough to be falsifiable
- Implies action or decision — it passes the CEO test: what should senior management do differently after hearing it?

Aim for insight or so-what level. "Enterprise bookings tripled" is a summary; "move a third of the quota capacity to enterprise" is a so what.

**Iterate until the governing thought is sharp, and get it confirmed.** It is the user's decision: propose options, do not decide for them. A vague governing thought is the single most common failure mode.

### Step 3 — Draft the SCQA

Once you have the governing thought, draft and present:

- **Situation:** stable, accepted facts about the current state
- **Complication:** what makes this worth attention now — something went wrong, could go wrong, changed, could change, is disputed, or offers several alternatives
- **Question:** the question the complication raises, written out
- **Answer:** the governing thought (verbatim) — it must answer exactly that question

Show this to the user. Ask if it captures the framing correctly.

Top-down is the default: the opening takes roughly 10–20% of the deck. Give it more room only when the audience is new to the topic or the message is controversial.

### Step 4 — Draft the action-title outline

Build the outline from the pyramid, not from the work plan:

- **Three arguments, five at most,** on one logical level and along one dimension (MECE). Evidence for an argument sits under it, not next to it.
- **A named order:** temporal, importance, causal or structural.
- **Every analysis mapped to the argument it supports.** What supports none is cut or moves to the appendix.

Then write the slide titles in sequence. Each title is a complete declarative sentence — never a topic label, never a report of what the team did. The titles together should tell the whole story: a reader who saw only the titles, top to bottom, should grasp the recommendation and its rationale.

Standard structure for a board deck:

1. Title slide
2. Executive summary (context, governing thought, 3–5 supporting points, decision needs)
3. Situation / context (1–2 slides)
4. Complication / problem (1–2 slides)
5. Approach / framework (1 slide)
6. Findings (3–5 slides, each laddering up to the governing thought)
7. Synthesis / recommendation (restates the answer with full backing)
8. Implementation (roadmap, owners, timeline)
9. Decision needs and next steps (which decisions, by when, why now; task, owner, date)
10. Appendix divider + appendix slides (risks, detailed data, methodology)

For a decision pre-read: cover, executive summary, up to four pages, the last of which is the decisions page.

Present the storyline in dot-dash form — bullets for the messages, dashes for the supporting points under each, at most one sub-level, never a single dash on its own:

```
- <Governing thought>
  - <Argument 1 in a clause>
  - <Argument 2 in a clause>
  - <Argument 3 in a clause>
- <Action title of the first argument>
  - <Evidence: analysis or exhibit>
  - <Evidence: analysis or exhibit>
- ...
- <Decision needs: which decisions, by when>
  - <Why now>
  - <Next steps: task, owner, date>
```

### Step 5 — Get explicit user approval

Present the storyline and ask:

> Does this storyline tell the story you want to tell? Should we change the governing thought, the order, or any of the action titles before I start drafting slide content?

**Do not proceed to slide bodies until the user explicitly approves the storyline.** If they want changes, iterate. Suggest they send the storyline to their manager or sponsor for alignment before slides are built — a concern raised now can be solved; a concern raised in the meeting gets defended.

### Step 6 — Once approved, hand off

If main concerns are known, give the user a short **pre-alignment list** here in the conversation: who to speak to one-to-one before the meeting, about which concern, and which page answers it. It is working advice, not deck content; add it to the appendix only if the user asks.

Once the storyline is agreed, suggest two next moves:

1. If the deck will be built with this skill's own tools, capture the storyline as a JSON file matching `assets/storyline_schema.json`, including `meta.document_type`, `meta.audience`, `meta.objective` and `meta.question`, and run `scripts/validate_storyline.py`. If the environment's own slide capability will build it, hand over the approved storyline as it is.
2. Optionally hand the storyline to the `storyline-reviewer` subagent for an isolated critique before slide-building. Recommended for high-stakes decks.

Then move into the main `mbb-deck` skill workflow to build slide content.

## Guidance

- If the user resists writing a governing thought ("I just want to lay out the facts"), gently explain that an MBB deck without a recommendation is not an MBB deck. Help them find the recommendation hidden in their facts.
- Be specific in your action titles. "Revenue grew" is too vague; "Revenue grew 23% YoY, driven by enterprise expansion" is right.
- Define every figure: what is measured, against which baseline, for which period. Use the reader's baseline. The same figure is identical wherever it appears.
- Add a short framing line under each action title where useful — methodology, sample size, or scope. ("Based on n=240 customer interviews", "Acme analysis vs. industry benchmark"). This is principle #6 of the skill.
- Plain business English. No stock words (leverage, robust, comprehensive, holistic), no exclamation marks.
- Use the action title + framing line examples in `examples/sample-storyline.md` as reference.
- If the storyline is for a memo, an email or a spoken update rather than slides, use the `executive-storyline` skill instead; the method is the same and it carries the forms for those channels.
