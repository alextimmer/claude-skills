---
name: mbb-deck
description: Use this skill whenever the user wants to create, improve, or review a presentation, deck, slides, or a one-pager in MBB / management consulting style (McKinsey, Bain, BCG style). Trigger on requests for "consulting deck", "strategy presentation", "executive briefing", "board deck", "steering committee deck", "decision pre-read", "MBB style", "pyramid principle", "management consulting deck", "slide writing", "action title", "review my deck/slides", "give feedback on this deck", or whenever the user asks for slides that need a clear recommendation, action titles, MECE structure, or executive-level polish. Covers both creating decks and reviewing existing ones. Do not trigger for casual or creative presentations (kids' birthday slideshow, photo deck, casual class lecture). For executive summaries, memos, emails to leadership or spoken updates that are not slides, use the executive-storyline skill.
---

# MBB-Style Presentation Skill

Build presentations in the structural style of top-tier management consulting firms. The hallmarks: an answer-first storyline, action titles, MECE structure, and one idea per slide.

The skill has two modes: **create** (develop storyline and slides — the workflow below) and **feedback** (review a draft deck against the standard — use `/critique-deck` for content and storyline, the `qa-reviewer` subagent for production polish; both run the deterministic lint first).

**Terms.** The *governing thought* is the single statement the deck must leave behind; many teams call it the *key message*. Below it sit the *arguments*, and below each argument its *evidence*. Keep the three apart.

**Not a deck?** The sibling skill `executive-storyline` applies the same storyline method to executive summaries, memos, emails to leadership and spoken updates — including the email that travels with a finished deck (`/exec-summary`). A third, `work-brief`, writes the brief when someone else (a colleague, an agency, another AI tool) will produce the deck.

## Ten core principles

1. **Answer first (Minto Pyramid).** State the recommendation up front, then the supporting arguments, then the evidence. The reader should know your conclusion from the executive summary slide. Work runs bottom-up, communication runs top-down: never present in the order you worked.
2. **Action titles, not topic titles.** Every slide title is a complete declarative sentence stating the takeaway. "Revenue grew 23% YoY, driven by enterprise" — not "Revenue Trends". The title alone should convey the insight.
3. **One idea per slide.** If you can't summarize the slide in a single sentence, split it into two slides. If content does not support that one message: **if in doubt, leave it out.**
4. **MECE structure.** Categories must be Mutually Exclusive and Collectively Exhaustive. No overlap, no gaps.
5. **Source everything.** Cite sources in a small footnote (typically ~9pt, gray) at the bottom-left of any data slide.
6. **Action title + framing line**. Beneath the action title, add a short subtitle (~10–15 words) that states the logic, methodology, or sample size. Title says what's true; framing line says how we know. Examples: "Based on n=240 customer interviews", "Acme analysis vs. industry benchmark", "Excludes one-time charges".
7. **Build data slides so they narrate themselves (McCandless).** Any chart or data slide must support a five-step read: (1) the chart can be named, (2) obvious questions are answered on the slide itself (axes, units, period, n), (3) the action title states the insight, (4) the specific data points proving the insight are visually highlighted (accent color on the relevant bar; gray on the rest), (5) the takeaway sets up the next slide. If a slide can't be talked through this way, the slide isn't done.
8. **Every slide is a table.** Think of any layout as rows and columns (rows = items, columns = dimensions such as measure, rationale, impact, timing). This single principle produces clean, structured pages and prevents scattered elements. It is a rule of thumb — adjust when a chart or framework demands it.
9. **Horizontal and vertical logic.** Read all action titles in sequence: they must tell the storyline of the document by themselves (horizontal logic). On each slide, the content must fully support its title (vertical logic). Both are tested explicitly during review.
10. **Synthesize, do not summarize.** Slides state implications (the "So What"), not just organized facts. "We win 40% of negotiations" is a fact; "Negotiation conversion declined from 55% to 40%, likely driven by recent scaling of the sales team" is an insight. Every finding can be stated as data, summary, insight or so what; the standard is the last two (`references/storyline.md`).

## Agents and tools available in this plugin

This plugin ships several subagents that handle specific phases of the work. Suggest them at the right moments in the workflow below — they run in their own context and return structured output without polluting the main conversation.

Subagents and slash commands come with the plugin (Claude Code and Claude Cowork both load them). Where the skill is loaded on its own, as an uploaded skill folder, do the same work inline: the reviewer's checks are the "Test your storyline" list in `references/storyline.md`, and the production checklist is in `references/visual-style.md`. Nothing in the method depends on them.

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
- `/exec-summary <path or pasted content>` — condenses a finished deck or document into an executive summary for an email, a one-pager or a spoken update (uses the `executive-storyline` skill).

## Data sources for the analytical agents

The analytical agents (`data-diagnostic`, `forecast-modeler`, `cohort-analyzer`, `market-basket-analyzer`) need data as input. Claude has multiple ways to get data into context — file uploads, code execution, filesystem reads, MCP database connectors — depending on the host environment. You don't need to know which mechanism is available; just ask the user how they want to share their data:

- Paste the metrics or a summary directly into the conversation
- Upload a CSV, Excel, or JSON file
- Point at a file path (Claude Code with filesystem access)
- Pull from a connected service (Google Drive, Notion, or a database via MCP)

If the user gestures at data without providing it ("build a deck from our Q3 numbers") and nothing is in context yet, ask once which method they want to use. Do not invent or estimate values to fill gaps — the analytical agents have explicit guards against that and will refuse to produce confident output on missing data.

## Workflow when the user requests a deck

Follow these steps in order. Do not skip to slide-building before the storyline is approved.

### Step 0 — Clarify audience, objective and document type

Before the message, the reader. Ask only for what is not already clear:

- **Audience:** who decides, who influences, and what is each decision maker's main concern? A strong storyline answers that concern before it is raised.
- **Objective:** what should the audience do after reading — and how far can one meeting realistically move them (unaware → aware → understands → buys in → acts)?
- **Document type:** it sets the bar and the length. Record it as `meta.document_type`; the validator calibrates to it.

| `document_type` | What it is | Bar |
|---|---|---|
| `team_alignment` | Thoughts on paper for the team | Concise; no polish, no elaborate storyline |
| `recurring_update` | Jour fixe, weekly or monthly status | Consistent structure, clean pages |
| `board` | Board and senior management deck | Full rigor: executive summary, decision needs, next steps; stands alone without a presenter |
| `decision_pre_read` | Pre-read for a decision meeting | Cover, one-page executive summary, up to four pages; decisions asked in the summary and repeated on the last page |
| `external` | Client, investor or public audience | Board rigor plus legal and PR review |
| `documentation` | A record to be read later | May be wordy; must stand fully on its own |
| `keynote` | Live talk to a large audience | Few memorable messages, visual slides; the presenter is the soundtrack |

**Optional structures — offer them when they pay off, never by default.** Each one is extra input from the user, so ask once, in a single question, only when its trigger applies, and accept "no":

| Structure | Offer it when | Otherwise |
|---|---|---|
| `meta.stakeholders` — per decision maker: role, where they stand and must get to on the commitment ladder, main concern | A decision document with two or more decision makers who stand in different places, or a contested message | One line in `meta.audience` is enough |
| `meta.key_figures` — what each headline number measures, against which reference, for which period | The governing thought or a decision rests on a number, or the audience has seen the figure before in another form | Skip |
| `name` on a slide — "the savings page" | A pre-read, or a summary or email will point into the deck | Skip. Names are metadata and are never printed on the slide |
| `callout` on a slide — a short outlined box | A main concern or a caveat belongs on one specific page (e.g. why a figure differs from one quoted earlier) | Skip |
| Pre-alignment list — who to speak to one-to-one before the meeting, about which concern | The storyline is approved and main concerns are known | Skip |

The pre-alignment list is working advice: give it in the conversation. Put it into the deck only if the user asks, and then in the appendix.

### Step 1 — Establish the governing thought

Ask the user (if not already clear): **"What is the single recommendation or key message this deck should leave the audience with?"**

The governing thought is one sentence. Every slide ladders up to it. If the user can't articulate it in one sentence, the thinking is not done — work with them to sharpen it before moving on. Test it: what should senior management do differently after hearing it (the CEO test)? The governing thought is the user's decision; propose options, then get it confirmed.

### Step 2 — Draft the storyline using SCQA

Before any slides, write out the Situation–Complication–Question–Answer structure:

- **Situation** — current state, accepted facts, no controversy
- **Complication** — what makes the situation worth attention now. Not necessarily a problem: something went wrong, could go wrong, changed, could change, is disputed, or offers several alternatives
- **Question** — the question the complication raises. Write it down (`meta.question`) even if the deck only implies it; the governing thought must answer exactly this question
- **Answer** — the governing thought (the recommendation)

Top-down is the default: the opening takes roughly 10–20% of the deck, the arguments and their evidence the rest. Give the situation and complication more room only when the audience is new to the topic or the message is controversial.

### Step 3 — Outline every slide as just an action title

List the action titles in sequence — 10–15 for a board deck, at most four pages after the executive summary for a decision pre-read. Each title is a complete sentence. Reading the titles top-to-bottom should tell the whole story without seeing any slide bodies.

Build the outline from the pyramid, not from the work plan:

- **Three arguments, five at most,** on one logical level and along one dimension (MECE). Name the order you use: temporal, importance, causal, or structural.
- **Evidence gets a home.** Map every analysis to the argument it supports; what supports none is cut or moves to the appendix.
- **Close with what you need.** A senior document ends on its decision needs (which, by when, why now) and next steps (task, owner, date) — the `decisions` slide — not on a data page.

**Get explicit user approval on this storyline before building slide content.** This is the most important review gate.

### Step 3.5 — (Recommended for high-stakes decks) Get an isolated review

Hand the storyline to the `storyline-reviewer` subagent. It returns a structured critique covering the governing thought, action titles, pyramid integrity, and MECE — without polluting this conversation with critique back-and-forth. Iterate on the storyline until the reviewer is satisfied, then proceed to Step 4.

For decks that depend on data analysis, this is also where the analytical agents (`data-diagnostic`, `forecast-modeler`, `cohort-analyzer`, `market-basket-analyzer`) feed in. If the storyline is forecast-driven and `forecast-modeler` has not run yet, run it now — its scenario range and decision triggers must be in hand by Step 4, where they become the substance of the recommendation slides.

### Step 4 — Build the slide content

Build every slide in this order — never start with the visual or the text:

1. **Message.** The one message of the slide, written down as the action title. If the message is not clear, the slide is not ready to be built.
2. **Layout.** Choose the layout — in table format where applicable (rows = items, columns = dimensions). See the three layout archetypes in `references/slide-patterns.md`.
3. **Main visual.** The centerpiece, typically the chart. Choose the chart type from the *message's comparison type*, not from the data shape (`references/visual-style.md`).
4. **Supporting text.** Bullets, labels, callouts, takeaway box — parallel grammar, groups of at least 2, max 5 per box.
5. **Polish.** Alignment, consistency, no jitter.

Before finalizing any slide, run the **10-second executive test**: can a senior executive get the point in 10 seconds? Does the title tell them what to think? Could any element be removed without losing the message? Would you be comfortable if only the titles were read aloud?

**How to capture the content depends on what will render it (Step 6).** The storyline JSON (`assets/storyline_schema.json`, worked example in `examples/sample-storyline.json`) is the input format of this skill's own validator and renderer. It is a tool, not a requirement: when the environment's own slide capability builds the deck, hand it the content in whatever form it takes and do not convert to JSON first.

### Step 5 — Validate the storyline

**With a storyline JSON**, run the validator before rendering:

```bash
python scripts/validate_storyline.py path/to/storyline.json
```

Address any ERROR-level issues. WARNING-level issues (e.g., topic titles, process titles, missing exec summary up front, a senior document without a decisions slide, executive-summary figures that appear on no page, filler wording) should also be fixed unless there's a deliberate reason. The page-count and decision-needs checks follow `meta.document_type`.

**Without a JSON**, run the same checks by reading: the "Test your storyline" list in `references/storyline.md`.

### Step 6 — Render with what the environment offers

The method is this skill's business. How the file gets made is the environment's. Decide in this order:

1. **The environment has its own way to make presentations — use it, the way it normally works.** This covers a desktop agent or chat with built-in file creation (Claude Cowork, claude.ai), a PowerPoint or Google Slides integration, an installed presentation skill, or the user's own template and brand tooling. Do not route the deck through this skill's scripts there, and do not ask the user to choose a renderer. Hand over the approved storyline and slide content together with the style guidance from `references/output-formats.md`.
2. **The user builds decks in other tooling, or asks for it — use the matching option below.** A Markdown outline to paste, Marp markdown, or the bundled Python renderer.
3. **Neither is clear — ask once** which format they want.

**Style guidance yields to the user's template.** The typography and palette in `references/visual-style.md` are this skill's defaults for a deck with no house style. A corporate template, a brand palette or the environment's design system takes precedence over them. What never yields is the content standard: one message per slide, action titles, sources, the storyline.

The options, for cases 2 and 3:

**Option A — Markdown outline.** A structured Markdown document the user pastes into PowerPoint, Keynote, or Google Slides. No tooling required on either end.

**Option B — Marp markdown.** For users who work in Marp (markdown-based slide tooling, version-controlled decks, exports to HTML/PDF/PPTX via Marp CLI). See `references/marp-rendering.md` for the complete translation guide — frontmatter, slide patterns, columns, images, themes, and all syntax conventions. Themes are user-provided, not bundled.

**Option C — Native `.pptx` via the environment's capability.** Case 1 above, named here for completeness: whatever the host provides. Hand off the approved storyline together with the renderer handoff brief from `references/output-formats.md`.

**Option D — `.pptx` via the bundled Python script.** For Claude Code, CI and other setups with Python 3.9+ and `python-pptx` (see `scripts/REQUIREMENTS.md`) where a deterministic, palette-consistent deck from a storyline JSON is wanted:

```bash
python scripts/build_deck.py path/to/storyline.json --out output.pptx
```

Available palettes: `navy`, `red`, `green`, `neutral`. Set in `meta.palette` or override with `--palette`. Use it when the user asks for it or already works this way; do not reach for it merely because Python happens to be available.

See `references/output-formats.md` for a full decision guide and worked examples of each option.

**An optional measured check.** `python scripts/lint_deck.py output.pptx` measures any finished `.pptx` — fonts, sizes, colors, bounds, jitter, page numbers, banned chart types. Run it when Python with `python-pptx` is at hand and the deck follows this skill's default style. When a template or brand governs the look, its typography and color findings are advisory; bounds, page numbers and the pie ban still apply.

**Falling back gracefully.** If the user picks Option D but lacks Python, do NOT try to install Python on their behalf. Suggest A, B, or C instead. The MBB methodology applies identically to all rendering paths — the rendering is interchangeable.

### Step 7 — (Before sharing) Run production QA

Hand the finished `.pptx` to the `qa-reviewer` subagent (or walk its checklist inline where subagents are unavailable). It runs the deterministic lint (`scripts/lint_deck.py`) first where Python is available — fonts, sizes, colors, bounds, jitter, page numbers, banned chart types are *measured*, not judged — then walks the judgment half of the production checklist (cover page, So-Whats, footnote conventions) and returns a pass/fail report with specific fixes. Address critical issues before sharing the deck externally.

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
2. **Executive summary** — context in two sentences, the governing thought, 3–5 supporting arguments (one per section, each opening with a bold lead that mirrors the section's action title), and the decision needs in their own box. The whole deck on one slide.
3. **Context / situation** — 1–2 slides
4. **Complication / problem framing** — 1–2 slides
5. **Approach / framework** — how the analysis was structured (often a 2x2, value chain, or MECE breakdown)
6. **Findings** — 3–5 slides, one finding per slide, each ladders to the governing thought
7. **Recommendation** — restate the answer, now with full backing
8. **Implementation** — roadmap, owners, timeline, milestones
9. **Decision needs and next steps** — which decisions, by when, why now; each paired with its safeguard and an owner; then task, owner, date
10. **Appendix** — detailed data and methodology backing the findings

**Decision pre-read variant:** cover, executive summary, up to four pages, the last of which is the decisions page. Refer to pages by name ("the savings page"), not by number. Everything else is appendix.

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
- **Process narration.** Never "we conducted 15 interviews and learned a lot" — always what the interviews revealed. Focus on results, not process. Process appears at most once, as the next step.
- **Work-order narrative.** A deck that retells the project chronologically ("first we analyzed, then we found"). Invert it into pyramid order.
- **Ending without an ask.** A senior deck that closes on a data page or on "let's discuss". State the decisions, the deadline and why now.
- **Undefined or shifting numbers.** Every figure names what is measured, against which baseline, for which period — in the reader's own baseline — and is identical in the executive summary, on the pages and in the appendix.
- **Filler wording.** Stock words (leverage, robust, comprehensive, holistic, seamless, unlock), empty intensifiers and exclamation marks. Replace each with the concrete point, number or decision. The validator flags them.

## Reference files and tools

For deeper detail on any topic, consult these files when relevant:

- `references/storyline.md` — Pyramid Principle, SCQA, governing thought construction, MECE, the four levels from data to so what, numbers and claims, decision needs, document types
- `references/slide-patterns.md` — Common slide archetypes (2x2, value chain, comparison table, etc.)
- `references/visual-style.md` — Typography, color, charting rules, footnote conventions (canonical for `build_deck.py`)
- `references/output-formats.md` — When to pick Markdown outline vs. Marp vs. PowerPoint plugin vs. Python script
- `references/marp-rendering.md` — Complete reference for translating storyline JSON to Marp markdown (read fully before generating Marp output)
- `examples/sample-storyline.md` — Worked example of a full storyline before slide-building
- `examples/sample-storyline.json` — Same storyline as JSON, ready to feed to `build_deck.py`

Tools shipped with this skill (all optional — no rendering path is required, and none should displace the environment's own way of making slides):

- `scripts/build_deck.py` — converts a storyline JSON into a styled `.pptx`. Requires Python 3.9+ and `python-pptx`.
- `scripts/validate_storyline.py` — checks a storyline JSON against MBB rules (incl. title/number match, clotheslines, bullet discipline, chart taxonomy, the pie ban, process titles, filler wording, executive-summary number drift, and the decision-needs close for senior document types). Run before `build_deck.py`.
- `scripts/lint_deck.py` — deterministic visual lint for ANY finished `.pptx` (fonts, sizes, colors, bounds, jitter, page numbers, banned charts). An optional measured check; typography and color findings are advisory when a template governs the look. `--profile dense` checks against the dense consulting-print standard.
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
