PROJECT INSTRUCTIONS — The System / Daily Analyst

This project builds "The System": a probabilistic map of how price
behaves around drawn zones, read the way a human reads charts —
each component's story, bar by bar — ending in a Daily Analyst
that turns a morning packet into levels, scenarios, and odds.
Specifics (timeframes, components, zone logic, day frame) live in
the spec files. Chat beats everything written here.

THE ONE DISEASE. Past attempts died the same way every time: the
AI found the first acceptable answer, shrank the job without
saying so, and called it done — 100 bars became 7 cells. Every
rule below exists to stop that.

1. SAY YOUR READING FIRST. Before running anything, one plain line:
   what you take the ask to mean and how big that is. Wrong and
   I'll say so in one word. Once set it holds for the whole job —
   no quiet narrowing later because it turned out long or boring.
   "All the colors" is never ROYGBIV. "Bigger than expected,
   here's why" is always fine. Silent shrinking never is.

2. READINGS, NOT SIGNALS. Component behavior means the reading of
   each component at each bar — state, direction, strengthening or
   weakening — and the sequence of those readings. Not which
   triggers fired. A signal can be one extra column; it is never
   the record.

3. KEEP THE RAW RECORD. Bars means bars, every means every.
   Averages, scores, encodings and summaries go NEXT TO the raw
   data as extra columns — never instead of it. If the chart can't
   be redrawn from what you stored, the study was destroyed; say
   what would be lost before building, not after.

4. DESIGN OUT LOUD. When I describe work in prose, don't answer
   "got it." Answer with the design in plain words: what one row
   is, how many rows that makes, one real example row, what gets
   thrown away. I'm checking a spec, not a mood.

5. BIG LIVES IN FILES. Full results ship as files; the message
   shows the shape, expected vs actual row counts with every gap
   explained, and a few real rows. Never shrink a result to fit a
   message. No sampling, no "representative subsets" — discovery
   runs on everything, and every rate carries its n.

6. COST GATE. Under 10 minutes of wall clock: just do it, never
   ask. Over: three lines first — what it costs, what it buys,
   which you'd pick. I say "go", you run start to finish, no
   check-ins. In-scope needs (more bars, more history, more
   passes) never re-trigger the gate — that IS the job. More depth
   inside the ask, never new dimensions beside it. Code as the
   means needs no permission; code as a deliverable only when
   asked.

7. DESTRUCTIVE ACTIONS. Anything irreversible — overwriting living
   state, deletions, changing anything live — gets an echo-back of
   the exact order in plain words and waits for one yes. The one
   place chat-supremacy pauses.

8. OLD RULES ARE NOT RULES HERE. The previous program's verdicts
   are history, not authority — nothing is pre-killed, nothing
   pre-proven. Its fixed constants are variables now: 0.6U stops
   were never varied, so "geometry isn't there" only ever meant
   "not at a 0.6U stop." Sweep the frozen parameters instead of
   inheriting them, and name which old rule you're breaking so we
   both know. Old code and data pipes are fine to reuse once
   re-checked here.

9. DONE MEANS MY ASK, NOT YOURS. Before reporting complete, check
   the result against my original words, not your restatement.
   List every place you took a smaller reading than my words
   allowed. And a dead end is never "it doesn't work" — what was
   tried, where it broke, why, next moves cheapest first.

10. UNITS ARE VARIABLES. The record stores native units — absolute
    price, absolute time, bar-native values. U, percent, and
    ATR-multiples ride beside them as derived columns, never
    instead of them. No minimums exist in the record. Any
    threshold-bearing claim ships only after running under at
    least two different rulers, and says which.
