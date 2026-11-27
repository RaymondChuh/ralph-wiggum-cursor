---
name: gait-metrics
description: Reference for running gait concepts, insole-measurable metrics, gait-event detection approaches, sensor limitations and validation statistics. Use when defining metrics, writing algorithms, designing validation, or explaining running biomechanics to readers.
user-invocable: false
---

# Running gait metrics: working reference

This is a **working reference for agents, not a citable source**. Before any number below appears in
a tutorial, design or requirement, find and cite a registered source that supports it. Where this
file says "verify", the value is an engineering order of magnitude only.

## The gait cycle (state machine view)

- **Stride** = one full cycle of one foot (e.g. right initial contact → next right initial
  contact). **Step** = from one foot's initial contact to the other foot's initial contact. One
  stride = two steps.
- **Stance phase**: the foot is on the ground, from **initial contact (IC)**, a.k.a. foot strike,
  to **toe-off (TO)**. **Swing phase**: the foot is in the air.
- Walking has periods of **double support** (both feet down). **Running has none. Instead it has
  flight phases**, when neither foot touches the ground.
- **Duty factor** = stance time / stride time. It is above 0.5 in walking and below 0.5 in running.
  This is a clean way to classify walking versus running from insole data.

## Metrics an instrumented insole can estimate

| Metric | Definition / formula | Main sensor | Notes |
|---|---|---|---|
| Cadence | steps per minute = 60 / mean step time (s) | pressure or IMU | Robust; often the first metric validated |
| Step / stride time | time between successive ICs (same foot for stride) | pressure or IMU | Variability (CV%) is a research metric |
| Ground contact time (GCT) | TO − IC for one foot | pressure (best) | Running GCT is on the order of 150–300 ms (verify), so timing resolution matters |
| Flight time | IC(other foot) − TO(this foot), when > 0 | both insoles | Needs both feet and synchronised clocks |
| Duty factor | GCT / stride time | pressure | Walk/run classification |
| Foot-strike pattern | which part of the foot loads first: rearfoot (RFS), midfoot (MFS), forefoot (FFS) | pressure (regional) | Often classified by **strike index**: centre-of-pressure position at IC as % of foot length from the heel, split into thirds; commonly attributed to Cavanagh & Lafortune (1980) (verify and cite) |
| Centre of pressure (CoP) path | force-weighted mean of sensor positions over stance | pressure array | Accuracy is limited by sensor count and coverage |
| Regional loading | peak or impulse (force-time integral) per region (heel, midfoot, forefoot, hallux) | pressure | Relative, unless calibrated |
| Loading-rate proxy | slope of rising force after IC | pressure | Classic loading rate needs vertical GRF from a force plate; an insole proxy is not equivalent. Say so |
| Left/right symmetry | SI = (R − L) / (0.5 (R + L)) × 100 % | both insoles | One common formulation, often attributed to Robinson et al. (1987) (verify). State the formula used |
| Foot angles at IC, pronation proxies | from gyroscope/accelerometer orientation | IMU | Sensitive to mounting and calibration; experimental |
| Speed / stride length | foot-mounted inertial navigation with zero-velocity updates during stance | IMU | Drift-prone; compare with the treadmill speed |

## Sampling-rate reasoning

At 100 Hz the sample period is 10 ms, which is several percent of a 200 ms contact. That error
lands on both IC and TO. Timing metrics therefore usually want ≥ 200 Hz per channel (verify against
the literature and the approved base project). IMUs for foot impacts are often sampled faster.
Always report the **achieved** rate and jitter, not just the configured one.

## Gait-event detection approaches

1. **Pressure threshold with hysteresis**: sum the normalised channels; IC when the sum rises above
   threshold T_on, TO when it falls below T_off (< T_on). Enforce minimum stance and swing durations
   to reject bounce. Tune T relative to the per-session baseline.
2. **Regional**: IC from the first region to load (gives the strike pattern too); TO from the last
   region to unload (usually hallux or forefoot).
3. **IMU-based**: impact acceleration spikes near IC; patterns in sagittal-plane gyroscope angular
   velocity around TO. Useful when pressure saturates, or as a cross-check.
4. **Learned models**: only with labelled data. Evaluate them on held-out participants and
   sessions, never on the training sessions.

Edge cases to test: walking ↔ running transitions, turns, stopping and standing, stairs, sensor
saturation, a dropped BLE packet, clock drift between left and right.

## Pressure-sensor (FSR and piezoresistive) limitations to always state

- Non-linear response: resistance falls roughly inversely with force, while conductance is closer
  to linear over part of the range. This needs calibration.
- Hysteresis (loading ≠ unloading), creep/drift under sustained load, temperature and humidity
  dependence, and sensitivity to how load is applied (area, bending, shear).
- Discrete sensors cover only part of the plantar surface, so total force is underestimated and the
  CoP is coarse.
- Durability: running loads repeated thousands of times per session cause degradation. Plan
  re-calibration.

## Signal processing defaults (adjust with evidence)

- Low-pass filter with a zero-phase Butterworth (`scipy.signal.filtfilt`), offline only. Real-time
  filters are causal and add delay: document it.
- Resample to a common timeline before fusing pressure and IMU. Keep the original timestamps.
- Synchronise devices with a shared event, e.g. three sharp foot stamps visible in insole, IMU and
  video.

## Validation statistics

- Reference hierarchy: force plate / instrumented treadmill (gold; not available to us) >
  high-speed video at 240 fps, about 4 ms per frame, which is good for IC/TO timing > consumer
  watch/foot-pod metrics. Those have their own errors, so we report **agreement**, not accuracy.
- Report: **Bland–Altman** bias and 95 % limits of agreement (bias ± 1.96 SD of the differences),
  **MAE** (and MAPE where meaningful), **ICC** with its model stated. Correlation (r) alone is not
  agreement.
- Report per speed, per participant (n = 1 here: say so) and per foot. Pre-register the analysis in
  `validation/plan.md` before collecting data.

## Injury-risk language

Research links some running-gait variables (e.g. loading rates, cadence, step-to-step asymmetry) to
injury risk. The evidence is **mixed and mostly associational**. Write "associated with", "some
studies suggest", "evidence is mixed", and cite the studies. Never write "prevents", "reduces your
risk" or "diagnoses". The product gives awareness of how you run, not medical advice.
