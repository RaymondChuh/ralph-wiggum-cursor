#!/usr/bin/env python3
"""Smart-insoles harness state tool. Standard library only (Python 3.9+).

The harness keeps all project state in files (Ralph-style), never in an agent's
context window. This tool reads that state and answers one question reliably:
"what is the single next thing to do?"

State files (paths relative to the harness root):
  state/workflow.json          phases and gates (static definition)
  state/backlog.md             tasks as `- [ ] P1-01 ...  <!-- owner: x; after: G1; hil: true -->`
  state/gates/<GATE>.md        gate request packets written by agents (frontmatter: gate, revision)
  state/hil/<TASK>.md          hardware-in-the-loop instructions written by agents (frontmatter: task, revision)
  state/gates/decisions.jsonl  HUMAN decisions, appended only by the UserPromptSubmit hook

Commands:
  status [--brief]        project overview (phases, gates, HIL, next action)
  next [--json]           the single next action for the orchestrator
  gates                   gate + HIL status table
  open-gate GATE_ID       create a gate request from the template, or bump its revision after a rejection
  open-hil TASK_ID        create a HIL request from the template, or bump its revision after a failure
  devlog TITLE [--phase P] create a dated build-journal entry from the template and print its path
  validate                consistency checks over the whole harness; exit 1 on errors
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

PHASE_RE = re.compile(r"^##\s+(P\d+)\b(.*)$")
TASK_RE = re.compile(
    r"^\s*-\s+\[(?P<mark>[ xX])\]\s+(?P<id>P\d+-\d+)\s+(?P<text>.*?)\s*(?:<!--(?P<ann>.*?)-->)?\s*$"
)
LOOSE_TASK_RE = re.compile(r"^\s*-\s+\[[ xX]\]\s+")
VALID_SOURCE_STATUS = {"candidate", "shortlisted", "approved", "rejected", "reference"}
VALID_SOURCE_TYPES = {"repo", "paper", "dataset", "product", "standard", "web", "book"}


# --------------------------------------------------------------------------- model


@dataclass
class Task:
    id: str
    phase: str
    text: str
    done: bool
    owner: str = "lead"
    after: List[str] = field(default_factory=list)
    hil: bool = False
    line: int = 0

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "phase": self.phase,
            "text": self.text,
            "done": self.done,
            "owner": self.owner,
            "after": self.after,
            "hil": self.hil,
        }


def parse_frontmatter(path: Path) -> Dict[str, str]:
    """Minimal `key: value` frontmatter parser (no nesting needed here)."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta: Dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def set_frontmatter_value(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} has no frontmatter")
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            lines.insert(i, f"{key}: {value}")
            break
        if line.split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {value}"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def today() -> str:
    return _dt.date.today().isoformat()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


