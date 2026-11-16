---
name: executive-storyline
description: Use this skill to create, condense, or review the storyline of an executive communication in any format - an executive summary, a memo, a steering-committee or board paper, a pre-read for a decision meeting, an email to leadership, or a spoken status update. Also use it to turn an existing deck or report into an executive summary ("write the email that goes with this deck", "summarize this for the CEO"). Trigger on "storyline", "executive summary", "exec summary", "pre-read", "key message", "governing thought", "top-down communication", "answer first", "so what", "decision paper", "board paper", "steering committee paper", "memo to the leadership team", or "how do I present this". Do not trigger for casual emails, meeting minutes, or neutral summaries with no executive reader and no recommendation. For building or reviewing the slides themselves, use the mbb-deck skill; this skill supplies the storyline both share.
---

# Executive Storyline Skill

Develop the storyline of an executive communication before any slide or paragraph is written, and hold drafts to that standard. The method is the same for a deck, a memo, an email and a spoken answer: one governing thought, stated first, supported by a few arguments that do not overlap, each backed by evidence, closing with what is asked of the reader.

## Three modes

- **Create** - develop a storyline from work results, analyses or a briefing.
- **Condense** - derive an executive summary (email, one-pager, spoken update) from an existing deck or document.
- **Feedback** - review a draft storyline, outline, executive summary or answer against the standard.

## Ground rules

- **Never invent numbers, quotes or facts.** Use only what the user provides. If a figure is missing, say so and mark the gap.
- **The governing thought is the user's decision.** Propose options, then get it confirmed before building on it.
- **Storyline before prose.** Deliver the storyline in dot-dash form and get it approved before writing the email, memo or pages.
- **Judge against the document type.** A team-alignment note and a board paper do not share a bar (see below).

## Terms

- **Governing thought** (also: key message) - the one statement the audience must take away, typically a recommendation. There is exactly one.
- **Arguments** - the logical groups of reasons directly below the governing thought.
- **Evidence** - the facts, data and analyses backing each argument.

Keep the terms apart. Evidence presented as if it were a new argument is the most common structural defect.

## The standard in eight lines

1. Governing thought first; never present in the order the work was done.
2. Insight and "so what" over data and summary: say what the reader should do.
3. Content, not process: what the work showed, not what was done.
4. Three arguments is ideal; more than five on one level is too many.
5. One dimension per level, no overlaps, no gaps (MECE).
6. Every figure defined (what, baseline, period, by when) and identical everywhere.
7. Close with the decision needs (which, by when, why now), then next steps.
8. The titles or lead sentences alone tell the complete story.

Full method: `references/method.md`.

## Create: nine steps

1. **Audience and objective.** Who decides, who influences, what do they know and prefer? Where does each stand on the commitment ladder (unaware, aware, understands, buys in, acts), and where must they be afterwards? What is each decision maker's main concern?
2. **The question.** The one question the document answers, in one sentence.
3. **The governing thought.** One sentence at insight or so-what level that answers that question and passes the CEO test (what should senior management do differently after hearing it?). If it cannot be said in one sentence, the thinking is not done. Confirm it with the user.
4. **The structure.** Top-down by default. A short situation-complication lead-in when the audience is new to the topic or the message is controversial.
5. **The argument groups.** Aim for three, MECE. If short of three, consider what can almost always be added: risks, caveats, next steps, milestones.
6. **The order.** Temporal, by importance, causal, or structural. Name the one you use.
7. **Action titles.** One full-sentence message per planned page or section. Read them alone, top to bottom: they must tell the story.
8. **Evidence.** Map each analysis to the argument it supports. Evidence without a home is cut or moves to the appendix.
9. **The close.** Decision needs in a section of their own, then next steps (task, owner, date).

Deliver the result in dot-dash form (`references/method.md` has the format and a worked example), then ask for approval. Only then write the asset.

