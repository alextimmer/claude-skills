# Storyline Construction

This reference covers the structural backbone of an MBB-style deck: the Pyramid Principle, SCQA, the governing thought, MECE, the step from data to "so what", numbers and claims, and the decision-needs close.

> **Terms:** *governing thought* and *key message* mean the same thing — the single statement the audience must take away. This skill uses *governing thought*. Below it sit the *arguments*; below each argument, its *evidence*.

## The Pyramid Principle (Minto)

Originally developed by Barbara Minto at McKinsey. The structure:

```
                  Governing Thought
                  (one sentence answer)
                          |
        ____________________________________
       |              |              |
   Argument 1    Argument 2     Argument 3
       |              |              |
   Evidence       Evidence        Evidence
```

Work runs bottom-up (gather data, analyze, conclude). Communication runs top-down (conclusion, then support). **Never present in the order you worked.** The pyramid is the direct outline of the deck: governing thought and a summary of the arguments up front, then one section per argument with its evidence.

Three rules:
1. **Ideas at any level summarize the ideas grouped below them.** The governing thought is the summary of the arguments; each argument is the summary of its evidence.
2. **Ideas in a group must be the same kind of idea, on the same logical level.** Don't mix "reasons we should do X" with "risks of doing X" in the same group, and don't introduce a piece of evidence for an earlier argument as if it were a new argument — fold it under the argument it supports.
3. **Ideas in a group must be logically ordered — and you must be able to name the order.** Temporal (oldest to newest or the reverse), importance (most to least), causal (cause to effect), or structural (geography, function, abstract to tangible).

**Grouping:** three elements per level is often ideal; more than five is too many. Group related arguments into argument groups instead of listing them flat. If you are short of three, consider what can almost always be added: risks, caveats, next steps, milestones.

**Overview and double-click:** the executive summary is the overview — the governing thought with one row per argument. Every section that follows is a double-click on one row: same order, same wording, same numbers. See "Structuring techniques" in `references/slide-patterns.md`.

## Before the pyramid: audience and objective

A storyline is written for the person who has to act, so settle three things first:

- **Who decides and who influences,** and what they know, think and prefer (facts or concepts, short or long).
- **The commitment ladder:** where each person stands (unaware → aware → understands → buys in → acts), where they must be after this deck, and what one meeting can realistically achieve.
- **Each decision maker's main concern.** A strong storyline answers it on the page before it is raised.

A structure that mirrors the team's workstreams instead of the audience's decision is written for the writer. Restart from audience and objective.

**Free text or structured?** For most decks, one line in `meta.audience` is enough. Offer the structured form (`meta.stakeholders`: name, role, current and target stage on the ladder, main concern) only when it pays off — a decision document with two or more decision makers who stand in different places, or a contested message. Then each recorded main concern should be answered on a page: by a **callout** on the page it belongs to, or by a **safeguard** on the decisions slide. The validator notes when concerns are recorded and nothing answers them.

**Pre-alignment.** Once the storyline is approved and the concerns are known, tell the user who to speak to one-to-one before the meeting and about what. This is advice for the conversation, not a slide; put it in the appendix only if asked.

## SCQA — drafting the introduction

Before the pyramid, frame the problem so the audience knows why they're being asked the question.

- **Situation** — Stable, accepted facts. The audience should nod. ("Acme has been the category leader for ten years.")
- **Complication** — What makes the situation worth attention now. ("Three new entrants have captured 22% share in 18 months.")
- **Question** — The question this raises. ("How should Acme respond?") The deck may leave it unstated, but write it down in the working storyline: the governing thought must answer exactly this question.
- **Answer** — The governing thought. ("Acme should reposition around premium segments and divest the value tier within 12 months.")

The Answer is the top of the pyramid. Everything that follows in the deck supports it.

> **Alias:** some firms teach this as **SCR** (Situation–Complication–Resolution) — the same framework with the Question folded into the Complication. If the user says SCR, it maps 1:1 onto SCQA.

**A complication is not necessarily a problem.** Six framings, each with its natural question:

| The complication is that... | The question becomes |
|---|---|
| something went wrong | What do we do? |
| something could go wrong | How do we prevent it? |
| something changed | What should we do? |
| something could change | How should we react? |
| there are different points of view | Who is right? |
| there are several alternatives | Which one do we take? |

**How much opening?** Top-down is the default: busy readers who know the context want the answer first. The standard deck spends roughly 10–20% on situation, complication and answer, and the remaining 80–90% on the arguments and their evidence. Give the opening more room only when the audience is new to the topic or the message is controversial and the audience must be brought along.

## From data to "so what"

Every finding can be stated on four levels. Each answers a different question:

| Level | Question it answers | Example |
|---|---|---|
| 1. Data | What are the numbers? | "Enterprise deals were 12% of new bookings last year." |
| 2. Summary | What happened? | "Enterprise bookings tripled in two years while mid-market stayed flat." |
| 3. Insight | Why does it matter? | "Enterprise now drives all of our growth, but the sales team is staffed for mid-market." |
| 4. So what | What should the reader do? | "Move a third of the mid-market quota capacity to enterprise next year." |