class Harness:
    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root or os.environ.get("INSOLES_ROOT") or DEFAULT_ROOT).resolve()
        self.state = self.root / "state"
        self.workflow_path = self.state / "workflow.json"
        self.backlog_path = self.state / "backlog.md"
        self.gates_dir = self.state / "gates"
        self.hil_dir = self.state / "hil"
        self.decisions_path = self.gates_dir / "decisions.jsonl"
        self.templates = self.state / "templates"
        self.journal_dir = self.root / "docs" / "journal"
        self._workflow: Optional[dict] = None

    # ------------------------------------------------------------------ loading

    @property
    def workflow(self) -> dict:
        if self._workflow is None:
            self._workflow = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        return self._workflow

    @property
    def phases(self) -> List[dict]:
        return self.workflow["phases"]

    @property
    def gate_defs(self) -> Dict[str, dict]:
        return {g["id"]: g for g in self.workflow["gates"]}

    def tasks(self) -> List[Task]:
        tasks: List[Task] = []
        phase = None
        for n, line in enumerate(self.backlog_path.read_text(encoding="utf-8").splitlines(), 1):
            pm = PHASE_RE.match(line)
            if pm:
                phase = pm.group(1)
                continue
            tm = TASK_RE.match(line)
            if not tm:
                continue
            ann = parse_annotation(tm.group("ann") or "")
            tasks.append(
                Task(
                    id=tm.group("id"),
                    phase=phase or "?",
                    text=tm.group("text").strip(),
                    done=tm.group("mark").lower() == "x",
                    owner=ann.get("owner", "lead"),
                    after=[g.strip().upper() for g in ann.get("after", "").split(",") if g.strip()],
                    hil=ann.get("hil", "false").lower() in {"true", "yes", "1"},
                    line=n,
                )
            )
        return tasks

    def decisions(self) -> List[dict]:
        if not self.decisions_path.exists():
            return []
        out = []
        for line in self.decisions_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    # ------------------------------------------------------------------ gates / HIL

    def gate_file(self, gate_id: str) -> Path:
        return self.gates_dir / f"{gate_id}.md"

    def hil_file(self, task_id: str) -> Path:
        return self.hil_dir / f"{task_id}.md"

    def _request_status(self, kind: str, item_id: str, path: Path) -> Tuple[str, Optional[dict], int]:
        """Return (status, latest_decision_for_current_revision, revision)."""
        if not path.exists():
            return ("not_requested" if kind == "gate" else "not_prepared", None, 0)
        try:
            revision = int(parse_frontmatter(path).get("revision", "1"))
        except ValueError:
            revision = 1
        matching = [
            d
            for d in self.decisions()
            if d.get("kind") == kind and d.get("id") == item_id and int(d.get("revision", 1)) == revision
        ]
        if not matching:
            return ("pending" if kind == "gate" else "waiting", None, revision)
        latest = matching[-1]
        return (latest["decision"], latest, revision)

    def gate_status(self, gate_id: str) -> Tuple[str, Optional[dict], int]:
        return self._request_status("gate", gate_id, self.gate_file(gate_id))

    def hil_status(self, task_id: str) -> Tuple[str, Optional[dict], int]:
        return self._request_status("hil", task_id, self.hil_file(task_id))

    def gate_options(self, gate_id: str) -> List[str]:
        meta = parse_frontmatter(self.gate_file(gate_id))
        raw = meta.get("options", "")
        return [o.strip() for o in raw.split(",") if o.strip()]

    def phase_requirement(self, phase: dict) -> str:
        """'ok' | 'skip' | 'wait' for phases with a `requires` clause."""
        req = phase.get("requires")
        if not req:
            return "ok"
        status, decision, _ = self.gate_status(req["gate"])
        if status != "approved":
            return "wait"
        if req.get("option") and (decision or {}).get("option", "").lower() != req["option"].lower():
            return "skip"
        return "ok"

    # ------------------------------------------------------------------ next action

    def next_action(self) -> dict:
        tasks = self.tasks()
        by_phase: Dict[str, List[Task]] = {}
        for t in tasks:
            by_phase.setdefault(t.phase, []).append(t)

        for phase in self.phases:
            pid = phase["id"]
            req = self.phase_requirement(phase)
            if req == "skip":
                continue
            if req == "wait":
                return self._gate_action(phase["requires"]["gate"], phase, reason="phase prerequisite")

            phase_tasks = by_phase.get(pid, [])
            blocking_gates: List[str] = []
            for t in phase_tasks:
                if t.done:
                    continue
                unmet = [g for g in t.after if self.gate_status(g)[0] != "approved"]
                if unmet:
                    for g in unmet:
                        if g not in blocking_gates:
                            blocking_gates.append(g)
                    continue
                if t.hil:
                    status, decision, rev = self.hil_status(t.id)
                    if status == "not_prepared":
                        return self._task_action(t, phase, "prepare_hil")
                    if status == "waiting":
                        return {
                            "kind": "wait_hil",
                            "phase": pid,
                            "task": t.as_dict(),
                            "request": self._rel(self.hil_file(t.id)),
                            "revision": rev,
                            "message": (
                                f"Waiting on YOU for hardware step {t.id}: follow "
                                f"{self._rel(self.hil_file(t.id))}, then type `/hil-done {t.id} [notes]` "
                                f"or `/hil-failed {t.id} <what happened>`."
                            ),
                        }
                    if status == "failed":
                        return self._task_action(t, phase, "fix_hil", decision)
                    return self._task_action(t, phase, "verify_hil", decision)
                return self._task_action(t, phase, "do")

            if blocking_gates:
                return self._gate_action(blocking_gates[0], phase, reason="tasks wait on this gate")
            exit_gate = phase.get("exit_gate")
            if exit_gate and self.gate_status(exit_gate)[0] != "approved":
                return self._gate_action(exit_gate, phase, reason="phase exit gate")
        return {"kind": "done", "message": "All phases complete (or skipped by gate decisions)."}

    def _task_action(self, t: Task, phase: dict, mode: str, decision: Optional[dict] = None) -> dict:
        hints = {
            "do": f"Delegate {t.id} to `{t.owner}` (see CLAUDE.md session protocol).",
            "prepare_hil": (
                f"{t.id} needs a physical step by the human. Have `{t.owner}` write the HIL request with "
                f"`python3 scripts/harness.py open-hil {t.id}` (follow the hardware-in-the-loop skill), then stop."
            ),
            "verify_hil": (
                f"The human reported {t.id} done. Have `{t.owner}` verify the evidence (logs/data/notes) "
                f"before ticking the task."
            ),
            "fix_hil": (
                f"The human reported {t.id} FAILED. Have `{t.owner}` troubleshoot from their notes, revise the "
                f"instructions with `python3 scripts/harness.py open-hil {t.id}` (bumps revision), then stop."
            ),
        }
        out = {
            "kind": "task",
            "mode": mode,
            "phase": phase["id"],
            "phase_name": phase["name"],
            "task": t.as_dict(),
            "message": hints[mode],
        }
        if decision:
            out["human_notes"] = decision.get("notes", "")
        return out

    def _gate_action(self, gate_id: str, phase: dict, reason: str) -> dict:
        status, decision, rev = self.gate_status(gate_id)
        gdef = self.gate_defs.get(gate_id, {})
        base = {"phase": phase["id"], "gate": gate_id, "gate_name": gdef.get("name", ""), "reason": reason}
        if status == "not_requested":
            return {
                **base,
                "kind": "prepare_gate",
                "message": (
                    f"Gate {gate_id} ({gdef.get('name', '')}) has not been requested. Finish the gate-prep task, "
                    f"or run `python3 scripts/harness.py open-gate {gate_id}` and fill in the request."
                ),
            }
        if status == "pending":
            opts = self.gate_options(gate_id)
            opt_hint = f" <option: {'|'.join(opts)}>" if opts else " [option]"
            return {
                **base,
                "kind": "wait_gate",
                "request": self._rel(self.gate_file(gate_id)),
                "revision": rev,
                "message": (
                    f"Waiting on YOU: gate {gate_id} ({gdef.get('name', '')}), revision {rev}. Read "
                    f"{self._rel(self.gate_file(gate_id))}, then type `/approve {gate_id}{opt_hint} [notes]` "
                    f"or `/reject {gate_id} <why>`."
                ),
            }
        if status == "rejected":
            return {
                **base,
                "kind": "revise_gate",
                "request": self._rel(self.gate_file(gate_id)),
                "revision": rev,
                "human_notes": (decision or {}).get("notes", ""),
                "message": (
                    f"Gate {gate_id} revision {rev} was REJECTED. Rework per the human's notes (add or re-open "
                    f"tasks in state/backlog.md), then `python3 scripts/harness.py open-gate {gate_id}` to submit "
                    f"revision {rev + 1}."
                ),
            }
        # approved but something still blocked: shouldn't happen, report clearly.
        return {**base, "kind": "blocked", "message": f"Gate {gate_id} is approved but work is still blocked."}

    # ------------------------------------------------------------------ creation helpers

    def _render_template(self, name: str, mapping: Dict[str, str]) -> str:
        text = (self.templates / name).read_text(encoding="utf-8")
        for key, value in mapping.items():
            text = text.replace("{{" + key + "}}", value)
        return text

    def open_gate(self, gate_id: str) -> str:
        gate_id = gate_id.upper()
        gdef = self.gate_defs.get(gate_id)
        if not gdef:
            raise SystemExit(f"Unknown gate {gate_id}. Known: {', '.join(self.gate_defs)}")
        path = self.gate_file(gate_id)
        status, _, rev = self.gate_status(gate_id)
        if status == "not_requested":
            self.gates_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(
                self._render_template(
                    "gate-request.md",
                    {
                        "GATE": gate_id,
                        "NAME": gdef["name"],
                        "QUESTION": gdef["question"],
                        "OPTIONS": ", ".join(gdef.get("required_options", [])),
                        "DATE": today(),
                    },
                ),
                encoding="utf-8",
            )
            return f"Created {self._rel(path)} (revision 1). Fill it in; the human decides with /approve or /reject."
        if status == "rejected":
            set_frontmatter_value(path, "revision", str(rev + 1))
            set_frontmatter_value(path, "updated", today())
            return (
                f"Bumped {self._rel(path)} to revision {rev + 1}. Update the packet (add a 'Changes since "
                f"revision {rev}' section) before ending the session."
            )
        if status == "pending":
            return f"{self._rel(path)} revision {rev} is already pending a human decision."
        raise SystemExit(f"Gate {gate_id} is already approved (revision {rev}); nothing to open.")

    def open_hil(self, task_id: str) -> str:
        task_id = task_id.upper()
        task = next((t for t in self.tasks() if t.id == task_id), None)
        if task is None:
            raise SystemExit(f"No task {task_id} in state/backlog.md")
        if not task.hil:
            raise SystemExit(f"Task {task_id} is not marked `hil: true` in state/backlog.md")
        path = self.hil_file(task_id)
        status, _, rev = self.hil_status(task_id)
        if status == "not_prepared":
            self.hil_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(
                self._render_template(
                    "hil-request.md", {"TASK": task_id, "TITLE": task.text, "OWNER": task.owner, "DATE": today()}
                ),
                encoding="utf-8",
            )
            return f"Created {self._rel(path)} (revision 1). Fill it in, then stop and hand over to the human."
        if status == "failed":
            set_frontmatter_value(path, "revision", str(rev + 1))
            set_frontmatter_value(path, "updated", today())
            return f"Bumped {self._rel(path)} to revision {rev + 1}. Revise the steps using the failure notes."
        if status == "waiting":
            return f"{self._rel(path)} revision {rev} is already waiting on the human."
        raise SystemExit(f"HIL step {task_id} is already marked done (revision {rev}).")

    def new_devlog(self, title: str, phase: str = "") -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "entry"
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        base = f"{today()}-{slug}"
        path = self.journal_dir / f"{base}.md"
        n = 2
        while path.exists():
            path = self.journal_dir / f"{base}-{n}.md"
            n += 1
        path.write_text(
            self._render_template("devlog-entry.md", {"TITLE": title, "PHASE": phase or "?", "DATE": today()}),
            encoding="utf-8",
        )
        return self._rel(path)

    # ------------------------------------------------------------------ validation

    def validate(self) -> Tuple[List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        # workflow
        try:
            phases = self.phases
            gates = self.gate_defs
        except Exception as exc:  # noqa: BLE001
            return ([f"state/workflow.json unreadable: {exc}"], [])
        phase_ids = [p["id"] for p in phases]
        if len(set(phase_ids)) != len(phase_ids):
            errors.append("workflow.json: duplicate phase ids")
        for p in phases:
            g = p.get("exit_gate")
            if g and g not in gates:
                errors.append(f"workflow.json: phase {p['id']} exit_gate {g} is not a defined gate")
            req = p.get("requires")
            if req and req.get("gate") not in gates:
                errors.append(f"workflow.json: phase {p['id']} requires unknown gate {req.get('gate')}")

        # agents and skills
        agents_dir = self.root / ".claude" / "agents"
        agent_names = set()
        for f in sorted(agents_dir.glob("*.md")):
            meta = parse_frontmatter(f)
            if not meta.get("name") or not meta.get("description"):
                errors.append(f"{self._rel(f)}: frontmatter needs name and description")
            else:
                agent_names.add(meta["name"])
                if meta["name"] != f.stem:
                    warnings.append(f"{self._rel(f)}: name '{meta['name']}' differs from filename")
        skills_dir = self.root / ".claude" / "skills"
        skill_names = set()
        for f in sorted(skills_dir.glob("*/SKILL.md")):
            meta = parse_frontmatter(f)
            if not meta.get("description"):
                errors.append(f"{self._rel(f)}: frontmatter needs a description")
            skill_names.add(meta.get("name") or f.parent.name)
        for f in sorted(agents_dir.glob("*.md")):
            for skill in _yaml_list_field(f, "skills"):
                if skill not in skill_names:
                    errors.append(f"{self._rel(f)}: preloads unknown skill '{skill}'")
        for p in phases:
            lead = p.get("lead")
            if lead and lead not in agent_names:
                errors.append(f"workflow.json: phase {p['id']} lead '{lead}' has no agent file")

        # backlog
        try:
            tasks = self.tasks()
        except FileNotFoundError:
            errors.append("state/backlog.md missing")
            tasks = []
        seen = set()
        for t in tasks:
            if t.id in seen:
                errors.append(f"backlog.md:{t.line}: duplicate task id {t.id}")
            seen.add(t.id)
            if not t.id.startswith(t.phase + "-"):
                errors.append(f"backlog.md:{t.line}: task {t.id} sits under phase {t.phase}")
            if t.phase not in phase_ids:
                errors.append(f"backlog.md:{t.line}: unknown phase {t.phase}")
            if t.owner != "lead" and t.owner not in agent_names:
                errors.append(f"backlog.md:{t.line}: owner '{t.owner}' has no agent file")
            for g in t.after:
                if g not in gates:
                    errors.append(f"backlog.md:{t.line}: task {t.id} waits on unknown gate {g}")
            if t.done and t.hil and self.hil_status(t.id)[0] != "done":
                errors.append(
                    f"backlog.md:{t.line}: HIL task {t.id} is ticked but no human /hil-done is recorded"
                )
        for n, line in enumerate(self.backlog_path.read_text(encoding="utf-8").splitlines(), 1):
            if LOOSE_TASK_RE.match(line) and not TASK_RE.match(line):
                errors.append(f"backlog.md:{n}: checkbox line without a task id like P1-01")

        # gates ticked off before approval?
        for p in phases:
            g = p.get("exit_gate")
            if not g:
                continue
            later = [t for t in tasks if _phase_index(phase_ids, t.phase) > _phase_index(phase_ids, p["id"])]
            if any(t.done for t in later if t.phase != p["id"]) and self.gate_status(g)[0] != "approved":
                warnings.append(f"Tasks after {p['id']} are ticked but exit gate {g} is not approved")

        # gate and HIL request files
        for f in sorted(self.gates_dir.glob("*.md")):
            if f.name.upper() == "README.MD":
                continue
            meta = parse_frontmatter(f)
            gid = meta.get("gate", "")
            if gid != f.stem:
                errors.append(f"{self._rel(f)}: frontmatter gate '{gid}' must match filename")
            if gid in gates:
                required = gates[gid].get("required_options", [])
                opts = [o.strip() for o in meta.get("options", "").split(",") if o.strip()]
                missing = [o for o in required if o not in opts]
                if missing:
                    errors.append(f"{self._rel(f)}: options must include {', '.join(missing)}")
            if not meta.get("revision", "").isdigit():
                errors.append(f"{self._rel(f)}: frontmatter revision must be an integer")
        for f in sorted(self.hil_dir.glob("*.md")) if self.hil_dir.exists() else []:
            if f.name.upper() == "README.MD":
                continue
            meta = parse_frontmatter(f)
            if meta.get("task") != f.stem:
                errors.append(f"{self._rel(f)}: frontmatter task must match filename")
            if not meta.get("revision", "").isdigit():
                errors.append(f"{self._rel(f)}: frontmatter revision must be an integer")

        # decisions
        try:
            for i, d in enumerate(self.decisions(), 1):
                for key in ("ts", "kind", "id", "decision", "revision", "source"):
                    if key not in d:
                        errors.append(f"decisions.jsonl line {i}: missing '{key}'")
                if d.get("kind") == "gate" and d.get("id") not in gates:
                    errors.append(f"decisions.jsonl line {i}: unknown gate {d.get('id')}")
                if d.get("source") != "UserPromptSubmit hook":
                    errors.append(f"decisions.jsonl line {i}: not written by the human-decision hook")
        except json.JSONDecodeError as exc:
            errors.append(f"decisions.jsonl is not valid JSON lines: {exc}")

        # sources registry
        sources = self.root / "research" / "sources.yaml"
        if sources.exists():
            try:
                import yaml  # type: ignore

                data = yaml.safe_load(sources.read_text(encoding="utf-8")) or {}
                entries = data.get("sources") or []
                ids = set()
                for i, s in enumerate(entries):
                    sid = s.get("id", f"#{i}")
                    for key in ("id", "type", "title", "url", "license", "status"):
                        if not s.get(key):
                            errors.append(f"sources.yaml {sid}: missing '{key}'")
                    if sid in ids:
                        errors.append(f"sources.yaml: duplicate id {sid}")
                    ids.add(sid)
                    if s.get("status") and s["status"] not in VALID_SOURCE_STATUS:
                        errors.append(f"sources.yaml {sid}: status must be one of {sorted(VALID_SOURCE_STATUS)}")
                    if s.get("type") and s["type"] not in VALID_SOURCE_TYPES:
                        errors.append(f"sources.yaml {sid}: type must be one of {sorted(VALID_SOURCE_TYPES)}")
            except ImportError:
                warnings.append("PyYAML not installed; skipped research/sources.yaml checks")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"research/sources.yaml unreadable: {exc}")

        # personal data must stay out of git
        gitignore = self.root / ".gitignore"
        if not gitignore.exists() or "data/raw/" not in gitignore.read_text(encoding="utf-8"):
            errors.append(".gitignore must ignore data/raw/ (personal recordings)")
        return errors, warnings

    # ------------------------------------------------------------------ reporting

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def status_lines(self, brief: bool = False) -> List[str]:
        tasks = self.tasks()
        nxt = self.next_action()
        lines: List[str] = []
        if not brief:
            lines.append("Smart Insoles harness: project status")
            lines.append("")
            lines.append(f"{'Phase':<64} {'Tasks':>7}  Gate")
        current_phase = nxt.get("phase")
        for p in self.phases:
            pt = [t for t in tasks if t.phase == p["id"]]
            done = sum(t.done for t in pt)
            gate = p.get("exit_gate")
            gate_txt = f"{gate} {self.gate_status(gate)[0]}" if gate else "-"
            req = self.phase_requirement(p)
            marker = ">" if p["id"] == current_phase else " "
            label = f"{marker} {p['id']} {p['name']}"
            if req == "skip":
                gate_txt = "skipped (by G4 decision)"
            if brief:
                if p["id"] == current_phase:
                    lines.append(f"Current phase: {p['id']} {p['name']} ({done}/{len(pt)} tasks)")
            else:
                lines.append(f"{label[:64]:<64} {done:>3}/{len(pt):<3}  {gate_txt}")
        pending_gates = [g for g in self.gate_defs if self.gate_status(g)[0] == "pending"]
        waiting_hil = [t.id for t in tasks if t.hil and not t.done and self.hil_status(t.id)[0] == "waiting"]
        if not brief:
            lines.append("")
        if pending_gates:
            lines.append("Gates waiting on the human: " + ", ".join(pending_gates))
        if waiting_hil:
            lines.append("Hardware steps waiting on the human: " + ", ".join(waiting_hil))
        recent = self.decisions()[-3:]
        if recent and not brief:
            lines.append("Recent human decisions:")
            for d in recent:
                opt = f" option={d['option']}" if d.get("option") else ""
                lines.append(f"  {d['ts'][:10]} {d['kind']} {d['id']} r{d['revision']} {d['decision']}{opt}")
        guardrails = self.state / "guardrails.md"
        if guardrails.exists():
            signs = len(re.findall(r"^### Sign:", guardrails.read_text(encoding="utf-8"), re.M))
            lines.append(f"Guardrails: {signs} signs in state/guardrails.md (read before working)")
        lines.append(f"NEXT [{nxt['kind']}{'/' + nxt['mode'] if nxt.get('mode') else ''}]: "
                     + (f"{nxt['task']['id']} {nxt['task']['text']} -> " if nxt.get("task") else "")
                     + nxt["message"])
        return lines


