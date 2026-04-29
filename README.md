# Claude Skills

A collection of Claude skills, plugins, and subagents I've built for my own use and shared publicly.

## What's in here

| Plugin                                        | Description                                                                                                                                                                                                                   |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`mbb-deck-plugin`](plugins/mbb-deck-plugin/) | Build presentations in MBB / management consulting style — Pyramid Principle, action titles, MECE structure. Includes `/storyline` and `/critique-deck` slash commands plus `storyline-reviewer` and `qa-reviewer` subagents. |

More plugins will land in `plugins/` over time. Each one is self-contained.

## Install in Claude Code

Add this whole repository as a marketplace, then install the specific plugin(s) you want:

```bash
# Add the marketplace once
/plugin marketplace add YOUR_USERNAME/claude-skills

# Install whichever plugin(s) you want
/plugin install mbb-deck-plugin@claude-skills
```

Updates flow automatically as you push commits (or bump the `version` field in each plugin's `plugin.json`).

## Use a single skill in Claude.ai

Some plugins also expose a skill folder you can upload directly to Claude.ai (Customize → Skills → Upload). For each plugin, the uploadable skill folder lives at:

```
plugins/<plugin-name>/skills/<skill-name>/
```

Zip *just that folder* (the zip's root must be the skill folder itself, with `SKILL.md` directly inside). Pre-built zips may be attached to the [Releases](https://github.com/YOUR_USERNAME/claude-skills/releases) page.

## Repository structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          ← marketplace catalog (lists every plugin)
├── plugins/
│   └── mbb-deck-plugin/          ← one plugin per folder
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/               ← subagents for this plugin (Claude Code only)
│       ├── commands/             ← slash commands (Claude Code only)
│       └── skills/
│           └── mbb-deck/         ← the actual skill — this is what gets uploaded to Claude.ai
│               ├── SKILL.md
│               ├── assets/
│               ├── examples/
│               ├── references/
│               └── scripts/
├── evals/
│   └── mbb-deck/                 ← maintainer evals for each skill, namespaced by skill name
│       ├── README.md
│       └── test_prompts.json
├── LICENSE
└── README.md
```

## Adding a new plugin to this repo

1. Create `plugins/<new-plugin>/` with `.claude-plugin/plugin.json`, plus any `agents/`, `commands/`, and `skills/<skill>/` folders.
2. Add a new entry to the `plugins` array in `.claude-plugin/marketplace.json`.
3. (Optional) Create `evals/<skill-name>/` for trigger-accuracy tests.
4. Update this README's plugin table.
5. Commit. Users with the marketplace already added will see the new plugin immediately.

## Validating before pushing

From the repo root:

```bash
claude plugin validate .
```

This catches naming errors, JSON parse issues, and frontmatter problems across all plugins.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0).

You can use, modify, and distribute this software for any **noncommercial purpose** — personal use, hobby projects, study, research, education, charitable work, government use. See the `LICENSE` file for the full terms.

**Commercial use requires a separate license.** If you want to use this in a for-profit context (consulting work for paying clients, integration into a commercial product, internal use at a for-profit company beyond evaluation), please open an issue on GitHub to discuss licensing terms.

## Contributing

Issues and PRs welcome. If you have improvements to a specific plugin, please file the issue against the plugin (mention it in the title) so I can route it.
