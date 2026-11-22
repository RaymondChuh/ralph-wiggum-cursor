# Backlog

The task queue for the whole project. `python3 scripts/harness.py next` reads this file to pick the
single next action.

**Format:** `- [ ] P<phase>-<nn> <task text>  <!-- owner: <agent>; after: <gate,...>; hil: true -->`

- `owner` is the agent file in `.claude/agents/` that does the work. `lead` means the orchestrator,
  i.e. the main session itself.
- `after` lists gates that must be human-approved before the task can start. Phase exit gates (see
  `state/workflow.json`) already block the next phase, so `after` is only needed for gates in the
  middle of a phase.
- `hil: true` marks a hardware-in-the-loop step. The agent writes instructions, the human does the
  physical step, the agent verifies the evidence. Ticking a HIL task without a recorded `/hil-done`
  fails `harness.py validate`.
- Agents tick `[x]` when a task meets its acceptance criteria. Agents may add tasks (next free
  number in that phase) and split coarse tasks. They never delete tasks: obsolete ones are ticked
  and annotated `(obsolete: why)`.
- Tutorial chapters for a phase are written at the start of the following phase, so they can
  describe the human's gate decision.

## P1 Research & source discovery

- [ ] P1-01 Write the search plan: questions to answer, keywords (running gait, plantar pressure, smart insole, FSR, IMU, open hardware), sources to search; log it in research/search-log.md  <!-- owner: research-scout -->
- [ ] P1-02 Survey open-source smart-insole / plantar-pressure / foot-IMU projects (GitHub, GitLab, Hackaday, OSHWA); register each in research/sources.yaml with its licence  <!-- owner: research-scout -->
- [ ] P1-03 Survey peer-reviewed papers on insole sensor layouts, gait-event detection, running metrics and validation against force plates; register them in research/sources.yaml  <!-- owner: research-scout -->
- [ ] P1-04 Survey public datasets (insole pressure, foot IMU, running gait) with licence and access terms; register them in research/sources.yaml  <!-- owner: research-scout -->
- [ ] P1-05 Benchmark commercial running insoles and pods for features and claimed metrics (benchmarking only; their code and designs are not reused); write research/landscape.md  <!-- owner: product-ideator -->
- [ ] P1-06 Score all candidates with the source-evaluation rubric and write research/shortlist.md (top 3 base projects, 5–10 core papers, 1–3 datasets)  <!-- owner: research-scout -->
- [ ] P1-07 Licence, safety and claims check of the shortlist; findings appended to research/shortlist.md  <!-- owner: safety-claims-reviewer -->
- [ ] P1-08 Prepare gate request G1 (`harness.py open-gate G1`) with the recommendation and alternatives  <!-- owner: research-scout -->

## P2 Literature synthesis & primers

- [ ] P2-01 Tutorial B1 "Prior art: what exists and what we chose" from the P1 journal, shortlist and G1 decision  <!-- owner: tutorial-writer -->
- [ ] P2-02 Deep-read the approved base project(s): architecture, sensors, firmware, data format, known issues; write research/notes/<source-id>.md  <!-- owner: literature-analyst -->
- [ ] P2-03 Deep-read the approved papers: extract sensor layouts, sampling rates, algorithms, accuracy versus reference; write research/notes/<source-id>.md  <!-- owner: literature-analyst -->
- [ ] P2-04 Write research/synthesis/state-of-the-art.md: what works, known limitations of insole sensing, gaps, open questions  <!-- owner: literature-analyst -->
- [ ] P2-05 Tutorial A1 "Running gait and the foot for software developers" (facts from gait-scientist, cited)  <!-- owner: tutorial-writer -->
- [ ] P2-06 Tutorial A2 "Electronics for software developers": voltage, current, resistance, voltage dividers, ADCs, I2C/SPI, BLE, batteries  <!-- owner: tutorial-writer -->
- [ ] P2-07 Tutorial A3 "Reading papers and open-hardware repos as a developer"  <!-- owner: tutorial-writer -->
- [ ] P2-08 Notebook N1: load an approved public dataset, plot pressure/IMU signals, find gait events by eye (data fetched by a script, not committed)  <!-- owner: software-engineer -->
- [ ] P2-09 Run /review-tutorial on A1, A2, A3, B1 and N1; apply the fixes  <!-- owner: tutorial-writer -->

