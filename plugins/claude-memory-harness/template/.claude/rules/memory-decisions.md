<!--
=============================================================================
 memory-decisions.md  —  DURABLE architecture & design decisions
=============================================================================
 PURPOSE
   Long-lived decisions and the REASONING behind them: pattern choices,
   dependency choices, conventions, hard constraints. This is what a new
   engineer (or agent) should read before touching the codebase. Entries
   here age SLOWLY — consult this file first before any design change.

 WHEN TO WRITE HERE
   - A design/architecture decision is made
   - A convention or test pattern is established
   - A non-obvious constraint is discovered that will shape future work

 FORMAT (see memory-attribution.md)
   ## YYYY-MM-DD: Short description [Agent Name]
   Lead with the INSIGHT, then the supporting detail. Prose + tables both fine.

 DIVIDING LINE vs memory-sessions.md
   If it changes how future work should be done and stays true for a long
   time  -> it belongs HERE.
   If it's the story of one stretch of work -> it belongs in sessions.
=============================================================================
-->

# Past Decisions

## YYYY-MM-DD: <Example — delete once you have real entries> [Agent Name]

- **Decision:** <what was decided, e.g. "Use Repository pattern for data access">
- **Why:** <the reasoning and the alternatives rejected>
- **Consequence / rule going forward:** <what future work must respect>

## Ruled out

<!-- Dead ends — approaches that were actually TRIED and failed (hypotheses don't
     qualify). Entry: what was tried / WHY it failed (not "didn't work") / what
     works instead. Same dated, attributed headings as everywhere else. -->

## Candidates (unconfirmed)

<!-- Lessons seen only ONCE that may be durable. Promote into a dated decision
     above when the pattern reappears on a second date; prune when it doesn't.
     One sighting makes a candidate, never a rule; the second sighting on a
     later date earns promotion. -->
