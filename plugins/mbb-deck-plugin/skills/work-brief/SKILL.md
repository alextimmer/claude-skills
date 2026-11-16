---
name: work-brief
description: Use this skill to write or review a brief for someone who will do the work - an AI tool, a colleague, an analyst, an agency or a contractor - so that what comes back is a recommendation in the right shape and not a summary of the files. Trigger on "write a brief", "brief my team", "briefing for the agency", "write a prompt for", "how do I brief", "delegate this", "hand this over", "instructions for the analyst", or when a user is about to ask someone else (or another AI) to produce a deck, memo, summary or analysis. Also use it to check an existing brief or prompt before it is sent. Do not trigger when the user wants the document itself written (use executive-storyline or mbb-deck), or for an informational briefing note to an executive (that is an executive summary: use executive-storyline).
---

# Work Brief Skill

Write the brief that gets good work back. A drafter, human or AI, is only as good as the brief. A brief without audience, key message and structure produces a tidy summary of the source material. A brief with them produces a recommendation.

The skill has two modes:

- **Write** - turn what the user knows into a brief the recipient can act on without a follow-up call.
- **Check** - review an existing brief or prompt and say what the recipient will have to guess.

## Ground rules

- **Three inputs are the user's to give:** who it is for, what the reader should do afterwards, and the key message. Ask for them. Do not fill them in.
- **Never invent facts, figures or sources.** A brief passes on what is known and names what is not.
- **Say what is decided and what is open.** The recipient must know where their judgment is wanted and where it is not.
- **Write it for the recipient, not for the file.** They have none of the context in the user's head.

## The five parts of every brief

| # | Part | What it settles | Example |
|---|---|---|---|
| 1 | **Role and audience** | Who writes, for whom, and what that reader knows and cares about | "You are a finance manager writing for the executive committee. They know the project; the CFO's concern is the budget." |
| 2 | **Objective** | What the reader should do after reading | "Approval of two decisions in the meeting on 12 May." |
| 3 | **Key message** | The governing thought, in one sentence | "Tender the logistics contract now; it saves cost without lowering the service level." |
| 4 | **Structure** | The shape of the result | "Opening in two sentences, one bullet per argument, then the decisions. One page." |
| 5 | **Facts and limits** | What to use, what not to do | "Use only the two attached files. Savings are stated against the approved budget. Do not invent numbers; list every figure you could not find." |

The user defines parts 1 to 3. Parts 4 and 5 you can propose.

If the user cannot state the key message yet, the work is not ready to be delegated as drafting. Say so, and offer the alternative brief: an *analysis* brief, whose objective is to find the answer, with the question in place of the key message.

## What a complete brief adds

The five parts are the core. A brief for real work also needs:

- **Deliverable** - format, length, language, template, file type.
- **Deadline and checkpoints** - when the result is due, and whether an outline or storyline should come back first for alignment. For anything longer than a page, ask for the storyline before the full draft.
- **What good looks like** - the two or three properties the result will be judged on.
- **Decided and open** - what is fixed and must not be reopened; where the recipient's own judgment is wanted.
- **Reference for figures** - what numbers are stated against (budget, prior year, a benchmark), in the reader's own terms.
- **What stays with the sender** - the key message, the reference for the figures, and the final check of every number are never delegated.

## Write: the steps

1. **Collect the three user inputs.** Audience, objective, key message. One question, only for what is missing.
2. **Choose the kind of brief.** Drafting (the answer is known, the document is wanted) or analysis (the answer is wanted). Say which.
3. **Fill the five parts**, then the additions that apply. Leave out what does not.
4. **Fit it to the recipient** (below).
5. **Read it as the recipient.** What would they have to guess? Each guess is a gap: close it or mark it as open on purpose.
6. **Hand it over** with the gaps listed: what the user still has to supply before sending.

## Fit it to the recipient

| Recipient | What changes |
|---|---|
| **AI tool** | State the role in the first line. Give the structure explicitly, with limits on length. Name the sources and forbid others. Add the two standing instructions: do not invent numbers; list every figure you could not find. Say what to return first (a storyline) if the task is large. |
| **Colleague or analyst** | Give the reason behind the task, so they can make the calls the brief did not foresee. Name the decided and the open. Agree the first checkpoint. |
| **Agency or contractor** | Add scope, what is out of scope, the approval path, the single contact, and what happens to the material afterwards. Be exact about format and deadline. |

Templates for each are in `references/templates.md`. A worked example is in `examples/brief-for-a-summary.md`.

## Check: reviewing an existing brief

Read the brief as the recipient and report:

1. **The five parts** - present, vague, or missing. Quote the vague ones.
2. **The guesses** - everything the recipient would have to assume, in order of how badly a wrong guess would hurt.
3. **What it will produce as written** - one honest sentence. Usually: "a summary of the material", "a draft for the wrong reader", or "a result that cannot be checked".
4. **The repaired brief** - with named gaps where only the user has the answer.

The common defects:

| Defect | What comes back |
|---|---|
| No audience | A text for nobody in particular, at the wrong level of detail |
| No objective | Information without an ask |
| No key message | A summary of the files instead of a recommendation |
| No structure | The order in which the material was found |
| No sources or limits | Plausible numbers nobody can trace |
| No reference for figures | Savings against a baseline the reader does not use |
| No checkpoint | A finished draft built on a misunderstanding |
| Everything open | The recipient decides what the sender should have decided |

## Language

Plain and specific. Imperatives for what must happen, reasons where judgment is needed. No stock words (leverage, robust, comprehensive), no "please ensure a high-quality result": say what quality means here.

## Relation to the other skills

`executive-storyline` and `mbb-deck` write the document. This skill writes the instruction for someone else to write it. It stands alone and needs no tooling; produce the brief in whatever form the environment and the recipient use.

## Reference files

- `references/templates.md` - the brief as a fill-in template for an AI tool, a colleague, and an agency; the analysis-brief variant
- `examples/brief-for-a-summary.md` - a weak prompt, what it would produce, and the repaired brief
