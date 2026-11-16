# mbb-deck-plugin

Build presentations in the structural style of top-tier management consulting firms (McKinsey, Bain, BCG). Enforces the Pyramid Principle, action titles, MECE structure, and minimal executive-grade visuals. A second skill, `executive-storyline`, applies the same storyline method to executive summaries, memos, pre-reads, emails to leadership and spoken updates. A third, `work-brief`, writes the brief for someone else who will do the work.

This plugin is part of the [`claude-skills`](../../) marketplace.

## What's inside

```
mbb-deck-plugin/
├── .claude-plugin/
│   └── plugin.json                    ← plugin manifest
├── agents/                            ← Claude Code subagents
│   ├── storyline-reviewer.md          ← critiques storylines (deck, memo, summary) against the document type
│   └── qa-reviewer.md                 ← runs production QA on finished decks
├── commands/                          ← Claude Code slash commands
│   ├── storyline.md                   ← /storyline — audience, governing thought, SCQA, action titles, decision needs
│   ├── critique-deck.md               ← /critique-deck <path> — MBB-style review of an existing pptx
│   └── exec-summary.md                ← /exec-summary <path> — the email or one-pager that travels with a deck
└── skills/
    ├── mbb-deck/                      ← the deck skill — what Claude reads at runtime
    │   ├── SKILL.md                   ← entrypoint
    │   ├── references/                ← deeper docs Claude pulls in on demand
    │   ├── examples/                  ← worked storyline examples (md + json)
    │   ├── scripts/                   ← build_deck.py, validate_storyline.py, lint_deck.py
    │   └── assets/                    ← palettes, schema, icons, example deck
    ├── executive-storyline/           ← the storyline skill for anything that is not a slide
    │   ├── SKILL.md                   ← create / condense / feedback
    │   ├── references/                ← method, executive summaries, feedback
    │   ├── examples/                  ← deck condensed into an email; weak vs. strong answer
    │   └── scripts/                   ← lint_prose.py
    └── work-brief/                    ← the brief for an AI tool, a colleague or an agency
        ├── SKILL.md                   ← write / check
        ├── references/                ← templates per recipient, analysis-brief variant
        └── examples/                  ← a one-line prompt repaired into a brief
```

## Install in Claude Code

```bash
/plugin marketplace add YOUR_USERNAME/claude-skills
/plugin install mbb-deck-plugin@claude-skills
```

Then ask Claude something like:

> Build me an MBB-style deck recommending whether we should expand to Germany.

or

> Write the email to the board that goes with this deck.

The matching skill triggers automatically.

## Use just the skill in Claude.ai

Zip an inner skill folder and upload it via Customize → Skills → Upload:

```bash
cd skills
zip -r mbb-deck.zip mbb-deck/
zip -r executive-storyline.zip executive-storyline/
zip -r work-brief.zip work-brief/
```

Each skill works on its own. Upload both if you want decks and the summaries that travel with them.

Note: Claude.ai uploads do NOT include the slash commands or subagents in this plugin — those are Claude Code features. If you need just the methodology and the build script, the skill folder alone is enough.

## Where it runs

- **Claude Code** — everything: both skills, the three commands, the subagents, the validation hook, and the bundled Python tools.
- **claude.ai and agent environments such as Claude Cowork** — the skills carry the method and need no tooling. The deck skill leaves rendering to the environment: where the host has its own way to make presentations, it uses that, in your template where you have one, and does not route the deck through the bundled scripts. Subagents and slash commands are Claude Code features; without them the skill runs the same checks inline. (Verified in Claude Code only; the behavior elsewhere follows from the skill text and has not been tested there.)

The storyline JSON, `build_deck.py` and the Marp guide are for decks made in other tooling — Claude Code, CI, version-controlled markdown decks.

## Workflow at a glance

1. User asks for a strategy/consulting deck → `mbb-deck` skill activates
2. Claude works through the storyline first (audience and document type → governing thought → SCQA → action titles → decision needs), gets approval
3. (Optional) Hand the storyline to `storyline-reviewer` subagent for an isolated critique
4. Claude builds the slide content — as a structured JSON storyline matching `assets/storyline_schema.json` when the bundled tools will render it, or in whatever form the environment's own slide capability takes
5. `scripts/validate_storyline.py` checks for topic and process titles, missing fields, executive-summary figures no page backs up, and a senior document that ends without decision needs
6. The deck is rendered: by the environment's own presentation capability where there is one, otherwise as a Markdown outline, Marp markdown, or a styled `.pptx` from `scripts/build_deck.py`
7. (Optional) Hand the finished deck to `qa-reviewer` subagent for production polish check
8. (Optional) `/exec-summary` condenses the finished deck into the email or one-pager that goes out with it

For a memo, a pre-read, an email to leadership or a spoken update, the `executive-storyline` skill runs the same storyline steps and writes the asset in the form that channel needs.

The three slash commands (`/storyline`, `/critique-deck`, `/exec-summary`) are user-invoked entry points that complement the auto-triggered skills.

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
