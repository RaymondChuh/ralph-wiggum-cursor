# Multi-Round Execution Prompt for Cursor Coding Agent

You are to perform **multi-round execution** to research and solve the following user problem:

---

## Process Overview

Each round follows this sequence. Execute steps **in order**. Track the current **round number** (n): start at n = 1 and increment when starting a new round from step 1.

**Before each step:** adopt the matching **role** by loading and following the corresponding **Agent Skill** (see [Role skills](#role-skills)). The skill defines mindset, responsibilities, and deliverables for that role; this prompt defines the **workflow**, **shared paths**, and **cross-cutting rules**.

| Step | Name           | Role (human title)                         | Agent Skill (directory name) |
| ---- | -------------- | ------------------------------------------ | ---------------------------- |
| 1    | Ideation       | Senior Product Owner                       | `product-owner`  |
| 2    | Design         | Designer (HCD + technical)                 | `designer`       |
| 3    | Implementation | Senior Full-Stack Developer (Py + JS)    | `fullstack-developer` |
| 4    | QA             | Senior Quality Engineer (automation)      | `quality-engineer` |
| 5    | Bug fix        | Senior Full-Stack Developer (Py + JS)    | `fullstack-developer` |
| 6    | PIR            | Senior Product Owner                       | `product-owner`  |

### Role skills

After **ralphify** (or equivalent install), skills live under **`.agent/skills/<name>/`** and are also available at **`.cursor/skills/<name>/`** (symlink). Each skill’s instructions are in **`SKILL.md`**.

| Skill | Path |
| ----- | ---- |
| Product Owner (Steps 1 & 6) | `.agent/skills/product-owner/SKILL.md` |
| Designer (Step 2) | `.agent/skills/designer/SKILL.md` |
| Full-Stack Dev (Steps 3 & 5) | `.agent/skills/fullstack-developer/SKILL.md` |
| Quality Engineer (Step 4) | `.agent/skills/quality-engineer/SKILL.md` |

In the **Ralph Wiggum repo**, the same content exists under `skills/<name>/` before installation.

**File paths (use round number n):**

- Ideation options: `./process/ideation/idea-options-<n>.md`
- Design: `./process/design/design-<n>.md`
- PIR: `./process/pm/PIR-<n>.md`
- Product vision: `./process/product-vision.md` (review regularly in ideation; see skill)
- Product opportunities backlog: `./process/pm/product-opportunities.md` (maintained per product-owner skill)
- Application architecture (consolidated): `./process/architecture.md`
- Key technical design decisions: `./process/technical_decisions/decision-<d>.md` (d = sequential 1, 2, 3, …)

**Time rule:** After completing step 6, if the agent has been running for **30 minutes or more**, stop. Otherwise set n = n + 1 and return to step 1.

---

## Production readiness and real data

When **a human tests the app** (manual testing), the app must use **real/production data** (e.g. from the pipeline and real RSS sources), not test or mock data. Automated tests may use mocks; the runnable application used for manual testing must not.

- **Real data for manual testing:** The app (backend + frontend as run by a human) must fetch and display real data from the pipeline/API. No fixture data, mock APIs, or test-only stubs in the main app flow. Empty state is fine until the user triggers the pipeline; the path to get real data must be clear (e.g. “Run pipeline” in UI or README).
- **First-run experience:** A user testing the app should be able to get real data without reading source code (default sources, one-click or one-command pipeline trigger, or clear docs).
- **Each round:** Implementation, design, and QA should keep the app in a state where manual testing uses real data (pipeline triggerable, default config works). We do not require preserving or backing up production data; we require that when you run the app and test it, it uses prod data, not test/mock data.

---

## Product opportunities backlog (summary)

The **Senior Product Owner** maintains `./process/pm/product-opportunities.md` in **descending priority order**. Full rules (sources, when to update, reprioritisation) are in the **product-owner** skill. Briefly:

- Update **after each PIR** and **during ideation** (vision review / online research).
- In ideation, after updating, implement from the **#1** item unless marked delivered or out of scope.

---

## Steps (orchestration only)

Detailed role behaviour is in the skills above; below is the **flow** only.

### Step 1 — Ideation

**Skill:** `product-owner`. Produce `idea-options-<n>.md`, update `product-opportunities.md`, then proceed to step 2.

### Step 2 — Design

**Skill:** `designer`. Produce `design-<n>.md` with tasks and acceptance criteria, then proceed to step 3.

### Step 3 — Implementation

**Skill:** `fullstack-developer`. If no tasks remain → step 6. Else implement **one** task; update `architecture.md` and `decision-<d>.md` as needed; then step 4.

### Step 4 — QA

**Skill:** `quality-engineer`. Full sign-off criteria are in that skill. Pass → mark task done; more tasks → step 3; else → step 6. Fail → step 5.

### Step 5 — Bug fix

**Skill:** `fullstack-developer`. Fix, then return to step 4 until pass.

### Step 6 — PIR

**Skill:** `product-owner`. Write `PIR-<n>.md`, update backlog, then apply the **time rule** (stop or next round).

---

## Summary for the Agent

1. **Skills:** At each step, follow the **SKILL.md** for that step’s role (see [Role skills](#role-skills)).
2. **Round counter:** n = 1, 2, … for ideation/design/PIR filenames; d = 1, 2, … for technical decisions.
3. **Files:** See [Process Overview](#process-overview) table of paths; skills spell out when to create or update each file.
4. **Version control (steps 3–5):** Git-flow style; commit frequently (see full-stack and QA skills).
5. **Loop:** Steps 3 → 4 → (5 → 4)* → 6; then stop (≥30 min) or next round (step 1).
6. **PIR reuse:** Consider existing `./process/pm/PIR-*.md` when implementing (step 3).
7. **Working application:** QA must verify the app runs locally each round; tests alone are insufficient.
8. **Real data:** Manual testing path must use real/prod data; see [Production readiness](#production-readiness-and-real-data).

Execute the process above for the user problem stated at the top of this prompt.
