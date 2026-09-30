<!--
=============================================================================
 memory-sessions.md  —  ROLLING log of work, newest at top
=============================================================================
 PURPOSE
   A reverse-chronological journal. Each entry is a session or a chunk of
   substantive work: what was done, what bug was fixed, what surprised us,
   what to do next. This is the file you skim to answer "where did I leave
   off?" Entries here age FAST — old ones can be pruned, or their durable
   lessons PROMOTED into memory-decisions.md.

 WHEN TO WRITE HERE
   - You complete substantive work
   - You fix a bug
   - You discover a non-obvious insight
   Skip: quick factual questions, trivial tasks with no new info.

 FORMAT (see memory-attribution.md)
   ## YYYY-MM-DD: Short description [Agent Name]
   Lead with the load-bearing insight, then detail: commands, dead ends,
   gotchas, "next steps".

 TIP
   Keep a "RESUME HERE" pointer at the very top when work is mid-flight, so
   the next session knows exactly where to pick up.
=============================================================================
-->

# Session Log

<!-- OPTIONAL: a standing micro-backlog ABOVE the
     dated entries. For small deferred items that are too minor for a session entry
     and too volatile for memory-decisions.md. Every session sees it first; remove
     items when done; note who deferred it and when. Delete this section if unused. -->
## Open TODOs (small)
- <small deferred item — what, where, why deferred, date deferred>
- Active plan: <plan file path — task N of M> (the implementation plan in flight; delete this line when none is)
- Handoff: <topic> -> <handoff file path, outside .claude/rules> (a topic that outlives this log; details live there, not here)

## YYYY-MM-DD: <Example — delete once you have real entries> [Agent Name]

### What was done
- <bullet summary of the work>

### What was learned / gotchas
- <non-obvious insight the next session should not have to rediscover>

### Next steps (the return point)
- <the ONE next concrete action — if unclear, ask the user one line before closing>
- <uncommitted WIP worth knowing about (from `git status --short`), if any>
- <any drafted-but-unsent prompt or command, saved verbatim, if any>
