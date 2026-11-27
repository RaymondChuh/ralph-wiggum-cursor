---
name: data-handling
description: Rules for recordings and datasets in the smart-insole project. Raw/sample/public data tiers, de-identification checklist, dataset cards, file formats and naming, third-party dataset licences. Use whenever capturing, storing, committing, sharing or plotting data.
user-invocable: false
---

# Data handling

## Three tiers

| Folder | Contents | In git? |
|---|---|---|
| `data/raw/` | The human's own recordings: insole logs, watch exports, phone video, HIL captures | **Never** (gitignored; a guard hook blocks commits) |
| `data/samples/` | Small, de-identified excerpts for tutorial readers, each with a dataset card | Yes |
| `data/public/` | Third-party datasets downloaded by `scripts/data/fetch_*.py` | No (gitignored cache); commit the fetch script, not the data |

## De-identification checklist (raw → samples)

- [ ] Trim to the minimum needed (e.g. 30–60 s per condition). Target < 5 MB per file.
- [ ] Remove names, emails, device names, Bluetooth MAC addresses, serial numbers, watch account ids.
- [ ] Replace absolute timestamps with relative time (`t_s` from 0). Remove dates and time zones.
- [ ] Remove GPS and location entirely. Treadmill speed is fine.
- [ ] No video frames with faces, home interiors or identifying surroundings. If a frame is
      needed, crop it to the shoe and treadmill belt.
- [ ] Round or omit body measurements (weight, height, shoe size) unless needed; if needed, bucket
      them (e.g. "70–80 kg").
- [ ] Write the dataset card. The human approves the first sample dataset at a review (mention it
      in the journal).

## Dataset card (`data/samples/<name>/README.md`)

Name, purpose, how it was recorded (hardware revision, firmware version, sample rate, sensor layout
reference), conditions (speeds, surface, footwear type), columns with units, known issues, licence
(**CC BY 4.0**, same as the docs), and a statement that it is de-identified and contains one adult
volunteer (the project author) who consented to publication.

## Formats and naming

- Tabular time series: CSV for small files (header row, SI units in the column names, e.g.
  `t_s, heel_l_raw, heel_l_N, acc_x_ms2`), Parquet for large ones. A sidecar `*.meta.json` carries
  the sample rate, firmware version, calibration model id and channel map.
- Names: `<date-or-session-id>_<condition>_<side>.csv`, e.g. `s03_treadmill-10kmh_left.csv`.
  Use session ids in samples, never dates.
- Store raw ADC counts **and** calibrated values (with the calibration model version). Never
  overwrite raw data.

## Third-party datasets

- Record the licence and access terms in `research/sources.yaml` before downloading.
- Credentialed datasets (e.g. some PhysioNet datasets): the human must register and accept the terms
  personally. Agents explain how; they do not bypass it.
- Redistribute (commit or excerpt) only if the licence allows it, with attribution in the dataset
  card and in `docs/reference/sources.md`.