Most drafts stop at data or summary and leave the rest to the reader. Governing thoughts and action titles belong on levels 3 and 4.

The right "so what" depends on the reader: the same data leads to different implications for Finance, Operations or Marketing. Write it for the person who has to act.

## Content beats process

Every statement is a governing thought, a content detail (a supporting fact or argument), or process (a report of activity: "we talked to Finance", "we created a draft"). A deck is made of the first two. Process appears at most once, at the end, as the next step. A storyline dominated by process statements has no message.

## Action-title writing rules (beyond "complete sentence")

- **State the So What, not just the facts.** "We win 40% of negotiations" is a fact; "Negotiation conversion declined from 55% to 40%, likely driven by recent scaling of the sales team" is an insight.
- **Present tense, active verbs.** "Price drives growth" beats "growth was driven by price".
- **Avoid general truths** that are always correct ("managing risk is important for success" says nothing).
- **Avoid absolute statements** without room for outliers ("all divisions fail to follow best practices").
- **Quantify whenever possible** — numbers make titles credible and precise.
- **Results, not process.** Never "we conducted analyses and learned a lot"; always what was learned.

**The improvement ladder** (worst → best):
1. A topic label — "Market dynamics"
2. A generic claim — "Focus on expansion to attractive geographies"
3. A specific but wordy sentence
4. A concise, quantified insight — "Asia Pacific and North America prioritized due to margins, growth and 100+ EUR mn market size"

Climb every title to rung 4 before slide content is built.

## The governing thought

A single sentence, ideally under 25 words, that:

- States a recommendation, conclusion, or insight (not a topic)
- Is specific enough to be falsifiable
- Implies action or decision
- Answers the question from the SCQA

If it cannot be stated in one sentence, the thinking is not done.

**Bad governing thoughts:**
- "We should think about international expansion." (Vague; not falsifiable)
- "Our growth strategy." (Topic, not a thought)
- "Customers want more features." (Insight, but no implication for action)

**Good governing thoughts:**
- "Acme should enter Germany and France in 2026 via direct sales, funded by exiting the SMB tier."
- "The decline in Q3 margin is caused by raw material costs, not pricing — we should hedge, not raise prices."
- "We can hit our 2027 EBITDA target by capturing three identified cost-out opportunities worth $42M."

**Four tests:**
- **Goal** — what is this work for?
- **CEO test** — what should senior management do differently after hearing it?
- **Relevance** — would the story suffer if this point were missing?
- **Insight** — is it merely interesting, or does it change a decision?

## MECE — Mutually Exclusive, Collectively Exhaustive

Top-down says what comes first; MECE makes sure the structure below it holds. Every breakdown in the deck must be MECE.

- **Mutually Exclusive** — categories don't overlap. A customer is in exactly one segment. Overlaps usually appear when one level mixes two dimensions (sections by product next to a section by region).
- **Collectively Exhaustive** — categories cover the entire space. No "other" bucket that's secretly large, no obvious member of the dimension missing.
- **The test:** for each level, name the one dimension it uses (by product, by region, by driver, by phase) and check that every element follows it and all members are covered.

