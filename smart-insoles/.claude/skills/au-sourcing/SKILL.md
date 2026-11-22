---
name: au-sourcing
description: Buying electronics parts for the smart-insole project from Australia. Supplier list, AUD/GST conventions, price-verification rules, BOM tiering and CSV columns. Use when creating or updating a BOM or recommending parts.
user-invocable: false
---

# Sourcing parts in Australia

## Suppliers (check stock and price live; this list is a starting point)

| Supplier | Good for | Notes |
|---|---|---|
| Core Electronics (core-electronics.com.au) | Dev boards, Adafruit/SparkFun/Pimoroni breakouts, sensors, tools | Australian stock, fast shipping, beginner-friendly guides |
| Little Bird Electronics (littlebird.com.au) | Maker boards and breakouts | Australian retailer |
| Jaycar Electronics (jaycar.com.au) | Basic components, tools, same-day pickup | Physical stores nationwide; pricier for components |
| Altronics (altronics.com.au) | Components, tools | Perth-based, ships nationally |
| element14 / Farnell AU (au.element14.com) | Exact manufacturer parts | Distributor; good for stage 2 |
| DigiKey AU (digikey.com.au) | Exact manufacturer parts, huge range | Ships from the US; free shipping above a threshold (check) |
| Mouser AU (au.mouser.com) | Exact manufacturer parts | Ships from the US; similar to DigiKey |
| RS Australia (au.rs-online.com) | Components, tools | Distributor |
| AliExpress | Cheap FSRs, velostat, modules | 2–6+ week delivery, variable quality and counterfeits; buy spares; budget tier only |
| JLCPCB / PCBWay (stage 2) | PCB fab + assembly, flex PCBs | Ship to AU; quote in USD, so convert to AUD with the date |

## Rules

- **Verify every line**: open the product page, record the SKU, the price in **AUD including GST**,
  stock status, and `price_checked: YYYY-MM-DD`. If you cannot verify a line, mark the price `est.`
  and say why.
- GST is 10 %. Overseas suppliers generally collect GST on low-value imports at checkout. Include
  shipping as its own line per supplier.
- Prefer **one or two suppliers per tier** to cut shipping costs and complexity. Prefer local stock
  for the critical path; AliExpress only for cheap consumables or spares, and never for the battery
  or charger.
- Always include what a software developer may not own: soldering iron and stand, solder, flux,
  multimeter, flush cutters, wire strippers, heat-shrink, header pins, breadboard, jumper wires,
  USB cable (data-capable), safety glasses. Mark items as "tools (one-off)" versus "per insole".
- Buy spares of fragile parts (FSRs, thin wire, connectors): typically +50 % or at least 2 extra.
- Two insoles (left and right) means two sets of sensors. State whether the tier builds one
  insole or a pair.

## BOM CSV columns

`tier, ref, part, qty, supplier, supplier_sku, url, unit_aud, total_aud, price_checked, alt_supplier, category, notes`

Here `category` is `per-insole` | `per-pair` | `tools` | `consumables` | `shipping`. `bom.md` shows a
total per tier (parts, tools and shipping separately), the lead-time risk, and what each tier
upgrades (e.g. more pressure channels, a better IMU, nicer battery packaging).
