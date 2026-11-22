# Guardrails ("Signs")

These are lessons learned, written as signs next to the slide (a metaphor from the Ralph technique
in this repo's root). Read this file before working on any task. Add a sign when a mistake happens
twice, when a subtle problem is found, or when the human corrects you. Use `/sign` or edit this
file directly.

```markdown
### Sign: <short name>
- **Trigger**: <when this applies>
- **Instruction**: <what to do instead>
- **Added after**: <task id / date / what went wrong>
```

## Seed signs (from the project brief)

### Sign: Decisions belong to the human
- **Trigger**: A gate or hardware-in-the-loop step is pending, or you are tempted to "assume approval".
- **Instruction**: Stop and summarise what the human must decide or do. Never write `state/gates/decisions.jsonl`; only the human's typed `/approve`, `/reject`, `/hil-done` and `/hil-failed` record decisions.
- **Added after**: Harness design (2026-11-21).

### Sign: No source, no claim
- **Trigger**: Writing any number, physiological fact, algorithm accuracy or "studies show".
- **Instruction**: Cite a registered source id from research/sources.yaml whose URL you actually opened. If you cannot verify it, write "unverified" and add a follow-up task. Never invent a citation, DOI, author or dataset.
- **Added after**: Harness design (2026-11-21).

### Sign: Wellness, not medicine
- **Trigger**: Describing what the insole does in docs, UI text, the README or tutorials.
- **Instruction**: Use awareness language: "see how your cadence changes", "estimate ground contact time". Never write "prevents injury", "diagnoses", "treats" or "clinically proven". Ask the safety-claims-reviewer when unsure.
- **Added after**: Harness design (2026-11-21).

### Sign: An FSR reading is not a calibrated force
- **Trigger**: Turning raw pressure-sensor ADC counts into force, load or pressure numbers.
- **Instruction**: State the calibration model and its limits (non-linearity, hysteresis, drift/creep, temperature, partial foot coverage). Raw counts may only be compared within one sensor and session unless calibrated.
- **Added after**: Harness design (2026-11-21).

### Sign: Personal data stays local
- **Trigger**: Saving, committing or publishing recordings, video, GPS or device identifiers.
- **Instruction**: Raw goes to data/raw/ (gitignored). Only de-identified, trimmed samples with a dataset card go to data/samples/. Follow the data-handling skill.
- **Added after**: Harness design (2026-11-21).

### Sign: The battery never goes under the foot
- **Trigger**: Placing a LiPo or Li-ion cell, or designing an enclosure.
- **Instruction**: Lithium cells are not loaded or flexed by the foot. Put them in a pod on the shoe or ankle, use a protected cell and a proper charger, and never charge one unattended. See the hardware-safety-and-claims skill.
- **Added after**: Harness design (2026-11-21).

## Learned signs

<!-- Agents append new signs below this line. -->
