# Example: from a one-line prompt to a brief

A project lead wants an AI tool to draft the executive summary for a steering committee.

## The brief as first written

> Summarize the attached project documents for the steering committee.

## Check

**The five parts**

| Part | Status |
|---|---|
| Role and audience | Vague: "the steering committee", with nothing on what they know or worry about |
| Objective | Missing |
| Key message | Missing |
| Structure | Missing |
| Facts and limits | Partly: "the attached documents", no rule on figures |

**What the recipient has to guess**

1. What the committee is supposed to do: note the status, or decide something.
2. What the project lead wants to tell them.
3. How long the result may be and in what form.
4. Whether a figure may be estimated when the documents do not give it.
5. What savings are measured against.

**What it will produce as written:** a neutral summary of the documents in the order they were attached, at whatever length the tool chooses, with no recommendation and no ask.

## The repaired brief

Gaps only the project lead can fill are in square brackets.

> You are the project lead for the logistics tender, writing for the steering committee. The members know the project. The CFO's main concern is whether the savings will show up against this year's budget.
>
> Objective: the committee approves two decisions in its meeting on [date].
>
> Key message: [one sentence, for example: tender the outbound logistics contract now, because it lowers cost without lowering the service level].
>
> Structure:
> - Opening: situation and complication in two sentences.
> - The recommendation in one sentence, in bold.
> - One bullet per argument, three at most, each opening with a bold lead and carrying its key number.
> - A box with the two decisions, the deadline, and why they are needed now.
> One page. Bullets, no running prose.
>
> Facts and limits:
> - Use only the two attached files. Do not use other knowledge for facts or figures.
> - State savings against the approved budget for [year], not against a do-nothing case.
> - Do not invent numbers. List every figure you needed and could not find.
> - Fixed: the key message and the two decisions as named in the tender memo.
> - Open: the wording and the order of the arguments.
>
> First return the storyline as bullets with one sub-level. Wait for my confirmation before writing the page.

## What changed

- **The reader has a face and a concern.** The draft can now answer the CFO's question before it is asked.
- **There is an ask.** "Approves two decisions" turns a status report into a decision page.
- **The key message is the sender's.** It is left as a gap because only the project lead can state it.
- **The shape is fixed.** One page, three arguments, a decisions box.
- **Figures can be traced.** One source, one reference, and a list of what could not be found.
- **There is a checkpoint.** A wrong storyline costs minutes instead of a full draft.

Three things stay with the project lead whatever comes back: the key message, the reference for the figures, and the final check of every number.
