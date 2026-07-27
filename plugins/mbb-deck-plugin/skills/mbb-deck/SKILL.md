---
name: mbb-deck
description: Use this skill whenever the user wants to create, improve, or review a presentation, deck, slides, or a one-pager in MBB / management consulting style (McKinsey, Bain, BCG style). Trigger on requests for "consulting deck", "strategy presentation", "executive briefing", "board deck", "MBB style", "pyramid principle", "management consulting deck", "slide writing", "action title", "review my deck/slides", "give feedback on this deck", or whenever the user asks for slides that need a clear recommendation, action titles, MECE structure, or executive-level polish. Covers both creating decks and reviewing existing ones. Do not trigger for casual or creative presentations (kids' birthday slideshow, photo deck, casual class lecture).
---

# MBB-Style Presentation Skill

Build presentations in the structural style of top-tier management consulting firms. The hallmarks: an answer-first storyline, action titles, MECE structure, and one idea per slide.

The skill has two modes: **create** (develop storyline and slides — the workflow below) and **feedback** (review a draft deck against the standard — use `/critique-deck` for content and storyline, the `qa-reviewer` subagent for production polish; both run the deterministic lint first).

## Ten core principles

1. **Answer first (Minto Pyramid).** State the recommendation up front, then the supporting arguments, then the evidence. The reader should know your conclusion from the executive summary slide.
2. **Action titles, not topic titles.** Every slide title is a complete declarative sentence stating the takeaway. "Revenue grew 23% YoY, driven by enterprise" — not "Revenue Trends". The title alone should convey the insight.
3. **One idea per slide.** If you can't summarize the slide in a single sentence, split it into two slides. If content does not support that one message: **if in doubt, leave it out.**
4. **MECE structure.** Categories must be Mutually Exclusive and Collectively Exhaustive. No overlap, no gaps.
5. **Source everything.** Cite sources in a small footnote (typically ~9pt, gray) at the bottom-left of any data slide.
6. **Action title + framing line**. Beneath the action title, add a short subtitle (~10–15 words) that states the logic, methodology, or sample size. Title says what's true; framing line says how we know. Examples: "Based on n=240 customer interviews", "Acme analysis vs. industry benchmark", "Excludes one-time charges".
7. **Build data slides so they narrate themselves (McCandless).** Any chart or data slide must support a five-step read: (1) the chart can be named, (2) obvious questions are answered on the slide itself (axes, units, period, n), (3) the action title states the insight, (4) the specific data points proving the insight are visually highlighted (accent color on the relevant bar; gray on the rest), (5) the takeaway sets up the next slide. If a slide can't be talked through this way, the slide isn't done.
8. **Every slide is a table.** Think of any layout as rows and columns (rows = items, columns = dimensions such as measure, rationale, impact, timing). This single principle produces clean, structured pages and prevents scattered elements. It is a rule of thumb — adjust when a chart or framework demands it.
9. **Horizontal and vertical logic.** Read all action titles in sequence: they must tell the storyline of the document by themselves (horizontal logic). On each slide, the content must fully support its title (vertical logic). Both are tested explicitly during review.
10. **Synthesize, do not summarize.** Slides state implications (the "So What"), not just organized facts. "We win 40% of negotiations" is a fact; "Negotiation conversion declined from 55% to 40%, likely driven by recent scaling of the sales team" is an insight.

## Agents and tools available in this plugin

This plugin ships several subagents that handle specific phases of the work. Suggest them at the right moments in the workflow below — they run in their own context and return structured output without polluting the main conversation.

**Pre-build analytical agents** (use when the deck depends on data analysis):

- `data-diagnostic` — turns raw business data into a one-page diagnostic memo with a governing diagnosis, risks, and 2–3 actions. Use when the deck needs to answer "what's actually happening?"
- `forecast-modeler` — turns historical metrics into a 12-month scenario forecast with decision triggers. Use when the deck depends on a forward-looking projection.
- `cohort-analyzer` — turns customer data into retention curves, an activation insight, and 5 ranked changes spanning the customer lifecycle. Use when the deck is about customer behavior, retention, or LTV.
- `market-basket-analyzer` — turns transaction data into association rules, 5 storefront changes, and a parameterized revenue model. Use when the deck is about cross-sell, bundling, or merchandising.

When any of these agents has run, adopt its output as the analytical foundation of the deck — its governing finding becomes the deck's governing thought.

**Build-phase reviewers**:

- `storyline-reviewer` — critiques a storyline draft (governing thought + action titles) before slide content is built. Use between Step 3 and Step 4 of the workflow for high-stakes decks.
- `qa-reviewer` — runs production QA (footers, formatting, alignment, footnote consistency, number formats) on a finished `.pptx`. Use after Step 6, before sharing the deck.

**Live-presentation coach**:

- `chart-presenter` — takes a single chart slide and returns a McCandless-method talking script (introduce → answer questions → state insight → call out data → close). Use when the user is rehearsing a live talk on a data slide.

**Slash commands**:

- `/storyline` — drops directly into storyline-drafting mode (governing thought + SCQA + action titles, with explicit user approval gate). Equivalent to running Steps 1–3 of the workflow as a focused interaction.
- `/critique-deck <path>` — runs a content-level critique on an existing `.pptx`. Different from `qa-reviewer`: this command focuses on storyline and content; `qa-reviewer` focuses on production polish.

## Data sources for the analytical agents

The analytical agents (`data-diagnostic`, `forecast-modeler`, `cohort-analyzer`, `market-basket-analyzer`) need data as input. Claude has multiple ways to get data into context — file uploads, code execution, filesystem reads, MCP database connectors — depending on the host environment. You don't need to know which mechanism is available; just ask the user how they want to share their data:

- Paste the metrics or a summary directly into the conversation
- Upload a CSV, Excel, or JSON file
- Point at a file path (Claude Code with filesystem access)
- Pull from a connected service (Google Drive, Notion, or a database via MCP)

If the user gestures at data without providing it ("build a deck from our Q3 numbers") and nothing is in context yet, ask once which method they want to use. Do not invent or estimate values to fill gaps — the analytical agents have explicit guards against that and will refuse to produce confident output on missing data.

## Workflow when the user requests a deck

Follow these steps in order. Do not skip to slide-building before the storyline is approved.

### Step 1 — Establish the governing thought

Ask the user (if not already clear): **"What is the single recommendation or key message this deck should leave the audience with?"**

The governing thought is one sentence. Every slide ladders up to it. If the user can't articulate it in one sentence, work with them to sharpen it before moving on.

### Step 2 — Draft the storyline using SCQA

Before any slides, write out the Situation–Complication–Question–Answer structure:

- **Situation** — current state, accepted facts, no controversy
- **Complication** — what changed, what's broken, what's at stake
- **Question** — the implicit question the audience is now asking
- **Answer** — the governing thought (the recommendation)

### Step 3 — Outline every slide as just an action title

List 10–15 action titles in sequence. Each title is a complete sentence. Reading the titles top-to-bottom should tell the whole story without seeing any slide bodies. **Get explicit user approval on this storyline before building slide content.** This is the most important review gate.

### Step 3.5 — (Recommended for high-stakes decks) Get an isolated review

Hand the storyline to the `storyline-reviewer` subagent. It returns a structured critique covering the governing thought, action titles, pyramid integrity, and MECE — without polluting this conversation with critique back-and-forth. Iterate on the storyline until the reviewer is satisfied, then proceed to Step 4.

For decks that depend on data analysis, this is also where the analytical agents (`data-diagnostic`, `forecast-modeler`, `cohort-analyzer`, `market-basket-analyzer`) feed in. If the storyline is forecast-driven and `forecast-modeler` has not run yet, run it now — its scenario range and decision triggers must be in hand by Step 4, where they become the substance of the recommendation slides.

### Step 4 — Build slide content as a structured JSON

Build every slide in this order — never start with the visual or the text:

1. **Message.** The one message of the slide, written down as the action title. If the message is not clear, the slide is not ready to be built.
2. **Layout.** Choose the layout — in table format where applicable (rows = items, columns = dimensions). See the three layout archetypes in `references/slide-patterns.md`.
3. **Main visual.** The centerpiece, typically the chart. Choose the chart type from the *message's comparison type*, not from the data shape (`references/visual-style.md`).
4. **Supporting text.** Bullets, labels, callouts, takeaway box — parallel grammar, groups of at least 2, max 5 per box.
5. **Polish.** Alignment, consistency, no jitter.

Capture the result as a structured JSON file matching `assets/storyline_schema.json`. A worked example lives in `examples/sample-storyline.json`. Before finalizing any slide, run the **10-second executive test**: can a senior executive get the point in 10 seconds? Does the title tell them what to think? Could any element be removed without losing the message? Would you be comfortable if only the titles were read aloud?

### Step 5 — Validate the storyline

Run the validator before generating the file:

```bash
python scripts/validate_storyline.py path/to/storyline.json
```

Address any ERROR-level issues. WARNING-level issues (e.g., topic titles, missing exec summary up front, too few content slides) should also be fixed unless there's a deliberate reason.

### Step 6 — Choose the output format and render

The storyline JSON is format-agnostic. The same storyline can be rendered four different ways. Pick based on the user's context. Ask if not clear.

**Environment quick-map** (the methodology is identical everywhere; only the renderer differs):

- **claude.ai (web/desktop chat):** the code-execution sandbox has `python-pptx` preinstalled and can run this skill's bundled scripts — Option D works with **zero setup** there (prefer it: deterministic MBB styling), and the validator (Step 5) runs too. Native file creation covers Option C.
- **Claude Code:** Option D needs local Python (`scripts/REQUIREMENTS.md`). Option C is available when the official `pptx` skill is installed (marketplace `anthropics/skills`, plugin `document-skills`) or another PowerPoint capability is present.
- **Anywhere else:** Options A and B always work — they are plain text.

**Option A — Markdown outline.** Produce a structured Markdown document the user pastes into PowerPoint, Keynote, or Google Slides. No tooling required on either end.

**Option B — Marp markdown.** If the user works in Marp (markdown-based slide tooling, version-controlled decks, exports to HTML/PDF/PPTX via Marp CLI), produce Marp-compatible markdown directly. See `references/marp-rendering.md` for the complete translation guide — frontmatter, slide patterns, columns, images, themes, and all syntax conventions. Themes are user-provided, not bundled.

**Option C — Native `.pptx` via an environment PowerPoint capability.** Covers whatever the host provides: the official Anthropic `pptx` skill (Claude Code: `/plugin install document-skills@anthropic-agent-skills`), claude.ai's built-in file creation, or Claude's PowerPoint add-in when working inside Office itself. Native renderers know nothing about MBB conventions — **always hand off the approved storyline together with the renderer handoff brief** from `references/output-formats.md` (style contract: typography, palette, chart rules, footers). Suggest this option when such a capability is available and Option D's requirements are not met.

**Mandatory after ANY native render (Option C):** run the deterministic lint on the produced file — `python scripts/lint_deck.py output.pptx` — and fix what it flags before showing the deck to the user. Native renderers improvise typography and color; the lint is what makes the style contract enforceable rather than hoped-for. It runs wherever Python + `python-pptx` exist, including claude.ai's sandbox.

**Option D — `.pptx` via the bundled Python script.** If the user has Python 3.9+ with `python-pptx` installed (see `scripts/REQUIREMENTS.md`), use `scripts/build_deck.py`:

```bash
python scripts/build_deck.py path/to/storyline.json --out output.pptx
```

Available palettes: `navy`, `red`, `green`, `neutral`. Set in `meta.palette` or override with `--palette`. On claude.ai this option needs no setup at all — `python-pptx` is preinstalled in the code-execution sandbox and the bundled scripts run there directly.

See `references/output-formats.md` for a full decision guide and worked examples of each option.

**Falling back gracefully.** If the user picks Option D but lacks Python, do NOT try to install Python on their behalf. Suggest A, B, or C instead. The MBB methodology applies identically to all rendering paths — the rendering is interchangeable.S

### Step 7 — (Before sharing) Run production QA

Hand the finished `.pptx` to the `qa-reviewer` subagent. It runs the deterministic lint (`scripts/lint_deck.py`) first — fonts, sizes, colors, bounds, jitter, page numbers, banned chart types are *measured*, not judged — then walks the judgment half of the production checklist (cover page, So-Whats, footnote conventions) and returns a pass/fail report with specific fixes. Address critical issues before sharing the deck externally.

### Step 8 — (Optional) Rehearse the live presentation

When the user will present live to an audience, offer the `chart-presenter` subagent — it generates a McCandless-method talking script for any data slide. Useful when the user has 30 seconds to 2 minutes per slide and needs to land the insight cleanly.

## Choosing the right agent

When the user's request matches one of these patterns, suggest the named agent:

| User signal                                                         | Agent to suggest         |
| ------------------------------------------------------------------- | ------------------------ |
| "I have data — what's going on?"                                    | `data-diagnostic`        |
| "What should we plan for next year?" / "Project our metrics"        | `forecast-modeler`       |
| "Why are customers churning?" / "Which cohorts retain?"             | `cohort-analyzer`        |
| "What do customers buy together?" / "What should we cross-sell?"    | `market-basket-analyzer` |
| "Review my storyline" / "Is this outline strong?"                   | `storyline-reviewer`     |
| "Is this deck ready to share?" / "QA my deck"                       | `qa-reviewer`            |
| "Help me present this slide" / "I'm rehearsing for a board meeting" | `chart-presenter`        |

Multiple agents can chain. A typical strategy deck might use: `data-diagnostic` (current state) → `forecast-modeler` (where it's going) → `/storyline` (draft) → `storyline-reviewer` → build deck → `qa-reviewer` → `chart-presenter` for live rehearsal.

## Standard deck structure

A 10–15 slide MBB-style deck typically follows this shape:

1. **Title slide** — document title (e.g., project or topic), client/department name, sub-headline, date (meeting or creation), team members, and clear internal vs. external positioning
2. **Executive summary** — the governing thought + 3–5 supporting arguments, each one sentence. The whole deck on one slide.
3. **Context / situation** — 1–2 slides
4. **Complication / problem framing** — 1–2 slides
5. **Approach / framework** — how the analysis was structured (often a 2x2, value chain, or MECE breakdown)
6. **Findings** — 3–5 slides, one finding per slide, each ladders to the governing thought
7. **Recommendation** — restate the answer, now with full backing
8. **Implementation / next steps** — roadmap, owners, timeline, milestones
9. **Appendix** — detailed data and methodology backing the findings

For details on each slide type, see `references/slide-patterns.md`.

## Anti-patterns (refuse or push back)

- **Topic titles.** "Market Overview" is wrong; "The market is consolidating around three players" is right.
- **Multiple ideas per slide.** Split it.
- **Decorative imagery, stock photos, gradients, 3D charts.** Strip them.
- **Bullet dumps.** Bullets must be parallel in structure and ladder to the slide title.
- **Recommendation buried at the end.** It belongs on slide 2.
- **Vague action titles** like "Revenue is doing well." Be specific: "Revenue grew 23% YoY, driven by enterprise expansion."
- **Action titles longer than two lines**. If you can't fit it in two lines, the claim is too compound — split the slide or sharpen the title.
- **Numbers in action titles that don't match the slide body.** Every number in the title must appear, identically, in the body.
- **Inconsistent footnote markers, units, or number formats.** Pick one footnote symbol style (e.g., ¹) and one number/currency format (e.g., €1,412.84) and use it across the entire deck.
- **Passive or vague recommendations.** "It might be worth considering" is not a recommendation. Use active voice with a clear subject and verb: "Acme should exit Segment C in Q3."
- **Pie charts. Banned outright** — the skill author's hard rule (no exceptions for "components" messages). Say so when a user asks for one, and render share-of-whole messages as a stacked column or a sorted bar chart instead. The validator and the deck lint both enforce this.
- **Clotheslines.** Long unordered lists of 5+ parallel items. Group them into labeled element groups (3 groups of 2 beat 1 list of 6) and consider a second dimension to turn the list into a table.
- **Colored boxes behind standard text.** Fills behind body text add ink without information. Reserve darker/colored fills for hierarchically superior text (column and section headers) — and apply that treatment consistently across the hierarchy level.
- **Single bullets and paragraph bullets.** A single bullet is not a list — write it as plain text. One idea per bullet, one line ideally, two lines maximum.
- **General truths and absolute claims.** "Managing risk is important for success" says nothing; "all divisions fail to follow best practices" leaves no room for outliers. Titles state specific, falsifiable insights.
- **Process narration.** Never "we conducted 15 interviews and learned a lot" — always what the interviews revealed. Focus on results, not process.

## Reference files and tools

For deeper detail on any topic, consult these files when relevant:

- `references/storyline.md` — Pyramid Principle, SCQA, governing thought construction, MECE
- `references/slide-patterns.md` — Common slide archetypes (2x2, value chain, comparison table, etc.)
- `references/visual-style.md` — Typography, color, charting rules, footnote conventions (canonical for `build_deck.py`)
- `references/output-formats.md` — When to pick Markdown outline vs. Marp vs. PowerPoint plugin vs. Python script
- `references/marp-rendering.md` — Complete reference for translating storyline JSON to Marp markdown (read fully before generating Marp output)
- `examples/sample-storyline.md` — Worked example of a full storyline before slide-building
- `examples/sample-storyline.json` — Same storyline as JSON, ready to feed to `build_deck.py`

Tools shipped with this skill (all optional — no rendering path is required):

- `scripts/build_deck.py` — converts a storyline JSON into a styled `.pptx`. Requires Python 3.9+ and `python-pptx`.
- `scripts/validate_storyline.py` — checks a storyline JSON against MBB rules (incl. title/number match, clotheslines, bullet discipline, chart taxonomy, the pie ban). Run before `build_deck.py`.
- `scripts/lint_deck.py` — deterministic visual lint for ANY finished `.pptx` (fonts, sizes, colors, bounds, jitter, page numbers, banned charts). Mandatory after native renders (Option C); `--profile dense` checks against the dense consulting-print standard.
- `scripts/REQUIREMENTS.md` — Python environment setup for the scripts above. Read before suggesting Option D.
- `assets/storyline_schema.json` — JSON schema documenting the storyline format
- `assets/palettes.json` — accent color palettes (navy / red / green / neutral) used by `build_deck.py`. Marp users can replicate these via inline CSS — see `references/marp-rendering.md`.
- `assets/style_config.json` — typography and layout configuration for `build_deck.py`
- `assets/example_deck.pptx` — a rendered example for visual reference
- `assets/icons/` — minimal SVG icons (arrows, harvey balls, check/x)

## Examples of action titles (good vs. bad)

| Topic title (bad) | Action title (good)                                                           |
| ----------------- | ----------------------------------------------------------------------------- |
| Market Overview   | The market is consolidating around three players, who now hold 71% share      |
| Customer Segments | Two of our four segments generate 85% of profit                               |
| Cost Analysis     | Procurement and logistics together account for 60% of controllable costs      |
| Recommendation    | We recommend exiting Segment C and reinvesting in Enterprise within 12 months |
