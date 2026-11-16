# Output formats — choosing the right one

Storyline JSON is **format-agnostic**. The same storyline can be rendered four different ways. This doc explains when to pick which.

The four options:

| # | Output | Tooling | When to use |
|---|---|---|---|
| A | Structured Markdown outline | None — Claude writes it inline | User builds the deck themselves in PowerPoint, Keynote, or Google Slides |
| B | Marp markdown | None — Claude writes Marp-compatible `.md` directly | User works in Marp (markdown-based slide tooling, version-controlled decks, exports to HTML/PDF/PPTX via Marp CLI) |
| C | Native file via the environment's own capability | Whatever the host provides: built-in file creation (Cowork, claude.ai), a PowerPoint or Google Slides integration, an installed presentation skill, the user's template tooling | **Default wherever such a capability exists.** The environment makes the file its usual way; this skill supplies storyline, content and style guidance |
| D | `.pptx` via bundled Python script | `scripts/build_deck.py` + Python with `python-pptx` | Claude Code, CI and similar setups where a deterministic deck from a storyline JSON is wanted, or the user asks for it |

## The decision

**First: does the environment have its own way to make presentations?** A desktop agent or chat with built-in file creation (Claude Cowork, claude.ai), a PowerPoint or Google Slides integration, an installed presentation skill, or the user's own template tooling. If so, use it the way it normally works — that is Option C — and do not ask the user to pick a renderer or route the deck through this skill's scripts. This skill contributes the storyline, the slide content and the style guidance; the environment contributes the file.

Options A, B and D exist for decks made in other tooling: an outline to paste, Marp, or the bundled Python renderer for Claude Code and CI.

Only if neither the environment nor the user's context settles it, ask once:

> Which format do you want the deck in? I can produce: (a) a structured Markdown outline you can paste into PowerPoint or Keynote, (b) Marp markdown, or (c) a styled `.pptx` via the bundled Python script (needs Python with `python-pptx`).

If the user has given context that implies a format, infer:

- They mentioned PowerPoint, Keynote, or Google Slides as their target tool → Option A
- They mentioned Marp, version control, GitHub Pages publishing, or "markdown decks" → Option B
- The `pptx` skill or other PowerPoint tools are visible in the environment, or they mentioned a PowerPoint plugin/add-in → Option C
- They explicitly asked for a `.pptx` and have Python available → Option D
- The environment creates files or presentations natively (Cowork, claude.ai) and they want a deck → Option C, with the environment's usual tooling. Option D only if they ask for the bundled script

## Option A — Structured Markdown outline

The user builds the deck themselves. You produce a markdown document like this:

```markdown
# Deck: [Title]

## Slide 1 — Title slide

- Title: ...
- Subtitle: ...
- Date: ...
- Prepared for / by: ...

## Slide 2 — Executive summary

**Action title:** [governing thought]
**Framing line:** [methodology / sample / scope]

Context: [situation and complication, two sentences]

Supporting points:
1. **[Lead mirroring section 1]** ...
2. ...
3. ...

Decisions needed: 1. ... 2. ...   Why now: ...

Source: ...

## Slide 3 — [Action title for slide 3]

**Framing line:** ...

[Body content — bullets, table, or chart description]

Source: ...

...
```

A `decisions` slide is written out as its table (decision, safeguard, owner, by when), the "why now" line, and the next steps (task, owner, date).

The user can copy each slide block into PowerPoint or Keynote one slide at a time. No tooling required on either end.

## Option B — Marp markdown

See `references/marp-rendering.md` for the complete guide on translating storyline JSON to Marp markdown — frontmatter, slide patterns, columns, images, themes, and all the syntax conventions.

Choose Marp when the user wants:
- Version-controlled decks (markdown diffs cleanly in git)
- Quick HTML or PDF export via Marp CLI or the VS Code extension
- The same source file rendering to multiple targets
- A simple, theme-able alternative to PowerPoint

## Option C — Native `.pptx` via an environment PowerPoint capability

