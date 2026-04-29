# Output formats — choosing the right one

Storyline JSON is **format-agnostic**. The same storyline can be rendered four different ways. This doc explains when to pick which.

The four options:

| # | Output | Tooling | When to use |
|---|---|---|---|
| A | Structured Markdown outline | None — Claude writes it inline | User builds the deck themselves in PowerPoint, Keynote, or Google Slides |
| B | Marp markdown | None — Claude writes Marp-compatible `.md` directly | User works in Marp (markdown-based slide tooling, version-controlled decks, exports to HTML/PDF/PPTX via Marp CLI) |
| C | Native `.pptx` via PowerPoint Claude plugin | The official PowerPoint plugin | User has the official PowerPoint Claude plugin enabled — produces a real `.pptx` without needing local Python |
| D | `.pptx` via bundled Python script | `scripts/build_deck.py` + Python with `python-pptx` | User has Python 3.9+ with `python-pptx` installed and wants a deterministic, locally-styled deck |

## The decision

If the user hasn't said which they want, ask once:

> Which format do you want the deck in? I can produce: (a) a structured Markdown outline you can paste into PowerPoint or Keynote, (b) Marp markdown, (c) a real `.pptx` via the PowerPoint plugin if you have it enabled, or (d) a styled `.pptx` via a Python script if you have Python with `python-pptx` installed.

If the user has given context that implies a format, infer:

- They mentioned PowerPoint, Keynote, or Google Slides as their target tool → Option A
- They mentioned Marp, version control, GitHub Pages publishing, or "markdown decks" → Option B
- They mentioned the PowerPoint Claude plugin, or you can see PowerPoint plugin tools available in the environment → Option C
- They explicitly asked for a `.pptx` and have Python available → Option D

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

Supporting points:
1. ...
2. ...
3. ...

Source: ...

## Slide 3 — [Action title for slide 3]

**Framing line:** ...

[Body content — bullets, table, or chart description]

Source: ...

...
```

The user can copy each slide block into PowerPoint or Keynote one slide at a time. No tooling required on either end.

## Option B — Marp markdown

See `references/marp-rendering.md` for the complete guide on translating storyline JSON to Marp markdown — frontmatter, slide patterns, columns, images, themes, and all the syntax conventions.

Marp is the right choice when the user wants:
- Version-controlled decks (markdown diffs cleanly in git)
- Quick HTML or PDF export via Marp CLI or the VS Code extension
- The same source file rendering to multiple targets
- A simple, theme-able alternative to PowerPoint

## Option C — Native `.pptx` via PowerPoint Claude plugin

If the official PowerPoint Claude plugin is available in the user's environment, hand off to it. The plugin can produce real `.pptx` files via Microsoft Office's API without needing local Python.

You can detect availability by:
- The user mentioning it explicitly
- Seeing PowerPoint-related tools in the available tools list
- The user asking for a `.pptx` and not having Python set up

When you hand off, give the plugin the structured content it needs (action titles, framing lines, body content, sources). The plugin handles the rendering.

## Option D — `.pptx` via `build_deck.py`

The bundled Python script. See `scripts/REQUIREMENTS.md` for setup. This is the most controlled output — same deck every time, palette-consistent, footers and pagination automatically applied — but the highest setup cost (requires a Python env with `python-pptx`).

When this is right:
- The user has Python set up and confirms it
- They want consistent styling across many decks (CI-friendly)
- They want palette options (navy / red / green / neutral) without manual styling

When it's wrong:
- The user has no Python env (suggest A, B, or C instead — don't try to install Python for them)
- The user wants extensive custom styling that diverges from the four palettes (suggest C if available, otherwise A)

## On falling back gracefully

If the user picks Option D but doesn't have Python, **don't try to install it**. Suggest Option A (Markdown outline they paste) or Option B (Marp markdown) instead. The skill's value is the methodology — the rendering is interchangeable.
