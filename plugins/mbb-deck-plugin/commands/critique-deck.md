---
description: Critique an existing presentation against MBB-style principles (Pyramid Principle, action titles, MECE, visual style)
argument-hint: <path-to-deck.pptx>
---

You are reviewing a presentation against MBB-style principles. The user has provided: $ARGUMENTS

## Your task

Read the deck (use the `pptx` skill if available to extract slide content), then produce a structured critique. Be direct — consultants critique decks frankly, not gently.

If Python with `python-pptx` is available, first run the deterministic lint and treat its output as measured fact: `python <skill>/scripts/lint_deck.py <deck.pptx>`.

Run these six named tests, in order:

1. **Titles-only read** — read only the action titles in sequence; report where the storyline breaks (horizontal logic).
2. **Title–content match** — check every number in a title against the slide body (vertical logic).
3. **Clothesline scan** — flag any slide with 5+ ungrouped parallel elements.
4. **Chart fit** — for each chart, name the comparison type of the *message* and check the chart type matches (components → stacked column/sorted bar — pie charts are banned outright in this skill; items → bar/waterfall; time → line/column; distribution → histogram; correlation → scatter/bubble).
5. **Density check** — the 90-second rule and the squint test per slide.
6. **Checklist run** — the violations against the production checklist (or note that `qa-reviewer` will run it).

## What to review

### 1. Storyline (most important)

- **Governing thought:** Can you state the deck's single recommendation in one sentence after reading it? If not, the deck has no thesis.
- **Action titles:** Read the titles top-to-bottom. Do they tell the story without the bodies? Are they complete declarative sentences or topic labels?
- **Pyramid:** Does the executive summary appear up front (slide 2 or 3)? Do supporting findings ladder up to the governing thought?
- **MECE:** Are the breakdowns mutually exclusive and collectively exhaustive? Look for overlapping categories or hidden "other" buckets.
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
## Storyline review

**Governing thought:** [State it in one sentence based on the deck. If you can't, say so.]

**Storyline read:** [List the action titles in order. Mark each ✓ if it's a real action title, ✗ if it's a topic label, ~ if it's borderline.]

**Verdict:** [Does the storyline hold together? Where does it break?]

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

For a structured per-slide QA pass on a finished deck (cover page, footers, formatting consistency, alignment), hand off to the `qa-reviewer` subagent instead. This command focuses on storyline and content; `qa-reviewer` covers production-quality QA.
