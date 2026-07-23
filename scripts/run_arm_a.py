#!/usr/bin/env python3
"""Run Arm A: harness + Claude + web search → fluent research report."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
DEFAULT_QUESTION = (
    "What are the real-world risks and benefits of using synthetic data to train "
    "or fine-tune large language models? Focus on data quality, bias, and evaluation."
)


def _extract_answer(log_path: Path) -> str:
    """Prefer the long comprehensive report + append source URLs from the tool trail."""
    raw = log_path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:50000]

    def text_of(msg: dict) -> str:
        content = msg.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                c.get("text", "")
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            )
        return ""

    hist = data.get("main_agent_message_history") or {}
    messages = hist.get("message_history") or []
    best = ""
    if isinstance(messages, list):
        for msg in messages:
            if msg.get("role") != "assistant":
                continue
            t = re.sub(r"<use_mcp_tool>[\s\S]*$", "", text_of(msg)).strip()
            if (
                "Comprehensive Report" in t
                or "FINAL COMPREHENSIVE REPORT" in t
                or (t.startswith("#") and len(t) > 3000)
            ):
                if len(t) > len(best):
                    best = t
        if not best:
            for msg in reversed(messages):
                if msg.get("role") != "assistant":
                    continue
                t = re.sub(r"<use_mcp_tool>[\s\S]*$", "", text_of(msg)).strip()
                if len(t) > len(best):
                    best = t

        urls = []
        for msg in messages:
            for u in re.findall(r"https?://[^\s\"'<>\]]+", text_of(msg)):
                u = u.rstrip(").,]\"'")
                if any(x in u for x in ("google.serper", "api.anthropic", "openrouter")):
                    continue
                if u not in urls:
                    urls.append(u)
        if urls:
            best = best + "\n\n## Sources consulted (from tool trail)\n\n"
            best += "\n".join(f"- {u}" for u in urls[:60])

    if best:
        return best
    boxed = data.get("final_boxed_answer") or ""
    return boxed if isinstance(boxed, str) else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run baseline research agent (Arm A)")
    parser.add_argument("--task", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--task-id-prefix",
        default="research",
        help="Prefix for harness task_id / log name",
    )
    parser.add_argument(
        "--config",
        default="agent_mvp_anthropic",
        help="Harness config name (without .yaml)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "examples" / "arm_a"),
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    load_dotenv(HARNESS / ".env")

    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        print(
            "ERROR: Set ANTHROPIC_API_KEY in .env (Claude API key)",
            file=sys.stderr,
        )
        return 1
    if not os.environ.get("SERPER_API_KEY", "").strip():
        print(
            "ERROR: Set SERPER_API_KEY in .env (required for web search)",
            file=sys.stderr,
        )
        return 1

    harness_env = HARNESS / ".env"
    root_env = ROOT / ".env"
    if root_env.exists():
        harness_env.write_text(root_env.read_text())

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = re.sub(r"[^a-zA-Z0-9_-]+", "_", args.task_id_prefix).strip("_") or "research"
    task_id = f"{prefix}_{stamp}"

    cmd = [
        "uv",
        "run",
        "--python",
        "3.12",
        "main.py",
        "trace",
        f"--config_file_name={args.config}",
        f"--task={args.task}",
        f"--task_id={task_id}",
    ]
    print("Running:", " ".join(cmd))
    print("cwd:", HARNESS)
    result = subprocess.run(cmd, cwd=str(HARNESS), env=os.environ.copy())
    if result.returncode != 0:
        return result.returncode

    log_path = HARNESS / "logs" / f"{task_id}.log"
    meta_path = out_dir / "run_meta.txt"
    report_path = out_dir / "report.md"
    body_path = out_dir / "report_body.md"

    meta_lines = [
        f"task_id={task_id}",
        f"config={args.config}",
        f"question={args.task}",
        f"generated_at={stamp}",
        f"log_path={log_path}",
        "arm=A (fluent research report, no trust layer)",
    ]
    meta_path.write_text("\n".join(meta_lines) + "\n")

    answer = ""
    if log_path.exists():
        answer = _extract_answer(log_path)
        body_path.write_text(
            "# Research draft (Arm A)\n\n"
            f"**Question:** {args.task}\n\n"
            + (answer or "_No final answer extracted — check the harness log._")
            + "\n",
            encoding="utf-8",
        )
    else:
        body_path.write_text(
            "# Research draft (Arm A)\n\n_Log file not found. Check harness/logs/._\n"
        )

    preview = (
        (answer[:4000] + ("…" if len(answer) > 4000 else "")) if answer else "_empty_"
    )
    report_path.write_text(
        "\n".join(
            [
                "# Arm A — Baseline research report",
                "",
                f"**Question:** {args.task}",
                "",
                "Fluent harness output with web search. No claim ledger.",
                "",
                "## Metadata",
                "",
                "```",
                *meta_lines,
                "```",
                "",
                f"Draft body: `{body_path}`",
                "",
                "## Draft preview",
                "",
                preview,
                "",
            ]
        )
    )
    print(f"Wrote {body_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {meta_path}")
    print(
        "Next: python3 scripts/run_trust_layer.py "
        f"--input {body_path} --out-dir <example>/arm_b"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
