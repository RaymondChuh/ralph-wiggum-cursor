# Build journal

The raw, dated log the agents write while they work: what they set out to do, what they did, what
they learned, the dead ends, and the decisions. It is the source material for the polished
chapters. Mistakes stay in, because they are often the most useful part.

Entries are named `YYYY-MM-DD-<title>.md` and created with
`python3 scripts/harness.py devlog "<title>" --phase P<n>`. Newest entries sort last.
