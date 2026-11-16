---
description: Condense a finished deck or document into an executive summary for an email, a one-pager or a spoken update
argument-hint: <path-to-deck-or-document, or paste the content> [email|one-pager|spoken]
---

You are condensing an existing deck or document into an executive summary. The user has provided: $ARGUMENTS

Use the `executive-storyline` skill (Condense mode). Its `references/executive-summary.md` has the anatomy and the form for each channel, and `examples/summary-from-deck.md` a worked example.

## Process

### 1. Read the whole source

- A storyline JSON: read it directly.
- A `.pptx`: use the `pptx` skill or another extraction capability if available. If none is, ask the user to paste the slide titles and the executive summary page.
- Pasted text or a document: use it as given.

List the action titles (or section headings) in order.

### 2. Titles-only read

Read only the titles in sequence. If they do not tell a story — topic labels, a chronological project narrative, no recommendation — say so before summarizing. A summary cannot repair a missing storyline; offer `/critique-deck` or the `storyline-reviewer` subagent, and ask whether to proceed anyway.

### 3. Confirm the three inputs that are the user's

Ask only for what the source and the request do not already answer:

- **Audience and channel:** who receives it, and as what — email, one-page summary, spoken update?
- **Objective:** what should the reader do afterwards, and by when?
- **Governing thought:** state it in one sentence as the source has it and get it confirmed. If you would word it differently, say so and ask; do not improve it silently.

### 4. Draft

Follow the anatomy:

1. **Context** — situation and complication in two sentences.
2. **Recommendation** — the governing thought in one sentence, in bold.
3. **Arguments** — one bullet per argument of the source, in the source's order, each opening with a bold lead that mirrors the section's action title, followed by the key numbers. Group pages into arguments; do not write one bullet per slide. Five bullets at most.
4. **Decision needs** — the decisions as the source states them, numbered, with the deadline and why now. If the source asks for none, say so instead of inventing an ask.
5. **Pointer** — one line to the attachment, naming the page that answers the reader's main concern. Use the page's recorded `name` ("the savings page") where the storyline has one; never a page number.

For an email, the subject line carries the ask and the date. For a spoken update: the governing thought, "for three reasons", then the next step or the decision needed.

### 5. Check every number

Trace each figure in the summary to the source: same value, same unit, same baseline, same period. Report the check as a short table. Where the source itself gives two figures for the same thing, or merges different measures under one number, stop and raise it with the user rather than choosing one.

Never add a figure the source does not contain. List any figure you wanted and could not find.

### 6. Lint and hand over

If Python is available, run the prose lint on the draft and fix what it flags:

```bash
python <executive-storyline skill>/scripts/lint_prose.py draft.md --type email
```

Then present the summary, the number check, and anything you raised in steps 2 and 5.

## Rules

- Content, not process: what the work showed, not what the team did.
- Nothing in the summary without a page behind it.
- Plain business English; no stock words, no exclamation marks.
