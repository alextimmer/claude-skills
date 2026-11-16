# Slide Patterns

Standard slide archetypes used in MBB-style decks. Pick the pattern that fits the action title.

## Every slide is a table (the generating principle)

Before picking a named pattern, think of the layout as **rows and columns**: rows = items (measures, options, phases), columns = dimensions (rationale, impact, timing, owner). This single principle produces clean, structured pages and prevents scattered elements. Three archetypes cover almost everything:

- **Qualitative slide** — a text table: items in rows, columns like measure / rationale / impact / timing. Also process steps and timelines.
- **Quantitative slide** — one chart as the main element, with a column for methodology and/or implications next to it.
- **Integrated slide** — a table combining text rows with a data column (e.g. options with a revenue-pool bar per row plus qualitative columns).

It is a rule of thumb, not a law — adjust when a framework (2x2, value chain) demands its own shape.

## Layout convention (applies to all slide types)

- **Action title** — top of slide, bold, ~24pt, left-aligned, one or two lines max
- **Body** — center of slide, the visual or content
- **Footer** — small text (~9pt, gray): page number bottom-right, source bottom-left
- **framing line position** - under the title, ~14pt, neutral gray, italic optional

## Pattern 1 — Bullet-supported insight slide

Action title at top. Body is 3–4 supporting bullets, parallel in structure, each bullet expanding one piece of the title's claim.

**When to use:** Findings that are best expressed as text rather than data.

**Bullet rules:**
- Each bullet starts with the same part of speech (all verbs, or all nouns)
- Each bullet is a complete thought, not a fragment
- Groups of at least 2 — a single bullet is not a list; write it as plain text
- 3–5 bullets maximum; one idea per bullet, two lines max
- No nested sub-bullets (at most one level if unavoidable)

**No clotheslines:** whenever 5 or more parallel elements appear, group them into labeled element groups (3 groups of 2 beat 1 list of 6), and consider a second dimension (e.g. examples per group) to turn the list into a table.

## Pattern 2 — Single-chart slide

Action title at top. Body is one chart (bar, line, waterfall, scatter). The chart's takeaway is *labeled directly on the chart* — never make the audience squint at a legend.

**Common charts in MBB decks:**
- **Bar chart** — comparing categories or time periods
- **Stacked bar / 100% stacked** — composition over time
- **Waterfall** — bridging from a starting value to an ending value, showing each driver
- **Line chart** — trends over time, usually with 2–4 series max
- **Scatter** — relationship between two variables, often with quadrant labels