Common MECE breakdowns:
- By geography (regions that don't overlap and cover the whole market)
- By customer type (SMB / Mid-Market / Enterprise — pick a clear cutoff)
- By function (Sales / Marketing / Product / Ops)
- By time period (FY24 / FY25 / FY26)
- By driver (Volume × Price × Mix for revenue change)
- By 2x2 axis (e.g., growth vs. margin)

When something doesn't fit MECE, redesign the framework rather than forcing the data — the framework is wrong, not the data.

## Numbers and claims

- **Define every target and figure:** what is measured, against which baseline, for which period, by when. "$14M of annual cost-to-serve savings from FY27 against the FY26 budget", not "$14M of efficiency".
- **Use the reader's baseline and terms.** Finance tracks savings against the budget, not against a do-nothing case. A figure the decision maker cannot find in their own numbers costs credibility.
- **Attribute every effect to the right lever.** If two measures produce the result together, say so instead of crediting one.
- **Claim only what the evidence proves.** If one of four criteria points the other way, write "on three of four criteria".
- **Keep numbers identical everywhere** — executive summary, pages, appendix. Separate components explicitly ("$26M of net new ARR plus $14M of cost savings") instead of merging different measures into one headline number.
- **Name what changes when.** For transitions, state from which date the new targets apply and who delivers until then.

### Recording the headline figures (`meta.key_figures`, optional)

The rules above are easy to state and hard to hold across fifteen pages. When the governing thought or a decision rests on a number, or the audience has met the figure before in another form, record each headline figure once and let every page follow that record:

| Field | What it fixes | Example |
|---|---|---|
| `value` | The figure exactly as written on the pages | `$14M` |
| `measure` | What is measured | fully loaded cost to serve the SMB tier |
| `reference` | What it is stated against | a baseline (budget, prior year, do-nothing case), a benchmark (peer average), a target, or `absolute` for a plain level |
| `period` | The period it covers | per year, FY24 |
| `by_when` | For targets, when it is reached | end-2027 |
| `lever` | What produces the effect | all levers, if several act together |
| `status` | How firm it is | actual, estimate, preliminary |
| `components` | The parts, when the figure is a sum | they add up to `value` and share its measure |

*Reference* is deliberately wider than *baseline*: a saving is stated against a budget, a growth rate against a prior period, a market share against competitors, a cost against nothing at all. Choose the reference the reader uses themselves.

The validator checks three things: every recorded figure is fully defined, appears on a page in identical form, and reconciles with its components. Whether the reference is the right one for this reader remains a judgment — the reviewer's and the user's.

This is a first, deliberately small model. It does not yet relate figures to each other (a rate and the level it applies to), carry ranges or scenarios, or check units across pages.

## Closing on decision needs

A senior deck ends by saying what is asked of the reader — the `decisions` slide (Pattern 10 in `references/slide-patterns.md`) — not on a data page and not on "let's discuss".

- **Which decisions:** each a sentence that can be approved or rejected.
- **By when, and why now:** the date and the event that forces it.
- **Safeguard and owner:** each decision paired with the answer to the main concern behind it, and with who carries it.
- **Concerns that belong to a page:** answer them there, in a `callout` — one or two lines in an outlined box above the footer ("Why this differs from the March figure: ...").
- **Next steps:** task, owner, date.

The executive summary asks for the decisions; the last page repeats them, in the same words.

**Decision pre-reads** (`document_type: decision_pre_read`) work without a presenter: cover, one-page executive summary, up to four supporting pages. Refer to pages by name ("the savings page") — record the name in the slide's `name` field; it is metadata for the summary, the email and the conversation and is never printed on the slide. Answer each stakeholder's main concern on the page — for example a small box explaining why the savings differ from a figure quoted earlier. Test the storyline in one-to-one conversations before the meeting: a concern raised in a one-to-one can be solved, a concern raised in the meeting gets defended.

## Calibrate to the document type

| `document_type` | Storyline bar |
|---|---|
| `team_alignment` | Thoughts on paper, concisely. No polish or elaborate storyline. |
| `recurring_update` | Consistent structure and clean pages; beautification does not matter. |
| `board` | Clear storyline, few words, details in the appendix. Executive summary, decision needs, next steps. Stands alone. |
| `decision_pre_read` | As `board`, in cover + executive summary + up to four pages. |
| `external` | Board-level rigor plus legal and PR review. |
| `documentation` | May be wordy; must stand fully on its own. |
| `keynote` | Few, memorable messages and visual slides; the presenter provides the soundtrack. |

When reviewing, establish the type first and judge against that bar.

## Test your storyline

Before approving a storyline, run these checks:

1. **The action-title test.** Read only the slide titles top-to-bottom. Do they tell the whole story without the bodies? Where does the thread break?
2. **The "so what" test.** For every slide, ask "so what?" The next slide's title should answer it.
3. **The pyramid test.** Do the supporting arguments, taken together, prove the governing thought? If even one is removed, does the argument weaken?
4. **The MECE test.** Name the dimension of each level. Are the arguments mutually exclusive and collectively exhaustive along it?
5. **The content/process scan.** Classify each title as governing thought, content or process. Flag every process statement that is not a next step.
6. **The insight check.** Which of the four levels does each title reach? Is the governing thought a recommendation or a summary of findings?
7. **The count and order check.** How many arguments per level, and which order is used? Name it or fix it.
8. **The number check.** Is every figure defined (basis, period, baseline) and identical wherever it appears?
9. **The close.** Does the deck end on decision needs and next steps?

## Common weaknesses

| Weakness | Fix |
|---|---|
| Work-order narrative: the deck retells the project chronologically | Invert into pyramid order |
| Buried governing thought: the recommendation appears on the last page | State it up front; let the deck substantiate it |
| Summary sold as insight: organized facts without an implication | Force the so what and the CEO test |
| Process padding: activities presented as content | Cut, or convert into one next-steps line |
| Argument sprawl: six or more parallel arguments | Group into three |
| Mixed logical levels: evidence presented as a new argument | Fold it under the argument it supports |
| Overlaps and gaps: a level mixes two dimensions or misses a member | One dimension per level, all members covered |
| Missing or artificial complication: no reason why this matters now | Add a real complication with its question |
| Wrong baseline: impact against a reference the decision maker does not use | Restate against their baseline; explain the difference |
| Missing decision needs: the deck ends without an ask | A decisions slide: which, by when, why now |
| Executive summary drift: the summary tells another story or its numbers differ | Rebuild it from the action titles |
| Written for the writer: structure mirrors the team's workstreams | Restart from audience and objective |
| Generic text: smooth sentences that say nothing specific | Replace each with the concrete point, number or decision |
