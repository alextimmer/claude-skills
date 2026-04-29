# evals

Maintainer evals for skills in this repo. **This folder is for the repo author, not for end users** — it's not bundled into any plugin install.

## Layout

Each skill gets its own subfolder, named after the skill (not the plugin):

```
evals/
└── mbb-deck/
    ├── README.md
    └── test_prompts.json
```

Each subfolder typically contains:

- `test_prompts.json` — prompts that should and should not trigger the skill, with rationale
- `README.md` — how to interpret and run them

## How to add evals for a new skill

1. Create `evals/<skill-name>/`
2. Copy the `mbb-deck/` README and `test_prompts.json` as a template
3. Replace the prompts and the `skill` field with your new skill's name
4. Tune the trigger / no-trigger lists based on what you want the skill to fire on

## Why per-skill folders?

When you add a second or third plugin to this monorepo, each skill needs its own trigger-accuracy tests. Namespacing by skill name (not plugin name — a plugin can have multiple skills) keeps things clean.
