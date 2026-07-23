#!/usr/bin/env python3
"""Run Arm B: trust layer on a research draft → prose final report (product output)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trust_layer.ledger import (
    build_ledger,
    ledger_from_jsonable,
    ledger_to_jsonable,
    render_ledger_markdown,
    render_structured_report,
    title_from_question,
)

DEFAULT_QUESTION = (
    "What are the real-world risks and benefits of using synthetic data to train "
    "or fine-tune large language models? Focus on data quality, bias, and evaluation."
)


def _extract_question(report: str) -> str:
    m = re.search(r"\*\*Question:\*\*\s*(.+)", report)
    if m:
        return m.group(1).strip()
    return DEFAULT_QUESTION


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trust layer → prose deep research report (Arm B / product final)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to fluent research draft (markdown/text)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "examples" / "arm_b"),
    )
    parser.add_argument(
        "--title",
        default="",
        help="Report title (default: derived from question)",
    )
    parser.add_argument(
        "--reuse-ledger",
        action="store_true",
        help="Rebuild report from existing ledger.json (skip re-extraction/grounding)",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 1
    report = src.read_text(encoding="utf-8")
    if len(report.strip()) < 80:
        print("ERROR: input report looks empty", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ledger.json"
    ledger_path = out_dir / "ledger.md"
    report_path = out_dir / "report.md"

    if args.reuse_ledger and json_path.exists():
        print("Reusing existing ledger.json ...")
        rows = ledger_from_jsonable(json.loads(json_path.read_text()))
    else:
        print("Building claim ledger (extract → tier → grounding)...")
        rows = build_ledger(report)
        json_path.write_text(json.dumps(ledger_to_jsonable(rows), indent=2))

    question = _extract_question(report)
    title = args.title.strip() or title_from_question(question)
    print("Writing trust-aware prose report (product final)...")
    structured = render_structured_report(
        rows,
        question=question,
        title=title,
        draft=report,
    )
    ledger_md = render_ledger_markdown(
        rows, title="Internal audit ledger (not user-facing)"
    )

    report_path.write_text(structured)
    ledger_path.write_text(ledger_md)

    print(f"Claims: {len(rows)}")
    print(f"Wrote product report: {report_path}")
    print(f"Wrote ledger appendix: {ledger_path}")
    print(f"Wrote: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