# --------------------------------------------------------------------------- helpers


def parse_annotation(raw: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in raw.split(";"):
        if ":" in part:
            key, _, value = part.partition(":")
            out[key.strip().lower()] = value.strip()
    return out


def _phase_index(ids: List[str], pid: str) -> int:
    return ids.index(pid) if pid in ids else -1


def _yaml_list_field(path: Path, key: str) -> List[str]:
    """Read a simple YAML list (`key:\\n  - a\\n  - b` or `key: a, b`) from frontmatter."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    out: List[str] = []
    collecting = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if collecting:
            m = re.match(r"^\s+-\s+(.+)$", line)
            if m:
                out.append(m.group(1).strip())
                continue
            collecting = False
        if line.startswith(f"{key}:"):
            rest = line.split(":", 1)[1].strip()
            if rest:
                out.extend(x.strip() for x in rest.strip("[]").split(",") if x.strip())
            else:
                collecting = True
    return out


# --------------------------------------------------------------------------- CLI


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None, help="harness root (default: this script's parent)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_status = sub.add_parser("status")
    p_status.add_argument("--brief", action="store_true")
    p_next = sub.add_parser("next")
    p_next.add_argument("--json", action="store_true")
    sub.add_parser("gates")
    p_og = sub.add_parser("open-gate")
    p_og.add_argument("gate_id")
    p_oh = sub.add_parser("open-hil")
    p_oh.add_argument("task_id")
    p_dl = sub.add_parser("devlog")
    p_dl.add_argument("title")
    p_dl.add_argument("--phase", default="")
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    h = Harness(args.root)

    if args.cmd == "status":
        print("\n".join(h.status_lines(brief=args.brief)))
    elif args.cmd == "next":
        nxt = h.next_action()
        if args.json:
            print(json.dumps(nxt, indent=2))
        else:
            print(f"[{nxt['kind']}{'/' + nxt['mode'] if nxt.get('mode') else ''}]")
            if nxt.get("task"):
                t = nxt["task"]
                print(f"task:  {t['id']} {t['text']}")
                print(f"owner: {t['owner']}   phase: {nxt['phase']} {nxt.get('phase_name', '')}")
            if nxt.get("gate"):
                print(f"gate:  {nxt['gate']} {nxt.get('gate_name', '')} ({nxt.get('reason', '')})")
            if nxt.get("human_notes"):
                print(f"human notes: {nxt['human_notes']}")
            print(nxt["message"])
    elif args.cmd == "gates":
        print(f"{'Gate':<5} {'Status':<14} {'Rev':>3}  Name")
        for gid, g in h.gate_defs.items():
            status, decision, rev = h.gate_status(gid)
            opt = f" (option {decision['option']})" if decision and decision.get("option") else ""
            print(f"{gid:<5} {status:<14} {rev:>3}  {g['name']}{opt}")
        hil_tasks = [t for t in h.tasks() if t.hil]
        if hil_tasks:
            print()
            print(f"{'HIL':<7} {'Status':<14} {'Rev':>3}  Task")
            for t in hil_tasks:
                status, _, rev = h.hil_status(t.id)
                print(f"{t.id:<7} {status:<14} {rev:>3}  {t.text}")
    elif args.cmd == "open-gate":
        print(h.open_gate(args.gate_id))
    elif args.cmd == "open-hil":
        print(h.open_hil(args.task_id))
    elif args.cmd == "devlog":
        print(h.new_devlog(args.title, args.phase))
    elif args.cmd == "validate":
        errors, warnings = h.validate()
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        print(f"validate: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
