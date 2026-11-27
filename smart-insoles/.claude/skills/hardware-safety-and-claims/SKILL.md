---
name: hardware-safety-and-claims
description: Safety rules for building and wearing the insole (lithium batteries, low-voltage wiring, skin contact, sweat, soldering, treadmill use) and the wellness-versus-medical-device claims boundary (Australia TGA, US FDA general wellness, EU MDR), with approved/forbidden phrasing. Use for hardware design, HIL instructions, product copy, tutorials and reviews.
user-invocable: false
---

# Hardware safety and claims

## Electrical and battery safety

- **Low voltage only.** Power comes from USB 5 V or a single lithium cell (about 3.0–4.2 V)
  through a regulator. Nothing mains-powered touches the project. For USB chargers and power
  supplies in Australia, use ones bearing the **RCM** (Regulatory Compliance Mark).
- **Lithium cells:**
  - use protected cells (with a protection circuit module), or boards with proper charge management;
  - charge with a dedicated charger IC at a sensible current, never by connecting directly to 5 V;
  - **never** put a cell under the foot or anywhere it is bent, crushed or punctured. It goes in a
    pod on the shoe, laces or ankle;
  - never charge while worn, and never charge unattended;
  - stop using any cell that is swollen, dented, hot, or smells sweet or solvent-like, and dispose
    of it at a battery recycling point (in Australia, B-cycle drop-off points).
- **No running while tethered.** Never run while the electronics are plugged into a laptop or wall
  charger. That creates a cable trip hazard and a mains-referenced path. For treadmill sessions,
  use battery power and wireless logging, or on-device logging.
- **Short circuits:** disconnect power before rewiring. Insulate exposed joints (heat-shrink).
  Keep the battery's leads from touching each other.
- **Skin and sweat:** no exposed conductors where they can touch skin. Encapsulate or laminate
  sensors and traces, because sweat is conductive and corrosive. Surfaces should stay near ambient
  temperature; any noticeable warmth means stop and investigate.
- **Mechanics:** strain-relieve wires where they cross flex points (the arch and toe break), route
  them away from pressure points, and avoid hard edges or bulges under the foot (blister risk).
- **Tools:** soldering irons run at roughly 300–400 °C. Use a stand, ventilate the fumes, wash your
  hands after handling solder (especially leaded solder), and wear eye protection when clipping
  leads.
- **Treadmill:** use the safety key/clip and start slowly. The human's safety beats data quality,
  always.

## Claims: wellness, not medicine

Regulators classify a product by its **intended purpose**, which is judged largely from claims in
labelling, documentation, apps and marketing. Claims to diagnose, prevent, monitor, treat or
alleviate a disease, injury or disability can make a product a **medical device** (in Australia:
TGA, Therapeutic Goods Act 1989 and the Medical Devices Regulations; in the US: FDA; in the EU:
MDR 2017/745). Low-risk general-wellness products are treated differently. For example, the FDA
has a "General Wellness: Policy for Low Risk Devices" guidance. **Rules change. Before asserting
specifics, check the current guidance on tga.gov.au / fda.gov and cite the page and date.**

| ✅ Use | ❌ Avoid |
|---|---|
| "Estimate your cadence and ground contact time" | "Prevents running injuries" |
| "See how your foot-strike pattern changes with speed" | "Diagnoses overpronation / plantar fasciitis" |
| "Compare left and right loading" | "Detects injury risk" / "medical-grade" |
| "Some studies associate X with injury; evidence is mixed" | "Clinically proven" (unless we validated it clinically, which we won't) |
| "For training insight; not medical advice" | "Treats", "rehabilitates", "corrects gait" |

Every user-facing surface (README, dashboard, tutorials, notebooks) carries the disclaimer in
`docs/start-here/safety-and-disclaimer.md`.

## Privacy

Gait data from a named person is health-related personal information. Australia's Privacy Act
treats health information as sensitive information. Follow the `data-handling` skill. In
screenshots and photos: no faces, no location, no device serial numbers or Bluetooth MAC addresses.
