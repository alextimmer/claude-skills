# Icons

Minimal monochrome SVGs for use in MBB-style decks. All icons use `currentColor` so they inherit the fill/stroke color from where they're embedded — color them via your palette's accent or a neutral gray.

## Available icons

| File | Use for |
|---|---|
| `arrow-right.svg` | Value chain steps, sequential flows |
| `chevron-right.svg` | Compact "next step" indicators in tight layouts |
| `check.svg` | Affirmative ratings in comparison tables |
| `x.svg` | Negative ratings in comparison tables |
| `harvey-full.svg` | Full Harvey ball (4/4) — strongest rating |
| `harvey-three-quarter.svg` | Harvey 3/4 |
| `harvey-half.svg` | Harvey 2/4 |
| `harvey-quarter.svg` | Harvey 1/4 |
| `harvey-empty.svg` | Empty Harvey (0/4) — weakest rating |

## Embedding into a slide

The `build_deck.py` script does not currently embed SVGs directly (PowerPoint's SVG support varies). Two options:

1. **Use Unicode/text-based ratings** in comparison tables (the default in `comparison` slide type — uses words like "High"/"Medium"/"Low"). Simpler and renders identically everywhere.
2. **Add a custom slide type** that embeds these SVGs as pictures via `python-pptx`'s `add_picture` after converting them to PNG. Useful if you want a Harvey-ball comparison; left as an extension.

## Style guidelines

- Use only one icon weight per deck — don't mix outline and filled icons
- Color: accent color for emphasis, neutral gray for secondary
- Size: typically 0.25–0.5 inches in slide
- Never use multi-color icons or photographic clipart