"Native" means whatever the host environment provides for creating `.pptx` files. Verified instances (as of 2026-07):

- **Official Anthropic `pptx` skill** — in Claude Code: `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills`; appears as the `pptx` skill.
- **claude.ai file creation** — Claude's built-in code-execution sandbox creates `.pptx` files directly (feature: "Create and edit files").
- **Claude's Office add-ins** — when the user works inside PowerPoint itself with Claude's add-in.
- **Other agent environments (for example Claude Cowork)** — use whatever presentation tooling the environment brings. This skill makes no assumption about it and adds no requirement to it.

Detect availability by: the user mentioning one of these, a `pptx` skill or PowerPoint tools visible in the environment, or the user asking for a `.pptx` when Option D's requirements aren't met.

When you hand off, give the renderer the structured content (action titles, framing lines, body content, sources) **plus the renderer handoff brief below** — native renderers know nothing about MBB conventions. Run the Step 7 QA pass on whatever comes back.

**The user's template wins.** The typography and palette in the brief are defaults for a deck with no house style. If the user has a corporate template, a brand palette, or the environment applies its own design system, follow that and drop the conflicting lines of the brief. The content rules (one message per slide, action titles, framing lines, sources, no decoration) stay.

## Option D — `.pptx` via `build_deck.py`

The bundled Python script. See `scripts/REQUIREMENTS.md` for setup. This is the most controlled output — same deck every time, palette-consistent, footers and pagination automatically applied — but the highest setup cost (requires a Python env with `python-pptx`).

When this is right:
- The user has Python set up and confirms it
- The user asks for it in an environment where Python with `python-pptx` is already present
- They want consistent styling across many decks (CI-friendly)
- They want palette options (navy / red / green / neutral) without manual styling

When it's wrong:
- The user has no Python env (suggest A, B, or C instead — don't try to install Python for them)
- The user wants extensive custom styling that diverges from the four palettes (suggest C if available, otherwise A)

## The renderer handoff brief (for Option C and any native renderer)

When a renderer other than `build_deck.py` produces the actual `.pptx` (claude.ai file
creation, the official pptx skill, a PowerPoint plugin), the MBB style must travel with
the content — those renderers know nothing about this skill's conventions. Alongside
the slide-by-slide content from the storyline JSON, always pass this style contract
(distilled from `references/visual-style.md`, the canonical source — read it first):

- **Typography:** sans-serif (Helvetica/Arial); action title bold ~24pt in the accent
  color, max two lines, left-aligned; body 14–18pt in `#333333` (never pure black);
  footnotes/sources ~9pt in `#888888`.
- **Palette:** ONE accent + grays + white, from `assets/palettes.json` — navy `#003A70`,
  red `#CC0000`, green `#00543D`, or neutral `#333333`; background white.
- **Charts:** no 3D, no gradients, no shadows, no chart backgrounds; the data point the
  action title is about gets the accent color, every other series gray; direct labels
  over legends; y-axis from zero unless relative change IS the point.
- **Every slide (except title):** framing line under the action title; source line
  bottom-left (`Source: ...`), page number bottom-right, both ~9pt gray.
- **Executive summary and decisions slides:** supporting points keep their bold leads
  (`**lead**` in the JSON means bold, not literal asterisks); the decision needs sit in
  an outlined box without a fill; the decisions slide is a plain table whose only
  filled element is the header row.
- **Forbidden:** stock photos, clip art, decorative icons, gradients, animations,
  more than one idea per slide.

State these in the handoff (or the generation prompt) — as constraints when no template
governs the look, as defaults to be overridden when one does. If the renderer produced the deck, still run the Step 7 QA pass — `qa-reviewer`
checks the result, not the pipeline that made it.

## On falling back gracefully

If the user picks Option D but doesn't have Python, **don't try to install it**. Suggest Option A (Markdown outline they paste) or Option B (Marp markdown) instead. The skill's value is the methodology — the rendering is interchangeable.
