#!/usr/bin/env python3
"""Extract the final research narrative from a harness task log JSON/log file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_from_json(data: dict) -> str:
    # Common fields in TaskTracer-style logs
    for key in (
        "final_boxed_answer",
        "final_answer",
        "final_summary",
        "answer",
    ):
        val = data.get(key)
        if isinstance(val, str) and len(val.strip()) > 40:
            return val.strip()
    # Nested
    input_ = data.get("input")
    if isinstance(input_, dict):
        pass
    # Message histories
    hist = data.get("main_agent_message_history")
    if isinstance(hist, dict):
        messages = hist.get("message_history") or hist.get("messages")
        if isinstance(messages, list):
            for msg in reversed(messages):
                content = msg.get("content")
                if isinstance(content, str) and len(content) > 80:
                    return content
                if isinstance(content, list):
                    texts = [
                        c.get("text", "")
                        for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    ]
                    joined = "\n".join(texts).strip()
                    if len(joined) > 80:
                        return joined
    return ""


def extract_from_text(text: str) -> str:
    # Look for boxed answer
    m = re.search(r"\\boxed\{([\s\S]*?)\}", text)
    if m and len(m.group(1).strip()) > 40:
        return m.group(1).strip()
    m = re.search(
        r"Final Answer:\s*([\s\S]+?)(?:\n={5,}|\n---|\Z)",
        text,
        re.IGNORECASE,
    )
    if m and len(m.group(1).strip()) > 40:
        return m.group(1).strip()
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Harness log path (.json or .log)")
    parser.add_argument("--out", required=True, help="Output markdown path")
    args = parser.parse_args()

    path = Path(args.log)
    raw = path.read_text(encoding="utf-8", errors="replace")
    content = ""
    if path.suffix == ".json" or raw.lstrip().startswith("{"):
        try:
            data = json.loads(raw)
            content = extract_from_json(data)
        except json.JSONDecodeError:
            content = extract_from_text(raw)
    else:
        content = extract_from_text(raw)

    if not content:
        print("WARNING: could not extract a clean final answer; writing raw log head", file=sys.stderr)
        content = raw[:50000]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "# Research draft (from harness)\n\n" + content + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out} ({len(content)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
