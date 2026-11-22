---
name: tutorial-style
description: House style for the smart-insole tutorial series. Audience model, chapter structure, software analogies, sim-path/hardware-path tabs, citations, admonitions, glossary rules, notebook rules. Use whenever writing or reviewing tutorial chapters, notebook prose, or the docs site.
user-invocable: false
---

# Tutorial style guide

## The reader

An experienced **software developer**: fluent in Python and/or TypeScript, git, the CLI, testing,
HTTP/JSON, async code. **No electronics** (does not know what a pull-down resistor or an ADC
reference voltage is). **No biomechanics** (does not know stance versus swing, or what a force
plate is). Smart, busy, and allergic to hand-waving. They want to understand *why*, and to rebuild
the project themselves.

## Principles

1. **Bridge from software.** Introduce each new concept with the closest software analogy, then
   say explicitly where it breaks. Examples:
   - an ADC is like sampling audio into integers; the sample rate and bit depth trade off the same
     way;
   - a voltage divider turns a resistance into a voltage the ADC can read; it's a "serializer" from
     physical to readable;
   - I2C is a shared bus with addresses, like many services behind one load balancer and a routing
     key, but slow, and one misbehaving device can hang the bus;
   - a BLE GATT service is a tiny typed key-value API where clients subscribe to change
     notifications, a bit like a WebSocket topic;
   - an interrupt handler is like a signal handler: do the minimum, defer the rest;
   - firmware's main loop is like a game loop or event loop;
   - calibration is fitting a model from known inputs, like regression with a test set;
   - the gait cycle is a state machine with timing: stance (foot on ground) → swing (foot in the
     air), with a flight phase when running.
2. **Why before how.** Each section opens with the problem it solves.
3. **Concrete over abstract.** Use real numbers with units, real pin names, real commands, real
   plots, and show the expected output.
4. **Honest engineering.** Include what went wrong when we built it (from the journal). Show
   trade-offs and the human's gate decisions.
5. **Safety inline, before the risk.** Put a `!!! danger` admonition immediately before the step
   that carries the risk, never only in an appendix.
6. **Cite everything factual.** Use source ids from `research/sources.yaml`, rendered as links to
   `docs/reference/sources.md#<id>`. Label our own measurements: "measured on our prototype; see
   validation report".
7. **No medical claims.** Use awareness and estimation language only (see `state/guardrails.md`).

## Structure

Use `chapter-template.md` (next to this file). Every chapter has:

- front matter (status, phase, time, cost, prerequisites, sources);
- an `abstract` box with learning objectives;
- the software developer's mental model;
- core concepts;
- hands-on with **both paths as tabs** reaching the same checkpoint;
- what went wrong when we built it;
- a troubleshooting table;
- a recap;
- going further;
- references;
- behind the scenes (links to journal entries, ADRs and gate packets).

## Markdown conventions (MkDocs Material)

- Admonitions:
  - `!!! info "Software analogy"`;
  - `!!! note "Body background"` for anatomy and biomechanics asides;
  - `!!! danger "Safety"`;
  - `!!! success "Checkpoint"`;
  - `!!! warning`;
  - `!!! tip`;
  - `??? question "Exercise"` (collapsible).
- Tabs: `=== "Simulation path"` / `=== "Hardware path"`, with the content indented 4 spaces.
- Diagrams: mermaid code fences for flows and state machines. For circuits, use ASCII or SVG in
  `docs/assets/`, with descriptive alt text.
- Math: `$...$` inline and `$$...$$` block (arithmatex). Define every symbol.
- Terms: on first use, bold the term and define it in one sentence. Add it to
  `docs/reference/glossary.md` and, for abbreviations, `docs/includes/abbreviations.md`
  (`*[ADC]: Analog-to-Digital Converter`), which adds hover tooltips on every page.
- Links are relative (`../reference/glossary.md#adc`). `mkdocs build --strict` must pass.
- Chapter ids: `A*` foundations, `B*` idea to design, `C*` building, `D*` validation, `E*` custom
  hardware. Files: `docs/chapters/<id-lower>-<slug>.md`.

## Notebooks (`docs/notebooks/`)

- Run top to bottom in < 2 minutes with no hardware, on public data fetched by a script or on
  `data/samples/`.
- The first cell is markdown: goal, data used (with licence), and how to run locally.
- Alternate short code cells with prose explaining *what to notice* in each plot.
- Save outputs so the site shows the plots. Clear any personal data from outputs.

## Voice

Second person, active voice, friendly, precise. Short paragraphs. No "simply", "just" or
"obviously". Prefer UK/Australian spelling (the project owner is in Australia): "metre", "colour",
"analyse".