If the user gestures at a document without giving the five briefing inputs (audience, objective, governing thought, structure, sources and limits), ask for the first three. They are the user's to define.

## Condense: an executive summary from an existing asset

1. Read the whole source. List its action titles (or section headings) in order.
2. Run the titles-only read. If the titles do not tell a story, say so before summarizing: a summary cannot repair a missing storyline, and the user should know.
3. State the governing thought in one sentence and confirm it. Take it from the source; do not improve it silently.
4. Write the summary following the anatomy in `references/executive-summary.md`: context, recommendation, one bullet per section with a bold lead and the key numbers, then the decision needs.
5. Check every number against the source. Same figure, same unit, same baseline. List any figure you could not find.
6. Fit the form to the channel (email, one-pager, spoken): `references/executive-summary.md` has each.
7. Point into the source by page name ("the savings page"), not by number. Use the names the source records; if it has none, name the one or two pages you refer to after their subject.

`examples/summary-from-deck.md` shows a deck condensed into an email.

## Feedback

Establish the document type first. Then run the six tests and deliver the three-part review (verdict, element by element, top three improvements) from `references/feedback.md`. Quote the original wording whenever you propose a rewrite.

## Calibrate to the document type

| Type | Bar |
|---|---|
| Team alignment | Thoughts on paper, concisely. No polish, no elaborate storyline. |
| Recurring update (jour fixe) | Consistent structure and clean pages. No beautification. |
| Board and senior management | Clear storyline, few words, details in the appendix. Executive summary, decision needs, next steps. Stands alone without a presenter. |
| Decision pre-read | Cover, one-page executive summary, up to four supporting pages. Decisions asked in the summary and repeated on the last page. |
| External | Board-level rigor plus legal and PR review. |
| Documentation | May be wordy. Must stand fully on its own. |
| Keynote | Few, memorable messages. The presenter provides the soundtrack. |

## Language

- Plain, concise business English that non-native speakers understand. Every word earns its place.
- Convince stakeholders; do not "win" them.
- No stock words (delve, leverage, comprehensive, compelling, robust, pivotal, seamless, holistic, impactful, unlock), no stock phrases ("it is important to note", "here is why"), no contrast setups ("not X but Y"), no trailing clauses (", ensuring..."), no empty intensifiers (really, truly), no exclamation marks. State the concrete point instead.

`scripts/lint_prose.py` checks a draft for these mechanically, along with process statements and a missing decision ask. It is an optional aid for environments where Python is at hand (standard library only); without it, apply the same rules by reading.

```bash
python scripts/lint_prose.py draft.md            # or: --type email|memo|summary
```

## Working with the mbb-deck skill

When the asset is a slide deck, this skill settles the storyline and `mbb-deck` builds and checks the pages. When a deck already exists and the user needs the email or summary that travels with it, stay here and use Condense.

## Briefing someone else

When the user wants another person or another AI tool to produce the document, the sibling skill `work-brief` writes that brief. The five inputs a drafter needs are listed under "Briefing inputs" in `references/executive-summary.md`.

## Environment

The skill is method and wording; it needs no tooling. Produce the asset with whatever the environment normally uses for documents and email, and in the user's template where there is one. Where the environment has no subagents or slash commands, run the feedback review inline.

## Reference files

- `references/method.md` - pyramid principle, grouping, logic and order, MECE, content versus process, the four levels from data to so what, structure choice, the opening, numbers and claims, dot-dash format
- `references/executive-summary.md` - anatomy and best practices, decision needs, decision pre-reads, forms per channel (email, one-pager, spoken), briefing inputs
- `references/feedback.md` - the three-part review, six tests, thirteen common weaknesses, output template
- `examples/summary-from-deck.md` - a board deck condensed into an email to the board
- `examples/weak-vs-strong.md` - the same status answer, bottom-up and top-down
- `scripts/lint_prose.py` - deterministic check for filler, process statements and a missing ask
