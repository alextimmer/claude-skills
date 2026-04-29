# Skills directory

This folder holds the actual skills inside `mbb-deck-plugin`. Each skill is a subfolder with `SKILL.md` and supporting files.

## What goes here

Your existing `mbb-deck/` folder. After moving it into place, this directory should look like:

```
skills/
└── mbb-deck/
    ├── SKILL.md
    ├── assets/
    │   ├── icons/                ← (already added by the additions zip)
    │   ├── palettes.json
    │   ├── storyline_schema.json
    │   ├── style_config.json
    │   └── example_deck.pptx     ← (regenerate with build_deck.py once)
    ├── examples/
    │   ├── sample-storyline.json
    │   └── sample-storyline.md
    ├── references/
    │   ├── slide-patterns.md
    │   ├── storyline.md
    │   └── visual-style.md
    └── scripts/
        ├── build_deck.py
        └── validate_storyline.py
```

## Once your files are in place

You can delete this README — it's only here to mark the folder.
