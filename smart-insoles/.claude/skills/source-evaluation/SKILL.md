---
name: source-evaluation
description: How to verify, register, licence-check and score open-source projects, papers and datasets for the smart-insole project (research/sources.yaml schema, scoring rubric, licence compatibility matrix). Use when finding, registering, ranking or citing any source.
user-invocable: false
---

# Source evaluation

## Verification (non-negotiable)

A source enters `research/sources.yaml` only after an agent **opened its URL** and confirmed the
title, authors/owner and year, and found the licence. Set `verified: YYYY-MM-DD`. If a detail
cannot be confirmed, write `unknown`; never guess. Search snippets, memory and LLM recall do not
count as verification.

## Registry entry

```yaml
- id: kebab-case-unique          # e.g. smith2021-insole-gct, gh-openinsole
  type: repo                     # repo | paper | dataset | product | standard | web | book
  title: "Exact title"
  url: https://...
  doi: 10.xxxx/...               # papers, if any
  authors: ["Surname, A.", ...]  # or owner/org for repos
  year: 2023
  license: MIT                   # SPDX id | unknown | proprietary | paper-copyright | CC-BY-4.0 ...
  reuse: full                    # full | attribution | learn-only | none (see the matrix below)
  verified: 2026-11-21
  status: candidate              # candidate | shortlisted | approved | rejected | reference
  relevance: running             # running | walking-only | general-gait | hardware-only | other
  scores: {licence: 5, relevance: 4, reproducibility: 3, documentation: 3, maintenance: 2, evidence: 3, au_parts: 4}
  total: 3.6
  summary: "One sentence: what it is and why it matters to us."
  notes_file: research/notes/<id>.md
```

## Scoring rubric (1–5 per criterion; weighted average = `total`)

**Repositories and open hardware**

| Criterion (weight) | 1 | 3 | 5 |
|---|---|---|---|
| Licence (×2) | none / NC / proprietary | copyleft (GPL, CERN-OHL-S) = learn-only | permissive (MIT, BSD, Apache-2.0, CERN-OHL-P, CC BY) |
| Relevance (×2) | walking/clinical only | gait generally | running/sport, insole form factor |
| Reproducibility (×1.5) | code only | code + partial BOM/schematic | firmware + schematic + BOM + build guide + data format |
| Documentation (×1) | none | README | guide, diagrams, results |
| Maintenance (×0.5) | > 4 years idle | some activity | active, issues answered |
| Evidence (×1) | no testing | demo plots | validated against a reference |
| AU parts availability (×1) | obsolete or exotic parts | partly available | all parts stocked by AU suppliers |

**Papers:** relevance (running, insole; ×2), study quality (participant count, population, reference
standard such as force plate or instrumented treadmill; ×2), reported agreement statistics (bias,
LoA, MAE, ICC rather than only r; ×1.5), openness (open access, data/code available; ×1), recency
(×0.5), independence (no vendor conflict; ×0.5).

**Datasets:** licence and access (open versus credentialed versus by-request; ×2), sensor match
(insole pressure and/or foot IMU; ×2), includes running (×2), sampling rate ≥ 100 Hz (×1), event
labels or reference measurements (×1.5), size and documentation (×1).

## Licence compatibility (our outputs: code MIT, docs CC BY 4.0)

| Source licence | What we may do | `reuse` |
|---|---|---|
| MIT, BSD-2/3, ISC, Zlib, Apache-2.0, Unlicense, CC0 | Copy and modify with attribution (Apache-2.0: keep NOTICE, note the patent clause) | full |
| CC BY 4.0 (text, figures, data) | Reuse with attribution | attribution |
| MPL-2.0 | Use files as-is; modifications to those files stay MPL | attribution |
| LGPL | Linking is complicated on microcontrollers (static linking); avoid copying | learn-only |
| GPL-2/3, AGPL, CERN-OHL-S, CC BY-SA | Copying would make our derivative copyleft; learn and link only, unless the human approves at G1 | learn-only |
| CC BY-NC, CC BY-ND, "research use only" | Cite and link; no reuse in our outputs | none |
| No licence | All rights reserved; read and link only | none |
| Paper (publisher copyright) | Cite; describe in our own words; no figures | none |
| PhysioNet credentialed / data-use agreement | The human must sign up themselves; never redistribute | none |

When unsure, mark `learn-only` and raise it at G1. You are not a lawyer; say so and flag it.

## Shortlist format (research/shortlist.md)

Ranked tables per type (base project, papers, datasets): id, title, total, licence/reuse, one-line
why. Then a paragraph of rationale per pick, the runners-up, the gaps no source covers, and the
licence consequences of the recommended combination.
