"""Extract (claim, evidence, url) triples from a research draft via LLM."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class ClaimRow:
    claim: str
    evidence: str
    source_url: str


EXTRACT_PROMPT = """You extract factual claims from a research report.

Return ONLY valid JSON with this schema:
{{
  "claims": [
    {{
      "claim": "one factual sentence",
      "evidence": "short quote or concrete span supporting it (numbers/names preferred)",
      "source_url": "https://..."
    }}
  ]
}}

Rules:
- Only include claims that appear to be factual assertions.
- If the report has a "Sources consulted" section, you MUST attach the best matching URL from that list for each claim whenever possible.
- Prefer claims that can be tied to an explicit URL.
- evidence must be a short span that should appear on the source page if the citation is real (use distinctive numbers, paper titles, or named entities).
- If a claim truly has no plausible URL from the report/sources list, set source_url to "".
- Max 20 claims. Prefer the most important ones about risks, benefits, data quality, bias, evaluation.
- Do not invent URLs that are not in the report.

Report:
---
{report}
---
"""


def _chat_openrouter(messages: list[dict[str, str]], model: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip(
        "/"
    ) + "/chat/completions"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0,
            "messages": messages,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _chat_anthropic(messages: list[dict[str, str]], model: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    # Convert to Anthropic messages API
    system = ""
    anth_messages = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            anth_messages.append({"role": m["role"], "content": m["content"]})
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 4096,
            "temperature": 0,
            "system": system or "Extract claims as JSON.",
            "messages": anth_messages,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = data.get("content", [])
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text")


def _parse_claims_json(text: str) -> list[ClaimRow]:
    text = text.strip()
    # Strip fences
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    # Find outermost JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    data: Any = json.loads(text)
    rows = []
    for item in data.get("claims", []):
        rows.append(
            ClaimRow(
                claim=str(item.get("claim", "")).strip(),
                evidence=str(item.get("evidence", "")).strip(),
                source_url=str(item.get("source_url", "")).strip(),
            )
        )
    return [r for r in rows if r.claim]


def extract_claims_heuristic(report: str) -> list[ClaimRow]:
    """Fallback: pull markdown-link-ish sentences when no LLM key is available."""
    rows: list[ClaimRow] = []
    # [text](url)
    for m in re.finditer(
        r"(?P<sent>[^.\n]{20,400}\[[^\]]+\]\((?P<url>https?://[^)]+)\))",
        report,
    ):
        sent = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group("sent")).strip()
        url = m.group("url")
        rows.append(ClaimRow(claim=sent[:300], evidence=sent[:180], source_url=url))
    # bare URLs after sentences
    if not rows:
        for m in re.finditer(
            r"(?P<sent>[A-Z][^.\n]{30,300}\.)\s*(?P<url>https?://\S+)",
            report,
        ):
            rows.append(
                ClaimRow(
                    claim=m.group("sent").strip(),
                    evidence=m.group("sent").strip()[:180],
                    source_url=m.group("url").rstrip(").,]"),
                )
            )
    return rows[:20]


def extract_claims(
    report: str,
    model: Optional[str] = None,
    use_heuristic_fallback: bool = True,
) -> list[ClaimRow]:
    messages = [
        {
            "role": "system",
            "content": "You are a careful research auditor. Output JSON only.",
        },
        {"role": "user", "content": EXTRACT_PROMPT.format(report=report[:120000])},
    ]
    try:
        if os.environ.get("OPENROUTER_API_KEY", "").strip():
            content = _chat_openrouter(
                messages,
                model or os.environ.get("TRUST_LAYER_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
            )
            return _parse_claims_json(content)
        if os.environ.get("ANTHROPIC_API_KEY", "").strip():
            content = _chat_anthropic(
                messages,
                model or os.environ.get("TRUST_LAYER_MODEL", "claude-sonnet-4-5-20250929"),
            )
            return _parse_claims_json(content)
        if use_heuristic_fallback:
            return extract_claims_heuristic(report)
        raise RuntimeError("No OPENROUTER_API_KEY or ANTHROPIC_API_KEY set")
    except Exception as e:
        if use_heuristic_fallback:
            rows = extract_claims_heuristic(report)
            if rows:
                return rows
        raise
