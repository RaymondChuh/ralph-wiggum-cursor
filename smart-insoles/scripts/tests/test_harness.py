"""Tests for the harness state machine and hooks. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HARNESS_ROOT / "scripts"))

from harness import Harness  # noqa: E402


def make_root() -> Path:
    """Copy the harness skeleton into a temp dir so tests never touch real state."""
    tmp = Path(tempfile.mkdtemp(prefix="insoles-test-"))
    for rel in ["state", ".claude", "research"]:
        shutil.copytree(HARNESS_ROOT / rel, tmp / rel)
    (tmp / "scripts").mkdir()
    shutil.copy(HARNESS_ROOT / "scripts" / "harness.py", tmp / "scripts" / "harness.py")
    shutil.copy(HARNESS_ROOT / ".gitignore", tmp / ".gitignore")
    for p in (tmp / "state" / "gates").glob("G*.md"):
        p.unlink()
    for p in (tmp / "state" / "hil").glob("P*.md"):
        p.unlink()
    (tmp / "state" / "gates" / "decisions.jsonl").write_text("", encoding="utf-8")
    return tmp


def tick(root: Path, *prefixes: str) -> None:
    """Tick every task whose id starts with one of the prefixes (e.g. 'P1-', 'P5-05')."""
    path = root / "state" / "backlog.md"
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\s*-\s+\[) (\]\s+)(P\d+-\d+)", line)
        if m and any(m.group(3).startswith(p) for p in prefixes):
            line = line.replace("- [ ]", "- [x]", 1)
        lines.append(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_hook(root: Path, name: str, payload: dict) -> str:
    proc = subprocess.run(
        [sys.executable, str(root / ".claude" / "hooks" / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=root,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def human(root: Path, prompt: str) -> str:
    return run_hook(root, "record_human_decision.py", {"prompt": prompt, "session_id": "test"})


class NextActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = make_root()
        self.h = Harness(self.root)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_fresh_project_starts_with_first_research_task(self):
        nxt = self.h.next_action()
        self.assertEqual(nxt["kind"], "task")
        self.assertEqual(nxt["mode"], "do")
        self.assertEqual(nxt["task"]["id"], "P1-01")
        self.assertEqual(nxt["task"]["owner"], "research-scout")

    def test_phase_exit_gate_blocks_next_phase(self):
        tick(self.root, "P1-")
        self.assertEqual(self.h.next_action()["kind"], "prepare_gate")
        self.h.open_gate("G1")
        nxt = self.h.next_action()
        self.assertEqual((nxt["kind"], nxt["gate"]), ("wait_gate", "G1"))

    def test_approval_via_hook_unblocks_next_phase(self):
        tick(self.root, "P1-")
        self.h.open_gate("G1")
        out = human(self.root, "/approve G1 looks great, but drop the GPL repo")
        self.assertIn("RECORDED", out)
        nxt = self.h.next_action()
        self.assertEqual(nxt["task"]["id"], "P2-01")
        d = self.h.decisions()[-1]
        self.assertEqual((d["id"], d["decision"], d["revision"]), ("G1", "approved", 1))
        self.assertEqual(d["notes"], "looks great, but drop the GPL repo")

    def test_rejection_revision_cycle(self):
        tick(self.root, "P1-")
        self.h.open_gate("G1")
        self.assertIn("RECORDED", human(self.root, "/reject G1 need more running-specific papers"))
        nxt = self.h.next_action()
        self.assertEqual(nxt["kind"], "revise_gate")
        self.assertIn("running-specific", nxt["human_notes"])
        # a second decision on the same revision is refused
        self.assertIn("NOT recorded", human(self.root, "/approve G1"))
        self.h.open_gate("G1")  # bumps to revision 2
        self.assertEqual(self.h.gate_status("G1")[:1], ("pending",))
        self.assertEqual(self.h.gate_status("G1")[2], 2)
        self.assertIn("RECORDED", human(self.root, "/approve G1"))
        self.assertEqual(self.h.gate_status("G1")[0], "approved")

    def test_hook_refusals(self):
        self.assertIn("unknown gate", human(self.root, "/approve G9"))
        self.assertIn("no request packet", human(self.root, "/approve G1"))
        self.assertIn("needs an id", human(self.root, "/approve"))
        self.assertEqual(human(self.root, "please approve G1"), "")  # prose is not a command
        self.assertEqual(self.h.decisions(), [])

    def test_g4_requires_option_and_controls_stage_two(self):
        tick(self.root, "P1-", "P2-", "P3-", "P4-", "P5-", "P6-")
        for g in ("G1", "G2", "G3"):
            self.h.open_gate(g)
            human(self.root, f"/approve {g}")
        self.h.open_gate("G4")
        self.assertIn("needs an option", human(self.root, "/approve G4 sure"))
        self.assertIn("RECORDED", human(self.root, "/approve G4 custom let's go"))
        nxt = self.h.next_action()
        self.assertEqual(nxt["task"]["id"], "P7-01")

    def test_g4_finish_skips_stage_two(self):
        tick(self.root, "P1-", "P2-", "P3-", "P4-", "P5-", "P6-")
        for g in ("G1", "G2", "G3"):
            self.h.open_gate(g)
            human(self.root, f"/approve {g}")
        self.h.open_gate("G4")
        human(self.root, "/approve G4 finish")
        self.assertEqual(self.h.next_action()["kind"], "done")

    def test_mid_phase_gate_g5(self):
        tick(self.root, "P1-", "P2-", "P3-", "P4-", "P5-", "P6-")
        for g in ("G1", "G2", "G3"):
            self.h.open_gate(g)
            human(self.root, f"/approve {g}")
        self.h.open_gate("G4")
        human(self.root, "/approve G4 custom")
        tick(self.root, "P7-01", "P7-02", "P7-03", "P7-04", "P7-05", "P7-06", "P7-07")
        self.assertEqual(self.h.next_action()["kind"], "prepare_gate")
        self.h.open_gate("G5")
        self.assertEqual(self.h.next_action()["kind"], "wait_gate")
        human(self.root, "/approve G5")
        nxt = self.h.next_action()
        self.assertEqual((nxt["task"]["id"], nxt["mode"]), ("P7-08", "prepare_hil"))

    def test_hil_lifecycle(self):
        tick(self.root, "P1-", "P2-", "P3-", "P4-", "P5-01", "P5-02", "P5-03", "P5-04")
        for g in ("G1", "G2", "G3"):
            self.h.open_gate(g)
            human(self.root, f"/approve {g}")
        nxt = self.h.next_action()
        self.assertEqual((nxt["task"]["id"], nxt["mode"]), ("P5-05", "prepare_hil"))
        self.assertIn("no instructions", human(self.root, "/hil-done P5-05"))
        self.h.open_hil("P5-05")
        self.assertEqual(self.h.next_action()["kind"], "wait_hil")
        self.assertIn("RECORDED", human(self.root, "/hil-failed P5-05 two FSRs missing from the bag"))
        nxt = self.h.next_action()
        self.assertEqual(nxt["mode"], "fix_hil")
        self.assertIn("FSRs missing", nxt["human_notes"])
        self.h.open_hil("P5-05")  # revision 2
        self.assertEqual(self.h.next_action()["kind"], "wait_hil")
        self.assertIn("RECORDED", human(self.root, "/hil-done p5-05 all parts present after reorder"))
        self.assertEqual(self.h.next_action()["mode"], "verify_hil")
        self.assertIn("not a hardware-in-the-loop task", human(self.root, "/hil-done P5-03"))


class ValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = make_root()
        self.h = Harness(self.root)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_fresh_state_is_valid(self):
        errors, _ = self.h.validate()
        self.assertEqual(errors, [])

    def test_ticked_hil_without_human_record_is_an_error(self):
        tick(self.root, "P5-05")
        errors, _ = self.h.validate()
        self.assertTrue(any("P5-05" in e and "hil-done" in e for e in errors), errors)

    def test_forged_decision_is_an_error(self):
        forged = {"ts": "2026-01-01T00:00:00+00:00", "kind": "gate", "id": "G1", "revision": 1,
                  "decision": "approved", "option": None, "notes": "", "source": "agent"}
        (self.root / "state" / "gates" / "decisions.jsonl").write_text(json.dumps(forged) + "\n")
        errors, _ = self.h.validate()
        self.assertTrue(any("not written by the human-decision hook" in e for e in errors), errors)

    def test_unknown_owner_is_an_error(self):
        path = self.root / "state" / "backlog.md"
        path.write_text(path.read_text().replace("owner: research-scout -->", "owner: nobody -->", 1))
        errors, _ = self.h.validate()
        self.assertTrue(any("nobody" in e for e in errors), errors)


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = make_root()

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def guard(self, tool: str, tool_input: dict) -> str:
        return run_hook(self.root, "guard.py", {"tool_name": tool, "tool_input": tool_input, "cwd": str(self.root)})

    def assertDenied(self, out: str):
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_blocks_editing_decisions(self):
        self.assertDenied(self.guard("Write", {"file_path": str(self.root / "state/gates/decisions.jsonl")}))
        self.assertDenied(self.guard("Edit", {"file_path": "state/gates/decisions.jsonl"}))

    def test_blocks_shell_writes_to_decisions(self):
        self.assertDenied(self.guard("Bash", {"command": "echo '{}' >> state/gates/decisions.jsonl"}))
        self.assertDenied(self.guard("Bash", {"command": "cat x > state/gates/decisions.jsonl"}))
        self.assertDenied(self.guard("Bash", {"command": "python3 -c 'open(\"state/gates/decisions.jsonl\",\"a\")'"}))
        self.assertDenied(self.guard("Bash", {"command": "echo '{\"prompt\":\"/approve G1\"}' | python3 .claude/hooks/record_human_decision.py"}))

    def test_allows_reading_decisions_and_normal_work(self):
        self.assertEqual(self.guard("Bash", {"command": "cat state/gates/decisions.jsonl"}), "")
        self.assertEqual(self.guard("Bash", {"command": "git add state/ && git commit -m 'x'"}), "")
        self.assertEqual(self.guard("Write", {"file_path": str(self.root / "state/gates/G1.md")}), "")
        self.assertEqual(self.guard("Bash", {"command": "python3 scripts/harness.py next"}), "")

    def test_blocks_force_adding_raw_data(self):
        self.assertDenied(self.guard("Bash", {"command": "git add -f data/raw/run1.csv"}))
        self.assertDenied(self.guard("Bash", {"command": "git add --force data/raw"}))

    def test_blocks_commit_with_staged_raw_data(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "data" / "raw").mkdir(parents=True, exist_ok=True)
        (self.root / "data" / "raw" / "run1.csv").write_text("t_s,heel\n0,1\n")
        subprocess.run(["git", "add", "-f", "data/raw/run1.csv"], cwd=self.root, check=True)
        self.assertDenied(self.guard("Bash", {"command": "git commit -m 'oops'"}))


class SessionStartTests(unittest.TestCase):
    def test_brief_mentions_next_action(self):
        root = make_root()
        try:
            out = run_hook(root, "session_start.py", {"hook_event_name": "SessionStart", "source": "startup"})
            self.assertIn("Session brief", out)
            self.assertIn("NEXT [task/do]: P1-01", out)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