## P3 Product ideation & requirements

- [ ] P3-01 Personas and jobs-to-be-done for runners and athletes; write ideation/personas.md  <!-- owner: product-ideator -->
- [ ] P3-02 Metric catalogue: which running metrics an insole can measure, from which sensors, with evidence and expected accuracy; write ideation/metrics.md  <!-- owner: gait-scientist -->
- [ ] P3-03 Two or three concept options with feature sets, sensor needs, complexity and risk; write ideation/concepts.md  <!-- owner: product-ideator -->
- [ ] P3-04 Claims review: wellness-versus-medical boundary for each concept (TGA, FDA, EU MDR); add findings to ideation/concepts.md  <!-- owner: safety-claims-reviewer -->
- [ ] P3-05 Requirements for the recommended concept (functional, accuracy, sampling, battery life, comfort, data/privacy) with acceptance tests; write ideation/requirements.md  <!-- owner: product-ideator -->
- [ ] P3-06 Prepare gate request G2  <!-- owner: product-ideator -->

## P4 Prototype design

- [ ] P4-01 Tutorial B2 "From metrics to requirements" from the P3 journal and G2 decision  <!-- owner: tutorial-writer -->
- [ ] P4-02 Microcontroller/firmware stack options (2–3) with trade-offs: sampling, BLE, power, simulator support, beginner-friendliness, path to a custom PCB; write design/stack-options.md  <!-- owner: firmware-engineer -->
- [ ] P4-03 Sensor selection and placement (count, type, insole layout, IMU mounting) with cited evidence; write design/hardware/sensors.md  <!-- owner: hardware-engineer -->
- [ ] P4-04 Circuit design: signal conditioning, ADC/multiplexing, power and battery, wiring diagram; write design/hardware/circuit.md  <!-- owner: hardware-engineer -->
- [ ] P4-05 BOM in budget/standard/premium tiers with Australian suppliers, AUD prices (incl. GST) and price-check date; write design/hardware/bom.csv and bom.md  <!-- owner: hardware-engineer -->
- [ ] P4-06 Firmware architecture and data protocol (sample rate, timestamps, BLE GATT layout, packet format, on-device logging); write design/firmware.md  <!-- owner: firmware-engineer -->
- [ ] P4-07 Software architecture: gaitlab Python package and Web Bluetooth dashboard; write design/software.md  <!-- owner: software-engineer -->
- [ ] P4-08 Validation plan using running watch/foot pod, 240fps phone video, treadmill and scale (protocols, metrics, agreement statistics); write validation/plan.md  <!-- owner: gait-scientist -->
- [ ] P4-09 Safety review of the design (battery placement and charging, skin contact, moisture, cable strain, heat)  <!-- owner: safety-claims-reviewer -->
- [ ] P4-10 Record design decisions as ADRs in design/decisions/  <!-- owner: hardware-engineer -->
- [ ] P4-11 Prepare gate request G3 (stack choice, BOM tier, exact purchase list per tier)  <!-- owner: hardware-engineer -->

## P5 Build

