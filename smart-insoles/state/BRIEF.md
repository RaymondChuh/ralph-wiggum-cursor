# Project brief

This is the project's charter, built from the owner's interview on 2026-11-21. Agents treat it as
binding. Only the human changes it; if an agent thinks it should change, they say so at the next
gate.

## Goal

Research, design and build a **smart insole for gait analysis in sport and running**, starting
from existing open-source projects and research papers. In parallel, write a **tutorial series**
that teaches the journey to software developers who have little hardware or medical background.

## Scope

| Topic | Decision |
|---|---|
| Application | Running and sport gait analysis: **performance + injury-risk awareness** (cadence, ground contact time, foot-strike pattern, loading, left/right symmetry). Medical depth stays at anatomy, biomechanics and injury science. No diagnosis or treatment. |
| Build path | **Stage 1:** working prototype on off-the-shelf dev boards. **Stage 2:** custom hardware (PCB, flexible sensor, enclosure), only if gate G4 decides it is worth it. |
| Sources | Agents find and rank open-source projects, papers and datasets; **the human approves the shortlist (G1)** before design work starts. |
| Firmware stack | **Agents recommend** 2–3 options with trade-offs at the design gate (G3); the human picks one. |
| Software stack | **Python** (numpy/scipy/pandas) for gait algorithms and notebooks; **browser dashboard over Web Bluetooth** (TypeScript) for live data. |
| Budget | Parts lists come in **budget / standard / premium** tiers in **AUD**; the human picks at G3. |
| Region | **Australia**: prefer suppliers that ship there (Core Electronics, Jaycar, Altronics, element14 AU, DigiKey AU, Mouser AU; AliExpress as a cheap, slow option). |
| Validation references available | Running watch / foot pod, 240fps phone slow-motion video, treadmill, bathroom/kitchen scale. |
| Where it runs | The human's **local machine**, with the board on USB. Agents may build firmware; flashing always asks the human's permission. |

## Approval gates (agents stop and wait)

1. **G1** Source shortlist
2. **G2** Concept and requirements
3. **G3** Design freeze: stack, BOM tier, purchase list (before any money is spent)
4. **Every hardware-in-the-loop step**: agents prepare instructions, the human does the physical
   step, agents verify
5. **G4** Stage-1 review: go custom / iterate / finish
6. **G5** Fabrication order for custom hardware

Everything else runs autonomously. Only the human records decisions (`/approve`, `/reject`,
`/hil-done`, `/hil-failed`).

## Tutorials

- **Format:** MkDocs Material site (`docs/`) + Jupyter notebooks (`docs/notebooks/`).
- **Process:** agents keep a build journal (`docs/journal/`) while they work. After each phase, the
  tutorial-writer turns it into polished chapters. The novice-reader, gait-scientist and
  safety-claims reviewers check every chapter.
- **Two reader paths:** every hardware chapter has a **simulation / recorded-data path**
  (no hardware needed) and a **real-hardware path**.
- **Audience:** experienced software developers (Python/JS, git, CLI, testing) with no
  electronics and no biomechanics background.

## Data and licensing

- The human's own recordings are personal biometric data. **Raw recordings stay local**
  (`data/raw/` is gitignored). Only **small, de-identified samples** go into `data/samples/`.
- **Code: MIT. Tutorials and docs: CC BY 4.0.** Prefer permissively licensed sources. Flag GPL,
  non-commercial and unlicensed sources at G1, because they would constrain these licences.

## Out of scope

- Medical diagnosis, treatment or clinical claims. The product is a wellness/performance tool.
- Mains-powered anything. Everything is low-voltage and battery-powered.
- Buying anything on the human's behalf.
