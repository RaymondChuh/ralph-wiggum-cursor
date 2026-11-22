---
name: hardware-in-the-loop
description: Protocol for steps where the human must physically act (assemble, wire, flash, measure, run on the treadmill). How agents write HIL instructions, hand over, verify evidence, and troubleshoot failures. Use for any backlog task marked `hil: true`.
user-invocable: false
---

# Hardware-in-the-loop (HIL) protocol

Agents cannot see, touch or power hardware. The human is the agents' hands. HIL steps therefore
need instructions good enough for a first-timer, evidence that proves what happened, and a clean
hand-off in both directions.

## Lifecycle

```
prepare_hil → (human acts) → /hil-done   → verify_hil → task ticked
                           ↘ /hil-failed → fix_hil → revision+1 → (human acts again)
```

1. **Prepare**: `python3 scripts/harness.py open-hil <TASK>` creates `state/hil/<TASK>.md` from the
   template. Fill in every section, then **stop the session**. Tell the human to run `/hil <TASK>`.
2. **Human acts**, then types `/hil-done <TASK> <observations>` or `/hil-failed <TASK> <what
   happened>`. A hook records it. **Agents never record HIL outcomes.**
3. **Verify** (mode `verify_hil`): check the evidence against the stated criteria. Fill in "Agent
   verification" in the request file. Tick the backlog task only if it passes.
4. **Fix** (mode `fix_hil`): troubleshoot from the notes, revise the instructions (`open-hil` bumps
   the revision), and add "Changes in revision N". Stop again.

## Writing good instructions

- **One action per step**, numbered. Give pin names exactly as printed on the board, wire colours
  if helpful, component values, and orientation (FSR tails, diode or LED polarity, battery
  connector polarity).
- **Safety box first**, specific to this step. Unplug power before every wiring change.
- **Checkpoints every 3–5 steps**: "You should now see/measure ...". Give the multimeter mode and
  the expected range (e.g. "continuity beep between A and B", "about 3.3 V between 3V3 and GND").
- **Exact commands** for building, flashing and capturing, with the expected output. Flashing will
  show a permission prompt in Claude Code; tell the human that is expected.
- **Evidence capture**: serial or BLE logs go to `data/raw/hil/<TASK>/` (gitignored). Name files
  `<TASK>-<what>-<YYYYMMDD-HHMM>.csv/.log`. Ask for specific numbers in the `/hil-done` notes.
  Optional photos go to `hardware/proto-v1/photos/<TASK>/`, and only if they contain no personal
  details.
- **Abort conditions**: heat, smell, smoke, a swollen battery, readings pinned at 0 or full scale,
  repeated resets. On any of these: power off, then `/hil-failed`.
- **Time box**: estimate the minutes. If a step is longer than about 45 minutes, split it into
  several HIL tasks.

## Verifying

- Load the logs and check the sample rate achieved, channel count, plausible ranges, no stuck
  channels, and the expected response to stimulus (press heel → heel channel rises).
- Compare the human's reported numbers with the expected ranges in the request.
- Record **pass/fail per criterion** in "Agent verification". Partial passes mean "fix", not "tick".

## Troubleshooting order (cheapest and most likely first)

Power and ground → connections and continuity → orientation and polarity → correct pins in the
firmware config → firmware actually flashed (version string) → sensor-specific behaviour → anything
exotic.
