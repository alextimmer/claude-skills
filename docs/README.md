# docs/ — repo-level documentation

This folder holds documentation **about the repository itself** — anything that is not
part of a specific plugin's user-facing payload.

## Why it can't interfere with plugin deployment

Marketplace installs package only each plugin's own directory (the `source:
./plugins/<name>` path in `.claude-plugin/marketplace.json`). Root-level folders like
`docs/` and `evals/` are never copied into a user's plugin cache and never load into
anyone's Claude context. They are visible on GitHub (committed and public) — that is
the intended difference from gitignored maintainer material (e.g.
`plugins/claude-memory-harness/research/`, which never publishes at all).

## What belongs here

- Repo-wide guides and conventions (release process, plugin authoring notes)
- Images and other assets referenced by the top-level README (e.g. the hero banner)
- Anything cross-plugin that users should be able to read on GitHub

## What does NOT belong here

- Plugin-specific docs → the plugin's own folder (`plugins/<name>/README.md`, etc.)
- Skill trigger evals → `evals/<skill-name>/`
- Private maintainer research → a gitignored folder inside the plugin it concerns
