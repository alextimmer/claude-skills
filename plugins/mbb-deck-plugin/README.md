# mbb-deck-plugin

Build presentations in the structural style of top-tier management consulting firms (McKinsey, Bain, BCG). Enforces the Pyramid Principle, action titles, MECE structure, and minimal executive-grade visuals.

This plugin is part of the [`claude-skills`](../../) marketplace.

## What's inside

```
mbb-deck-plugin/
├── .claude-plugin/
│   └── plugin.json                    ← plugin manifest
├── agents/                            ← Claude Code subagents
│   ├── storyline-reviewer.md          ← critiques storylines before slide-building
│   └── qa-reviewer.md                 ← runs production QA on finished decks
├── commands/                          ← Claude Code slash commands
│   ├── storyline.md                   ← /storyline — drafting mode for storyline + SCQA + action titles
│   └── critique-deck.md               ← /critique-deck <path> — MBB-style review of an existing pptx
└── skills/
    └── mbb-deck/                      ← the actual skill — what Claude reads at runtime
        ├── SKILL.md                   ← entrypoint
        ├── references/                ← deeper docs Claude pulls in on demand
        ├── examples/                  ← worked storyline examples (md + json)
        ├── scripts/                   ← build_deck.py, validate_storyline.py
        └── assets/                    ← palettes, schema, icons, example deck
```

## Install in Claude Code

```bash
/plugin marketplace add YOUR_USERNAME/claude-skills
/plugin install mbb-deck-plugin@claude-skills
```

Then ask Claude something like:

> Build me an MBB-style deck recommending whether we should expand to Germany.

The skill triggers automatically.

## Use just the skill in Claude.ai

Zip the inner skill folder (`skills/mbb-deck/`) and upload it via Customize → Skills → Upload:

```bash
cd skills
zip -r mbb-deck.zip mbb-deck/
```

Note: Claude.ai uploads do NOT include the slash commands or subagents in this plugin — those are Claude Code features. If you need just the methodology and the build script, the skill folder alone is enough.

## Workflow at a glance

1. User asks for a strategy/consulting deck → `mbb-deck` skill activates
2. Claude works through the storyline first (governing thought → SCQA → action titles), gets approval
3. (Optional) Hand the storyline to `storyline-reviewer` subagent for an isolated critique
4. Claude generates a structured JSON storyline matching `assets/storyline_schema.json`
5. `scripts/validate_storyline.py` checks for topic titles, MECE issues, missing fields
6. `scripts/build_deck.py` produces the styled `.pptx`
7. (Optional) Hand the finished deck to `qa-reviewer` subagent for production polish check

The two slash commands (`/storyline`, `/critique-deck`) are user-invoked entry points that complement the auto-triggered skill.

## Methodology references

This plugin encodes practices from:

- Barbara Minto, *The Pyramid Principle*
- Gene Zelazny, *Say It With Charts*
- David McCandless, the McCandless Method (for data-slide narration)
- Standard MBB-firm internal style conventions

## Disclaimer

Not affiliated with, endorsed by, or representative of McKinsey & Company, Bain & Company, or Boston Consulting Group. "MBB" is widely-used industry shorthand for a structural and visual style; this plugin encodes that style, not any firm's proprietary materials.

## License

PolyForm Noncommercial 1.0.0 — same as the parent repository. Free for noncommercial use; commercial use requires a separate license. See the [root LICENSE](../../LICENSE) and the project README for details.
