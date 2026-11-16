# Skills directory

This folder holds the skills inside `mbb-deck-plugin`. Each skill is a subfolder with `SKILL.md` and supporting files, and each can be zipped and uploaded to Claude.ai on its own.

```
skills/
├── mbb-deck/                     ← decks: storyline JSON, validator, renderer, visual lint
│   ├── SKILL.md
│   ├── assets/
│   │   ├── icons/
│   │   ├── palettes.json
│   │   ├── storyline_schema.json
│   │   ├── style_config.json
│   │   └── example_deck.pptx     ← rendered from examples/sample-storyline.json
│   ├── examples/
│   │   ├── sample-storyline.json
│   │   └── sample-storyline.md
│   ├── references/
│   │   ├── marp-rendering.md
│   │   ├── output-formats.md
│   │   ├── slide-patterns.md
│   │   ├── storyline.md
│   │   └── visual-style.md
│   └── scripts/
│       ├── build_deck.py
│       ├── lint_deck.py
│       └── validate_storyline.py
├── executive-storyline/          ← everything that is not a slide: summaries, memos, pre-reads, emails
│   ├── SKILL.md
│   ├── examples/
│   │   ├── summary-from-deck.md
│   │   └── weak-vs-strong.md
│   ├── references/
│   │   ├── executive-summary.md
│   │   ├── feedback.md
│   │   └── method.md
│   └── scripts/
│       └── lint_prose.py
└── work-brief/                   ← the brief for someone who will do the work (AI tool, colleague, agency)
    ├── SKILL.md
    ├── examples/
    │   └── brief-for-a-summary.md
    └── references/
        └── templates.md
```

## How the two relate

Both skills teach the same storyline method (governing thought first, MECE arguments, content over process, defined numbers, decision needs at the close). Each carries its own copy of the method so that either works when uploaded alone:

- `mbb-deck/references/storyline.md` — the method as it applies to slides
- `executive-storyline/references/method.md` — the method for any asset

When one changes, check the other. `work-brief` shares only the vocabulary (audience, objective, key message) and has no copy of the method. The filler-word and process-statement patterns are likewise kept in step between `mbb-deck/scripts/validate_storyline.py` and `executive-storyline/scripts/lint_prose.py`.

## Regenerating the example deck

```bash
python mbb-deck/scripts/build_deck.py mbb-deck/examples/sample-storyline.json --out mbb-deck/assets/example_deck.pptx
```
