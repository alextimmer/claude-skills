# Visual Style Guide

The MBB visual style is austere and disciplined. The goal is clarity and authority, not decoration.

## Typography

- **One font family for the entire deck.** No mixing. Sans-serif: Helvetica, Arial, or system equivalent. (Never Comic Sans, Calibri default decoration, or anything playful.)
- **Action title:** Bold, ~24pt, left-aligned, one or two lines maximum. Title color is the accent color.
- **Body text:** Regular weight, 14–18pt. Body text is dark gray (#333333), not pure black. **One font size for all body text on a page** — only the action title and footnotes differ from it.
- **Footnotes and source lines:** ~9pt, light gray (#888888), bottom of slide.
- **Maximum two font weights per slide** — e.g. bold for headers, regular for body.
- **ALL CAPS sparingly:** only for category labels and section markers, never body text.
- **Density profiles:** the sizes above are the *presentation readability* standard (this skill's default). When the deck is meant to be READ like a document rather than presented, switch to the *dense consulting-print* standard — title 18–22pt, body 8–11pt, footnotes 7–8pt — via the `dense` profile in `assets/style_config.json` (check with `lint_deck.py --profile dense`). **Never shrink below 8pt to fit content — cut content instead.**

## Color palette

Restrained. One accent color, used sparingly, plus grays and white.

- **Background:** White (#FFFFFF) or very light gray (#F5F5F5)
- **Accent (pick one and stick with it across the entire deck):**
  - McKinsey-style navy: `#003A70`
  - Bain-style red: `#CC0000`
  - BCG-style green: `#00543D`
  - Or a brand color the user provides
- **Body text:** Dark gray `#333333`
- **Footnotes:** Light gray `#888888`
- **Chart neutrals:** Use grays for non-emphasized data series. The accent color highlights the important data.

**Rule:** Color carries meaning. If a bar is in the accent color, it's the one the audience should look at. Don't color things just because.

**Maximum three colors in active use per slide** — primary, accent, neutral. The accent color is used for one thing only: the most important data point, call to action, or highlight. Keep contrast high (dark text on light backgrounds).

**No colored boxes behind standard text.** Regular content (table cell entries, bullets, explanations) sits on the plain slide background — fills behind standard text add ink without information and reduce readability. **The exception is hierarchically superior text:** column and section headers may carry a darker or colored background, precisely to underline the hierarchy. Apply the treatment consistently: if one header of a level carries a fill, all headers of that level do, and no lower-level text uses the same treatment. The fill signals hierarchy, never decoration.

## Charting rules

### Choose the chart from the comparison type of the MESSAGE

Derive the chart from what the title claims, not from the data shape:

| Comparison type of the message | Chart |
|---|---|
| Components (share of a whole) | Stacked column or **sorted bar** — **never a pie chart** (see below) |
| Items (absolute comparison) | Bar chart, waterfall |
| Time series | Line or column chart |
| Distribution | Column (histogram) or line |
| Correlation | Scatter, paired bars, or bubble (bubbles show x, y, and area — three dimensions) |

**Pie charts are banned in this skill — the skill author's hard rule, no exceptions.** When a user asks for one, say so explicitly and offer the sorted bar or stacked column instead. `validate_storyline.py` and `lint_deck.py` both enforce the ban mechanically.

**Reach for a waterfall whenever the message is "how did this number change" or "which drivers compose it"** — bridging a start value to an end value (FY25 ARR → FY27 ARR), or decomposing a total into contributions (price / volume / mix). It is the workhorse chart of professional services; when in doubt between a waterfall and a plain bar for a change-or-drivers message, take the waterfall.

### Craft rules

- No 3D
- No gradient fills
- No drop shadows
- No chart background
- **No screenshots of charts** — rebuild natively: screenshots can't highlight your message, clash with the document's look, and bring resolution problems
- Gridlines: only when essential, light gray, no major+minor combo
- Data labels: prefer direct labels on the chart over a separate legend — never force the reader to cross-reference
- Y-axis: usually start at zero (unless showing relative change is the explicit point)
- Series count: max 4 on a line chart, max 5 on a stacked bar
- Highlight the data point the action title is about (accent color); make all other data gray
- **Chart headers state the insight, not the metric** — "EBIT margin declines despite growth" beats "EBIT margin, %"
- **Anchor time series with CAGR labels** to state the growth story
- **Complete chart-title block:** what the reader sees, unit of measurement, time period, legend/key, source, and any qualifiers (scope, exclusions). Sort the data (largest first) — sorting is part of the craft

## Data tables

- Use a data table **only when the audience needs to look up specific values**; if the point is a trend or comparison, use a chart
- Highlight the one cell or row that carries the message
- Column headers short: one or two words
- **Numbers right-aligned, text left-aligned — always**

## Bullets and density

- Bullets always come in **groups of at least 2** — a single bullet is not a list; write it as plain text
- **Max 3–5 bullets per text box**; more → restructure or group
- One idea per bullet: one line ideally, two lines maximum; at most one level of sub-bullets
- Bullets are supporting evidence, not the message — the message is in the action title
- **The 90-second rule:** if a slide takes more than 90 seconds to read, it is too dense — cut content or split it
- **The squint test:** squint at the slide — the most important element must still be obvious
- Appendix slides may be denser: they are reference material, not presentation material

## First impressions (what reviewers see in the first seconds)

Before showing a deck to anyone, verify the first-seconds items: grouping and alignment, nothing out of bounds, consistent font sizes, parallel grammar in bullets, controlled white space, and selective bolding of the words that carry the message. Reviewers judge these within seconds; `lint_deck.py` measures most of them mechanically.

## Whitespace

Generous. The deck should feel uncrowded. Specifically:

- Margins: at least 0.5 inch on all sides, more if possible
- Title spacing: clear gap between the action title and body
- Body content: don't extend to the edges; leave breathing room
- If the slide feels full, you have too much on it — split it

## Footers (every slide except the title slide)

- **Bottom-left:** Source line. Format: `Source: Acme internal data, FY24; team analysis`
- **Bottom-right:** Page number. Just the number, no "Page" or "Slide" prefix.
- **Center (optional):** Confidentiality marking if needed (`Confidential — for [Client] only`)

Footer text is ~9pt, light gray, never bold.

## Title slide

The exception to everything above. Title slides typically have:

- Deck title (large, bold, accent color)
- Subtitle (smaller, dark gray)
- Date
- "Prepared for [Audience]" line
- "Prepared by [Team / Author]" line
- Optional small logo or wordmark
- No page number, no source line

## Images and icons

- Icons only when they help comprehension (process diagrams, framework illustrations)
- No stock photography
- No clip art
- If using icons: monochrome, all in the same style, all in the accent or gray color
- Logos: only when essential (e.g., showing competitor positioning)

## Animation and transitions

None. MBB decks are designed to be read on paper or PDF. Any reliance on animation makes the deck weaker as a standalone document.

## File-level conventions

- 16:9 aspect ratio
- One master template applied consistently across all slides
- File name: `[Client]_[Topic]_[YYYY-MM-DD]_v[N].pptx`