**Chart anti-patterns:** 3D effects, gradient fills, more than 4 series on one chart, dual y-axes — and **pie charts, which are banned outright in this skill** (the skill author's hard rule; share-of-whole messages render as stacked columns or sorted bars). See the comparison-type → chart-type table in `references/visual-style.md`.

### Building a chart slide that narrates itself (McCandless Method)

Any data slide should support five questions in order. If the slide can't answer them by itself, the slide is incomplete.

1. **What is this chart?** A title or label so the viewer can name it. ("FY24 revenue by region.")
2. **What are the obvious questions?** Axes labeled, units stated, time period given, sample size or scope noted. The viewer should not have to ask "what are we looking at."
3. **What is the insight?** The action title states it. The chart is evidence; the title is the claim.
4. **Which data points prove it?** The chart visually highlights them — accent color on the bars/lines that matter, neutral gray on the rest. Don't make the audience hunt.
5. **What's the takeaway, and what comes next?** The slide ends in a position that the next slide's action title naturally picks up. (The "so what" test, applied to chart slides specifically.)

This is the McCandless Method, and it's both a build rule and a presentation rule. A slide built this way can be talked through live without notes; a slide built badly cannot be rescued by a good presenter.

## Pattern 3 — 2x2 matrix

Two axes, four quadrants. Used for positioning, prioritization, or segmentation.

- Label both axes with what increases in each direction
- Label each quadrant (e.g., "Stars", "Question Marks") or leave them blank if the items themselves tell the story
- Place items as dots, logos, or short labels in the quadrants
- The action title states the conclusion the matrix supports ("Three of our five products fall in the low-growth, low-margin quadrant")

## Pattern 4 — Value chain / horizontal flow

Steps left-to-right with arrows or chevrons. Each step has a short label and a one-line description below.

**When to use:** Showing a process, customer journey, or sequential framework.

## Pattern 5 — MECE bucket list

3–5 vertical or horizontal boxes representing the breakdown. Each box has:
- A category name (the bucket)
- A short description
- A key metric or finding

**When to use:** Introducing the framework that organizes the rest of the deck. Often the slide right after the executive summary.

## Pattern 6 — Comparison table

Options as columns, criteria as rows. Cells contain ratings (High/Medium/Low, Harvey balls, or check/cross).

**When to use:** Evaluating 2–4 options against the same criteria, leading to a recommendation.

**Rules:**
- The recommended option is highlighted (bold border, accent color, or a "Recommended" badge)
- Criteria are listed in order of importance
- Don't include a criterion if all options score the same on it

## Pattern 7 — Quote slide

A single direct quote in large text in the center, attribution below in smaller text.

**When to use:** Bringing in the voice of the customer, employee, or stakeholder. Use sparingly — at most one or two per deck.

## Pattern 8 — Roadmap / Gantt

Phases as columns or rows with milestones, owners, and dates.

**When to use:** Implementation slide — place it near the end of the deck.

**Rules:**
- Show 2–4 phases (Now / Next / Later, or quarters)
- Each phase has 2–4 milestones max
- Mark dependencies if relevant
- Owner names or function on each milestone

## Structuring techniques for documents (navigation)

For decks longer than ~10 slides, help the audience keep the map in their head:

- **Structure pages:** introduce a framework before a section, so upcoming pages have a home.
- **Tracking elements:** repeat the framework marker on each following page so the audience connects the dots.
- **Chapter trackers:** small section labels in the top corner of each slide.
- **Double-click logic:** a detail page is structured as a virtual double-click into an element of the prior page.
- **Leading references:** start action titles with the words introduced on the structure page, so slides visibly attach to the framework.

## Useful slide elements

- **Callouts and bubbles** for remarks on specific chart elements
- **Takeaway boxes** for the slide's overall conclusion
- **Concern boxes** (`callout` on any content slide) — one or two lines in an outlined box above the footer, answering a stakeholder's main concern on the page where it arises, or stating a caveat: "Why this differs from the March figure: the March estimate excluded billing." Outline only, no fill. At most one per slide, and only where a reader would otherwise stop and ask
- **Page names** (`name` on any slide) — "the savings page". Metadata for references from the executive summary, the email or the conversation; never printed on the slide, so they add no clutter
- **Icons** for scannability (monochrome, one style, accent or gray only)
- **Status stickers** — PRELIMINARY, INDICATIVE, FOR DISCUSSION, ILLUSTRATIVE — whenever numbers are not final. Use them honestly: they manage expectations and protect credibility.

## Pattern 9 — Executive summary slide

This slide is special. It is the entire deck on one page. Every reader reads it and many read little else, so it has to carry the whole message.

Structure:
- Action title at top: the governing thought
- **Context** (`context`): situation and complication in at most two sentences
- **Arguments** (`supporting_points`): 3–5 points, one per major section of the deck, in the deck's order. Each opens with a **bold lead** that mirrors the section's action title, followed by the key numbers
- **Decision needs** (`decisions`, `why_now`): for decision documents, the decisions in their own box — numbered, one line each — with the deadline that forces them
- No chart, no decoration

Rules:
- **Mirror the document.** The summary follows the deck's structure, so the reader can navigate from it. If in doubt, it is the condensed sequence of the action titles.
- **Quantify.** "$14M a year against budget" convinces; "significant upside" does not.
- **Answer first, content not process.** Not "we ran a tender and a customer test", but what they showed.
- **Same numbers, same words** as the pages that follow. The validator flags a summary figure that appears on no other page.

**This is the most important slide in the deck.** If the audience reads only one slide, this is the one.

## Pattern 10 — Decisions and next steps slide (`type: decisions`)

The closing page of a senior document: what is asked of the reader. A table, like every slide — rows are decisions, columns are decision, safeguard, owner, by when — followed by "why now" and the next steps.

**When to use:** the last page before the appendix in any `board`, `decision_pre_read` or `external` document. The validator warns when it is missing.

**Rules:**
- Each decision is a sentence that can be approved or rejected ("Approve the SMB tier sunset over 18 months"), not a topic to discuss
- At most five decisions; three is typical — decide what this meeting can realistically settle
- Pair each decision with its **safeguard**: the answer to the main concern behind it
- State **why now**: the deadline or event that forces the decisions
- Next steps carry task, owner and date
- The wording matches the decisions box on the executive summary exactly
