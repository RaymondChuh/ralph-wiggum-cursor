---
name: review-tutorial
description: Run the three-reviewer check on a tutorial chapter or notebook (novice reader, domain accuracy, safety/claims), then have the writer fix blockers and majors.
disable-model-invocation: true
argument-hint: "<chapter-id | path under docs/>"
---

Target: `$ARGUMENTS`

1. Resolve it to file path(s) under `docs/chapters/` or `docs/notebooks/`.
2. Launch these reviewers **in parallel**. Each writes a report to `state/reviews/` using the
   format in its agent definition:
   - `novice-reviewer`: clarity, jargon, missing steps, broken sim/hardware paths;
   - `gait-scientist`: domain accuracy, numbers, citations, over-claiming. Ask it to write
     `state/reviews/<date>-<slug>-domain.md` with ids D-01...;
   - `safety-claims-reviewer`: safety instructions, claims language, privacy, licences of reused
     material.
3. Merge the findings into a triage list, sorted by severity, and remove duplicates.
4. Delegate the fixes to `tutorial-writer`: every `blocker` and `major` must be fixed; for `minor`
   and `nit`, fix them or explain the decision. The writer appends a `Resolution:` line to each
   finding in the reports.
5. Re-run `mkdocs build --strict` if available.
6. If any safety blocker remained unresolved, stop and tell the human. Otherwise set the chapter's
   front matter `status: reviewed`, update `docs/chapters/index.md`, and commit
   (`insoles(docs): review <chapter-id>`).
7. Report the counts by severity and anything the human should look at.
