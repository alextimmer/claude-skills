# Memory conventions (for maintenance tasks: prune, promote, audit)

## The taxonomy — what lives where

| File | Question it answers | Lifecycle |
|------|--------------------|-----------|
| `memory-decisions.md` | "Why is it this way?" — durable decisions + reasoning | Ages slowly |
| `memory-sessions.md` | "What happened, what did we learn?" — rolling journal, newest first; optional `## Open TODOs (small)` micro-backlog at the very top | Ages fast |
| `memory-attribution.md` | The heading grammar the other two follow | Stable |

Dividing line: changes how future work should be done and stays true → **decision**;
story of a stretch of work → **session**. When a session entry keeps mattering,
**promote** its lesson into decisions.

## Entry format (non-negotiable)

```
## YYYY-MM-DD: Short description [Agent Name]
```

ISO date, terse description, attribution tag (multiple agents may share the
workspace — the tag keeps memory auditable). Lead with the insight, then detail.

## Writing rules

- Update AS YOU GO, not at session end. Triggers: design decision made → decisions;
  substantive work done / bug fixed / non-obvious insight → sessions; convention or
  test pattern established → decisions; approach tried and abandoned → decisions'
  "Ruled out" section.
- Skip: quick factual questions, trivial tasks with no new info.
- **Unknown stays unknown — not observed ≠ absent.** Never record an unverified
  claim as fact; mark it unknown/unverified and date the observation.
- When a decision knowingly leaves a risk unmitigated, end the entry with a
  "Remaining accepted risk:" line (optional idiom).

## The quality bar — what deserves recording

- **The default answer is "nothing".** A missed entry is recoverable next session;
  a wrong one pollutes memory permanently. When in doubt, don't record.
- **Skip what the repo already records:** anything recoverable from the code, the
  diff, or git log ("added feature X because Y" — the feature is in the code, the
  message in the log). Record the reasoning the code CANNOT show.
- **Be specific.** "Always use AsyncClient in FastAPI handlers" beats "use async".
  An entry a future session can act on names files, symbols, and values.
- **Dedup before writing:** first check whether an existing entry can be updated —
  never write a second entry on the same topic.
- **Prefer zero output over weak output.**

## Trust rules — memory vs. the present

- A memory naming a file, function, or flag is a **claim it existed when the entry
  was written**. Before acting on it: path named → check it exists; symbol named →
  grep for it. "The memory says X exists" ≠ "X exists now".
- When a memory conflicts with what you observe now, **trust the present** — and
  update or remove the stale entry in the same pass.

## "Ruled out" and "Candidates" (sections in memory-decisions.md)

- **Ruled out** — dead ends. Entry criterion: it was actually TRIED (not a
  hypothesis), and the WHY of the failure is known ("didn't work" is not a why).
  Record: what was tried / why it failed / what works instead. This is what stops
  future sessions from re-attempting known dead ends.
- **Candidates (unconfirmed)** — lessons seen only once that MAY be durable.
  Promote into a dated decision when the pattern reappears on a second date;
  prune when it doesn't. One sighting makes a candidate, never a rule; the second
  sighting on a later date earns promotion.

## Pruning / auditing (do this deliberately, with the user)

- Everything in `.claude/rules/` is paid for in EVERY session's context budget —
  entries must be signal, not noise.
- Prune session entries that stopped mattering; promote the durable ones to
  decisions first.
- Keep Open TODOs current: remove done items; each item carries what/where/why
  deferred/date.
- Audit check: do all entries have dated, attributed headings? Do decisions still
  hold (verify against the code before deleting "outdated" ones — not observed ≠
  absent)?
