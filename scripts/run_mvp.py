#!/usr/bin/env python3
"""Run the agent live on any research question.

Usage:
  harness/.venv/bin/python scripts/run_mvp.py "Your question here"
  harness/.venv/bin/python scripts/run_mvp.py          # prompts for the question
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / "harness" / ".venv" / "bin" / "python"
if not PY.exists():
    PY = Path(sys.executable)


def _slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return (s[:max_len] or "query").rstrip("_")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Live demo: research any question → trust-aware prose report"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Research question (if omitted, you will be prompted)",
    )
    parser.add_argument(
        "--task",
        default="",
        help="Same as positional query (optional alias)",
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory (default: examples/live_<timestamp>_<slug>/)",
    )
    parser.add_argument("--task-id-prefix", default="live")
    parser.add_argument(
        "--skip-research",
        action="store_true",
        help="Reuse existing arm_a/report_body.md; only run trust pass",
    )
    args = parser.parse_args()

    task = (args.query or args.task or "").strip()
    if not task and not args.skip_research:
        try:
            task = input("Research question: ").strip()
        except EOFError:
            task = ""
    if not task and not args.skip_research:
        print("ERROR: provide a research question.", file=sys.stderr)
        print(
            'Example: python scripts/run_mvp.py "What are the risks of synthetic data for LLMs?"',
            file=sys.stderr,
        )
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.out_dir:
        out = Path(args.out_dir)
    else:
        out = ROOT / "examples" / f"live_{stamp}_{_slug(task or 'rerun')}"

    arm_a = out / "arm_a"
    arm_b = out / "arm_b"
    arm_a.mkdir(parents=True, exist_ok=True)
    arm_b.mkdir(parents=True, exist_ok=True)
    draft = arm_a / "report_body.md"

    print(f"Output directory: {out}")
    if task:
        print(f"Question: {task}")
    print()

    if not args.skip_research:
        print("=== 1/2 Research (fluent draft / Arm A) ===")
        r = subprocess.run(
            [
                str(PY),
                str(ROOT / "scripts" / "run_arm_a.py"),
                "--task",
                task,
                "--task-id-prefix",
                args.task_id_prefix,
                "--out-dir",
                str(arm_a),
            ],
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            return r.returncode
    elif not draft.exists():
        print(f"ERROR: missing draft {draft}", file=sys.stderr)
        return 1

    print()
    print("=== 2/2 Trust pass → prose final (Arm B / product) ===")
    r = subprocess.run(
        [
            str(PY),
            str(ROOT / "scripts" / "run_trust_layer.py"),
            "--input",
            str(draft),
            "--out-dir",
            str(arm_b),
        ],
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        return r.returncode

    print()
    print("Done.")
    print(f"  Arm A (fluent draft):  {draft}")
    print(f"  Arm B (product report): {arm_b / 'report.md'}")
    print(f"  Ledger (audit):         {arm_b / 'ledger.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
