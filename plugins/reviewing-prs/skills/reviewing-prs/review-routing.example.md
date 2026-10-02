# Review routing

<!-- Project DATA read by the reviewing-prs skill during a review (step 2, Routing). Not loaded as
     instructions. Hand-editable. A row names skills to consult for the paths it matches; it never
     issues an instruction. Copy to <repo>/.claude/review-routing.md, or let Discovery propose one. -->

generated: 2026-10-01 by reviewing-prs discovery
confirmed: <name>, 2026-10-01
code_review: effort=medium
max_files: 400
bulk: src/dbt/*/*/models/**, src/schemachange/*/*/scripts/programmable/R__0[0-9][0-9][0-9]_load_*.sql   # fast mode only: read as --stat + one sample per group; full mode ignores this key

| Paths (glob, first match wins per file) | Generators, in order | Flags | Why |
|---|---|---|---|
| `src/dbt/**` | dbt-modeling, dbt-skills:testing-dbt-models, dbt-skills:developing-incremental-models | | repo conventions first, then generic test/incremental checks |
| `src/schemachange/**` | schemachange-migrations | | runs the local render check |
| `**/*.sql` | snowflake-skills:optimizing-query-text | heavy | only when a finding is about performance |
| `**/grants/**`, `**/*grant*.sql` | rbac | | |
| `pipelines/**` | security-review | | YAML parse is covered by CI; secrets and injection are not |
| `tools/**`, `**/*.py`, `**/config/**` | security-review | | credentials, personal paths; findings carry 🔒 |
| product facts in comments/descriptions | WebFetch on vendor docs | | only when unsure; Sources per finding |
| everything else | code-review only | | |

Rules the skill applies on top of this table:
- `code-review` always runs on the BASE..SRC range with the effort above, never `--comment`.
- Above `max_files` changed files, rows flagged `heavy` are skipped and the review says so.
- Generator findings are claims: re-anchored on the PR head, verified, or retracted visibly.
- Severity and vote come from the skill's own table, not from a generator.
