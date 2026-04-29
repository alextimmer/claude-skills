# Requirements for `build_deck.py` and `validate_storyline.py`

The Python scripts in this folder are **optional**. If you don't have a Python environment, use one of the other rendering options described in `references/output-formats.md` (Markdown outline, Marp markdown, or the PowerPoint Claude plugin).

## What's needed

| Requirement | Version | Why |
|---|---|---|
| Python | 3.9 or higher | f-strings, type hints, modern dict ordering |
| `python-pptx` | 0.6.21 or higher | Generates the `.pptx` file |

That's it. No other dependencies. The validator script (`validate_storyline.py`) needs only Python — no `python-pptx` required for it to run.

## Installation

If you have Python 3.9+ already:

```bash
pip install python-pptx
```

That's the whole setup. Verify with:

```bash
python3 -c "import pptx; print(pptx.__version__)"
```

You should see something like `0.6.23` or higher.

## If you don't have Python

You have three good alternatives — none require installing anything:

1. **Markdown outline** — Claude produces a structured outline you paste into PowerPoint, Keynote, or Google Slides. See `references/output-formats.md`.
2. **Marp markdown** — Claude produces Marp-compatible markdown. Renders to HTML/PDF/PPTX via the Marp CLI or VS Code extension. See `references/marp-rendering.md`.
3. **PowerPoint Claude plugin** — If the official PowerPoint Claude plugin is available in your environment, Claude can produce a real `.pptx` directly.

Pick whichever fits your workflow. The MBB methodology applies identically to all output paths — the rendering layer is interchangeable.

## If `pip install python-pptx` fails

Most common cause: `pip` is pointing at a Python version that's too old (often Python 2.7 on macOS).

Try:

```bash
python3 -m pip install python-pptx
```

Or if you use a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate        # Windows
pip install python-pptx
```

## Running the scripts

From the skill folder root:

```bash
# Validate a storyline JSON before rendering
python3 scripts/validate_storyline.py examples/sample-storyline.json

# Render a storyline JSON to .pptx
python3 scripts/build_deck.py examples/sample-storyline.json --out output.pptx

# Override the palette
python3 scripts/build_deck.py examples/sample-storyline.json --out output.pptx --palette red
```

The validator should be run before the builder — it catches structural issues that produce broken decks (missing fields, topic titles, MECE violations).

## What this skill does NOT install for you

If you don't have Python or `python-pptx`, this skill won't try to install them on your behalf. Suggesting `pip install` is one thing; running it from a shell tool is a system-level change that should be your call, not Claude's. Use one of the other rendering paths instead.