- [ ] P5-01 Tutorial B3 "Designing the prototype: sensors, circuit, BOM" from the P4 journal and G3 decision  <!-- owner: tutorial-writer -->
- [ ] P5-02 Refine this phase: split P5 into concrete firmware/software/hardware tasks from the approved design, marking every physical step `hil: true`  <!-- owner: lead -->
- [ ] P5-03 Firmware skeleton that builds, has host-side unit tests and a simulator configuration (e.g. Wokwi) for the no-hardware path  <!-- owner: firmware-engineer -->
- [ ] P5-04 gaitlab: ingest, filtering and gait-event detection, tested against the approved public dataset  <!-- owner: software-engineer -->
- [ ] P5-05 Parts arrival check: inventory against the approved BOM, visual inspection  <!-- owner: hardware-engineer; hil: true -->
- [ ] P5-06 Single-sensor bench test: one pressure sensor + divider + ADC, readings versus known weights on the kitchen scale  <!-- owner: hardware-engineer; hil: true -->
- [ ] P5-07 Live dashboard: Web Bluetooth stream view of the protocol from P4-06  <!-- owner: software-engineer -->
- [ ] P5-08 Full insole assembly and bring-up (flash firmware, confirm every channel responds)  <!-- owner: hardware-engineer; hil: true -->
- [ ] P5-09 End-to-end integration: capture → gaitlab → dashboard on a short walking trial  <!-- owner: software-engineer; hil: true -->
- [ ] P5-10 Tutorials C1 firmware, C2 data pipeline (notebook), C3 dashboard, C4 assembly; each with a sim path and a hardware path  <!-- owner: tutorial-writer -->
- [ ] P5-11 Run /review-tutorial on the P5 chapters; apply the fixes  <!-- owner: tutorial-writer -->

## P6 Validation

- [ ] P6-01 Static calibration of the pressure sensors against the scale; record the calibration model  <!-- owner: gait-scientist; hil: true -->
- [ ] P6-02 Treadmill sessions at set speeds, recorded together with the running watch/foot pod and 240fps phone video (raw data stays local)  <!-- owner: gait-scientist; hil: true -->
- [ ] P6-03 Label foot-strike and toe-off events from the video; align clocks across devices  <!-- owner: gait-scientist -->
- [ ] P6-04 Agreement analysis (bias, limits of agreement, MAE) for cadence, ground contact time and foot-strike pattern; write validation/report.md  <!-- owner: gait-scientist -->
- [ ] P6-05 Build a de-identified sample dataset for tutorial readers in data/samples/ with a dataset card  <!-- owner: software-engineer -->
- [ ] P6-06 Tutorial D1 "Does it work? Validating against a watch, video and a treadmill" + notebook N2  <!-- owner: tutorial-writer -->
- [ ] P6-07 Stage-1 retrospective and recommendation: custom hardware, iterate the prototype, or finish; write validation/retrospective.md  <!-- owner: hardware-engineer -->
- [ ] P6-08 Tutorial D2 "Retrospective: what we'd change" and /review-tutorial on D1, D2 and N2  <!-- owner: tutorial-writer -->
- [ ] P6-09 Prepare gate request G4 with options custom / iterate / finish  <!-- owner: gait-scientist -->

## P7 Stage 2: custom hardware

- [ ] P7-01 Tutorial E1 "When (and why) to design custom hardware"  <!-- owner: tutorial-writer -->
- [ ] P7-02 Custom architecture: MCU module, flexible or printed pressure-sensor options, battery and charging, enclosure; write design/custom/architecture.md  <!-- owner: hardware-engineer -->
- [ ] P7-03 KiCad schematic with ERC passing  <!-- owner: hardware-engineer -->
- [ ] P7-04 PCB and flexible-sensor layout with DRC passing  <!-- owner: hardware-engineer -->
- [ ] P7-05 Fabrication and assembly quotes (AUD, shipping to Australia) and unit cost  <!-- owner: hardware-engineer -->
- [ ] P7-06 Safety review of the custom design (charging, ESD, enclosure, skin contact)  <!-- owner: safety-claims-reviewer -->
- [ ] P7-07 Prepare gate request G5 (fabrication order)  <!-- owner: hardware-engineer -->
- [ ] P7-08 Custom board bring-up  <!-- owner: hardware-engineer; after: G5; hil: true -->
- [ ] P7-09 Re-validation against the stage-1 results  <!-- owner: gait-scientist; after: G5; hil: true -->
- [ ] P7-10 Tutorials E2 "Schematic and PCB with KiCad" and E3 "Bring-up and re-validation"; /review-tutorial  <!-- owner: tutorial-writer; after: G5 -->
