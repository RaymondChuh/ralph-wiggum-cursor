---
name: tutorial
description: Write or refresh a tutorial chapter (or all chapters of a phase) from the build journal, artifacts and gate decisions, then send it to review.
disable-model-invocation: true
argument-hint: "<chapter-id like A1 | phase like P2>"
---

Target: `$ARGUMENTS`

1. Resolve the target using `docs/chapters/index.md` (the curriculum map). A phase id means every
   chapter mapped to that phase. If the target is unknown, list the valid ids and stop.
2. Gather inputs for each chapter:
   - the journal entries for the mapped phase(s) (`docs/journal/`);
   - the artifacts they link to;
   - the gate packets and the human's decision notes;
   - existing chapter text, if this is a refresh.
3. Delegate to `tutorial-writer` with those paths, the chapter id, title, learning objectives (from
   the curriculum map) and the `tutorial-style` skill. If the chapter needs a notebook, delegate the
   code cells to `software-engineer` first, or in parallel if they are independent.
4. Run `mkdocs build --strict` if MkDocs is installed (`pip install -r requirements-docs.txt`).
   Fix any failures.
5. Run the review workflow (`/review-tutorial` steps) on the result, unless the human asked for a
   draft only.
6. Update the chapter's status in `docs/chapters/index.md`, tick any matching backlog task, write a
   journal line, and commit (`insoles(docs): <chapter-id> <status>`).
