# Start here

## How this series is made

The project is run by an **agent harness**: specialist AI agents (research scout, gait scientist,
hardware engineer, firmware engineer, software engineer, tutorial writer and reviewers) coordinated
by a lead agent, with a human maker who approves every key decision and does every physical step.
The agents keep a [build journal](../journal/index.md) as they work. When a phase finishes, the
tutorial writer turns the journal into polished chapters, and three reviewers check them: a
"novice reader" persona, a domain expert and a safety/claims reviewer.

That means you see the real path, including the dead ends. Each chapter ends with a **Behind the
scenes** section linking to the journal entries and decisions it came from.

## What you need

| | Simulation path | Hardware path |
|---|---|---|
| Computer | Any laptop with Python 3.11+ and a modern browser | Same, plus a free USB port |
| Browser | Chrome or Edge for the Web Bluetooth dashboard (Safari/iOS don't support it) | Same |
| Hardware | None | Parts list from chapter B3 (tiers in AUD) |
| Tools | None | Soldering iron, multimeter and basics (listed in the BOM) |
| Time | ~1–2 h per chapter | Add 1–3 h per build chapter |

## Conventions

- **Units** are SI and always written: N (newtons), ms, Hz, V, mA.
- Terms are **bolded and defined** on first use and collected in the [glossary](../reference/glossary.md).
  Hover over abbreviations like ADC or IMU for a tooltip.
- Citations link to the [bibliography](../reference/sources.md).
- Admonition boxes:

!!! info "Software analogy"
    Connects a new idea to something you already know, and says where the comparison breaks down.

!!! note "Body background"
    Short anatomy or biomechanics asides.

!!! danger "Safety"
    Appears right before a step that could hurt you or the hardware. Don't skip these.

!!! success "Checkpoint"
    What you should see if everything worked.

## Licences

Tutorials and docs: **CC BY 4.0**. Code: **MIT**. Third-party sources keep their own licences;
see the [bibliography](../reference/sources.md).
