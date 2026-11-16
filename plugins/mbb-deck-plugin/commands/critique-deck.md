---
description: Critique an existing presentation against MBB-style principles (Pyramid Principle, action titles, MECE, visual style)
argument-hint: <path-to-deck.pptx>
---

You are reviewing a presentation against MBB-style principles. The user has provided: $ARGUMENTS

## Your task

Read the deck (use the `pptx` skill if available to extract slide content), then produce a structured critique. Be direct — consultants critique decks frankly, not gently.

If Python with `python-pptx` is available, first run the deterministic lint and treat its output as measured fact: `python <skill>/scripts/lint_deck.py <deck.pptx>`.

First establish the **document type** (team alignment, recurring update, board, decision pre-read, external, documentation, keynote) and judge against that bar. If the user did not say, infer it and state that you inferred it.

Never supply facts: if a rewrite needs a number the deck does not contain, leave a named gap.

Run these ten named tests, in order:

1. **Titles-only read** — read only the action titles in sequence; report where the storyline breaks (horizontal logic).
2. **Title–content match** — check every number in a title against the slide body (vertical logic).
3. **Clothesline scan** — flag any slide with 5+ ungrouped parallel elements.
4. **Chart fit** — for each chart, name the comparison type of the *message* and check the chart type matches (components → stacked column/sorted bar — pie charts are banned outright in this skill; items → bar/waterfall; time → line/column; distribution → histogram; correlation → scatter/bubble).
5. **Density check** — the 90-second rule and the squint test per slide.
6. **Checklist run** — the violations against the production checklist (or note that `qa-reviewer` will run it).
7. **Content/process scan** — classify each title and lead statement as governing thought, content or process; flag every process statement that is not a next step.
8. **Insight check** — place the governing thought and each title on the four levels (data, summary, insight, so what); is the governing thought a recommendation or a summary of findings?
9. **Number check** — follow each figure through the deck: is it defined (what, baseline, period), stated against the reader's baseline, and identical in the executive summary, on the pages and in the appendix?
10. **Close check** — does a senior deck end on its decision needs (which, by when, why now) and next steps (task, owner, date), and does the executive summary ask for the same decisions?

## What to review

### 1. Storyline (most important)

- **Governing thought:** Can you state the deck's single recommendation in one sentence after reading it? If not, the deck has no thesis.
- **Action titles:** Read the titles top-to-bottom. Do they tell the story without the bodies? Are they complete declarative sentences or topic labels?
- **Pyramid:** Does the executive summary appear up front (slide 2 or 3)? Do supporting findings ladder up to the governing thought?
- **Structure fit:** Does the structure fit the audience and how controversial the message is? Does the opening stay within roughly 10–20% of the deck, with a real complication (why this matters now)?
- **MECE:** Are the breakdowns mutually exclusive and collectively exhaustive? Name the dimension each level uses. Look for overlapping categories, two dimensions mixed on one level, or hidden "other" buckets.
- **Count and order:** Three arguments is ideal, more than five too many. Can the order be named (temporal, importance, causal, structural)?
- **Work-order narrative:** Does the deck retell the project chronologically instead of leading with the answer?
- **So-what test:** For each slide, ask "so what?" Does the next slide answer it?

### 2. Slide-level

For each slide, flag:

- Topic titles ("Market Overview", "Customer Analysis") that should be action titles
- Action titles longer than two lines
- Numbers in titles that don't match the body
- Multiple ideas crammed into one slide
- Bullet lists that are not parallel in structure
- Missing source lines on data slides
- Generic recommendations ("we should consider growth")
- Missing framing line where it would aid clarity (sample size, methodology, scope)

### 3. Visual style

- 3D charts, gradient fills, drop shadows
- Stock photography or decorative imagery
- Inconsistent fonts, multiple accent colors, excessive color
- Crowded slides without whitespace
- Charts with too many series or unlabelled takeaways
- Missing page numbers or sources in footers
- Inconsistent footnote markers (mixing ¹ and ⁾ and ᵃ)
- Inconsistent number/currency formats (€100 vs. 100€ vs. 100 EUR)

## Output format

Produce the critique in this structure:

```
## Verdict

**Document type:** [given or inferred] — judged against: [the bar for that type]

- One clear governing thought, stated early, at insight or so-what level? [Yes/No and why]
- Structure fits the audience and the controversy of the message? [Yes/No and why]

## Storyline review

**Governing thought:** [State it in one sentence based on the deck. If you can't, say so. Name the level it reaches: data, summary, insight or so what.]

**Storyline read:** [List the action titles in order. Mark each ✓ if it's a real action title, ✗ if it's a topic label, ~ if it's borderline.]

**Thread:** [Does the storyline hold together? Where does it break?]

**Process statements:** [Each one that is not a next step, quoted, with the content rewrite.]

**Numbers:** [Figures that are undefined, against the wrong baseline, or differ between places — both places quoted.]

**Close:** [Decision needs (which, by when, why now) and next steps present? Do they match the executive summary?]

## Slide-by-slide issues

[For each problem slide, give: slide number, the issue, the fix.]

## Visual style issues

[List each, with the fix.]

## Top 3 changes that would most improve this deck

1. [Specific actionable change]
2. ...
3. ...
```

## Tone

- Be direct and specific. "Slide 6 is weak" is useless; "Slide 6's title 'Customer Analysis' is a topic label — rewrite as 'Two of our four customer segments generate 85% of profit'" is useful.
- Don't soften with hedges like "you might consider." Say "rewrite" or "remove" or "split into two slides."
- Quote specific text from the deck when calling out problems.
- Acknowledge what works. If the storyline is strong, say so before drilling into slide-level fixes.

## When to escalate

If the deck has more than ~20 issues, don't list them all. List the top 5–7 and note: "There are more — fix these first, re-run the critique, then we'll address the rest." Bulk lists are useless to act on.

If the user needs the email or one-page summary that travels with the deck, point them to `/exec-summary`.

For a structured per-slide QA pass on a finished deck (cover page, footers, formatting consistency, alignment), hand off to the `qa-reviewer` subagent instead. This command focuses on storyline and content; `qa-reviewer` covers production-quality QA.
