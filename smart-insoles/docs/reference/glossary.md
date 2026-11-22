# Glossary

Each entry is one or two sentences in plain English, with a software analogy where one helps.
The tutorial-writer adds a term whenever a chapter introduces it. Abbreviations also get a hover
tooltip via `docs/includes/abbreviations.md`.

## Body and running

### Cadence
Steps per minute (both feet counted). One of the most robust metrics an insole can estimate.

### Gait cycle
The repeating pattern of one leg's movement, from one foot strike to the next strike of the
**same** foot (one **stride**, which contains two **steps**). Think of it as a state machine that
loops: stance → swing → stance.

### Stance phase
The part of the gait cycle when the foot is on the ground, from **initial contact** to
**toe-off**.

### Swing phase
The part of the gait cycle when the foot is in the air.

### Flight phase
In running, the moments when **neither** foot touches the ground. Walking has none, because
walking always has a foot down.

### Ground contact time (GCT)
How long one foot stays on the ground during a step: toe-off time minus initial-contact time,
usually in milliseconds.

### Foot-strike pattern
Which part of the foot lands first: **rearfoot** (heel), **midfoot**, or **forefoot**.

### Plantar pressure
Pressure on the sole (plantar surface) of the foot. Insoles measure it at a few sensor locations.

## Electronics

### ADC
Analog-to-Digital Converter. Turns a voltage into an integer, many times per second, like
recording audio. Its resolution (e.g. 12-bit = 0–4095) and sample rate trade off the same way.

### FSR
Force-Sensitive Resistor. A thin sensor whose electrical resistance drops when pressed. Cheap and
flexible, but not precise: it needs calibration and drifts.

### IMU
Inertial Measurement Unit. A chip with an accelerometer (measures acceleration, including gravity)
and a gyroscope (measures rotation speed), sometimes a magnetometer too.

### Voltage divider
Two resistances in series that turn a changing resistance (like an FSR) into a changing voltage an
ADC can read.

### BLE
Bluetooth Low Energy. A low-power wireless protocol. Data is exposed as a small typed API (GATT)
that a phone or browser can read and subscribe to.

### LiPo
Lithium-polymer battery. Light and energy-dense, but dangerous if punctured, bent, shorted or
charged badly.

## Data and validation

### Bland–Altman analysis
A way to check whether two measurement methods agree: plot their differences against their means
and report the average difference (bias) and the range most differences fall within (limits of
agreement).
