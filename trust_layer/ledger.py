"""Build and render the claim ledger + trust-aware prose report."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Any, Optional

import requests

from .claims import extract_claims
from .grounding import check_grounding
from .tiers import TIER_LABELS, assign_tier

DEFAULT_REWRITE_MODEL = "claude-sonnet-4-5-20250929"

PROSE_REWRITE_PROMPT = """You write the FINAL user-facing deep research report for a trust-aware research agent.

Write a real multi-section research brief in markdown prose (paragraphs under ## / ### headings).
Do NOT write a bullet dump of claims. Do NOT leave empty stub sections.

Trust rules (authoritative — the ledger decides what may be stated):
- VERIFIED_STRONG: state clearly as findings.
- VERIFIED_WEAK: include with softer framing ("secondary reporting suggests", "industry commentary indicates").
- UNVERIFIED: do NOT assert as fact in the main body. List them ONLY under a final
  "## Needs review" section wrapped in HTML <details>/<summary> (collapsed by default).

REQUIRED citations (do not skip):
- Whenever you use a VERIFIED_STRONG or VERIFIED_WEAK claim, you MUST attach its url from the ledger
  as a markdown link immediately after that sentence, e.g. ([source](https://...)).
- If several claims share one url, still include the link at least once per paragraph that uses them.
- Do not invent urls. Only use urls present in the ledger.
- A report with findings but zero https links is incorrect — rewrite until verified claims have links.

Structure:
- Start with: # {title}
- Include **Question:** line
- Prefer the draft's thematic outline
  but OMIT sections that would have no verified content — do not write "no claims passed" stubs.
- Executive summary in prose, then thematic sections in prose.
- End with ## Needs review (details block) if there are UNVERIFIED items, then ## Limits of this report.

Other rules:
- Remove agent chatter ("Excellent. Now I have gathered...").
- Do not invent facts beyond the draft + ledger.
- Do not mention tiers, grounding, Arm A/B, or internal pipeline jargon.
- Keep length similar to a concise deep-research brief (not a telegram; not a 50-page dump).

Question:
{question}

Claim ledger:
{ledger_summary}

Research draft (use for outline and wording; filter by ledger):
---
{draft}
---
"""


@dataclass
class LedgerRow:
    claim: str
    evidence: str
    source_url: str
    tier: int
    tier_label: str
    grounding: str  # pass | fail
    grounding_detail: str
    coverage: str  # ok | low


def build_ledger(
    report: str,
    session: Optional[requests.Session] = None,
) -> list[LedgerRow]:
    claims = extract_claims(report)
    sess = session or requests.Session()
    out: list[LedgerRow] = []
    for c in claims:
        tier = assign_tier(c.source_url)
        if not c.source_url:
            out.append(
                LedgerRow(
                    claim=c.claim,
                    evidence=c.evidence,
                    source_url="",
                    tier=3,
                    tier_label=TIER_LABELS[3],
                    grounding="fail",
                    grounding_detail="No source URL",
                    coverage="low",
                )
            )
            continue
        g = check_grounding(c.source_url, c.evidence, session=sess)
        out.append(
            LedgerRow(
                claim=c.claim,
                evidence=c.evidence,
                source_url=c.source_url,
                tier=tier,
                tier_label=TIER_LABELS[tier],
                grounding="pass" if g.ok else "fail",
                grounding_detail=g.detail,
                coverage="ok" if g.url_resolves else "low",
            )
        )
    return out


def render_ledger_markdown(rows: list[LedgerRow], title: str = "Claim ledger") -> str:
    lines = [
        f"# {title}",
        "",
        "Confidence = source tier. Grounding fail ⇒ unsupported regardless of tier.",
        "",
        "| # | Claim | Evidence | Source | Tier (confidence) | Grounding | Coverage |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        claim = r.claim.replace("|", "\\|").replace("\n", " ")
        ev = r.evidence.replace("|", "\\|").replace("\n", " ")
        url = r.source_url.replace("|", "\\|")
        g = r.grounding
        if r.grounding == "fail":
            g = "fail (unsupported)"
        lines.append(
            f"| {i} | {claim} | {ev} | {url} | {r.tier} | {g} | {r.coverage} |"
        )
    lines.extend(["", "## Tier counts", ""])
    for t in (1, 2, 3):
        n = sum(1 for r in rows if r.tier == t)
        lines.append(f"- Tier {t}: {n}")
    unsupported = sum(1 for r in rows if r.grounding == "fail")
    lines.append(f"- Unsupported (grounding fail): {unsupported}")
    lines.append("")
    return "\n".join(lines)


def _partition(
    rows: list[LedgerRow],
) -> tuple[list[LedgerRow], list[LedgerRow], list[LedgerRow]]:
    strong = [r for r in rows if r.grounding == "pass" and r.tier <= 2]
    weak = [r for r in rows if r.grounding == "pass" and r.tier >= 3]
    fail = [r for r in rows if r.grounding == "fail"]
    return strong, weak, fail


def _ledger_summary_for_rewrite(rows: list[LedgerRow]) -> str:
    strong, weak, fail = _partition(rows)
    buckets = {
        "VERIFIED_STRONG": strong,
        "VERIFIED_WEAK": weak,
        "UNVERIFIED": fail,
    }
    parts: list[str] = []
    for label, items in buckets.items():
        parts.append(f"### {label}")
        if not items:
            parts.append("(none)")
        for r in items:
            parts.append(f"- claim: {r.claim}")
            if r.source_url:
                parts.append(f"  url: {r.source_url}")
            if r.evidence:
                parts.append(f"  evidence: {r.evidence[:220]}")
        parts.append("")
    return "\n".join(parts)


def _needs_review_block(unverified: list[LedgerRow]) -> str:
    if not unverified:
        return ""
    lines = [
        "## Needs review",
        "",
        "<details>",
        "<summary>Claims from the research draft that could not be verified — expand to inspect</summary>",
        "",
        "These failed a receipt check (missing URL, blocked page, or evidence span not found). "
        "They are **not** findings.",
        "",
    ]
    for r in unverified:
        lines.append(f"- {r.claim}")
    lines.extend(["", "</details>", ""])
    return "\n".join(lines)


def _append_limits(text: str) -> str:
    if "## Limits" in text:
        return text
    return (
        text.rstrip()
        + "\n\n## Limits of this report\n\n"
        + "This final report only states claims that could be confirmed against fetched source text. "
        + "Unconfirmed items from the research draft appear under Needs review.\n"
    )


def _rewrite_prose_with_llm(
    *,
    draft: str,
    rows: list[LedgerRow],
    question: str,
    title: str,
    model: str,
) -> str:
    prompt = PROSE_REWRITE_PROMPT.format(
        title=title,
        question=question or "(see draft)",
        ledger_summary=_ledger_summary_for_rewrite(rows),
        draft=draft[:45000],
    )
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 8192,
                "temperature": 0,
                "system": (
                    "You write polished multi-section deep research reports in markdown prose. "
                    "Obey the claim ledger strictly."
                ),
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(
            p.get("text", "")
            for p in data.get("content", [])
            if p.get("type") == "text"
        ).strip()

    from .claims import _chat_openrouter

    return _chat_openrouter(
        [
            {
                "role": "system",
                "content": "You write polished multi-section deep research reports in markdown prose.",
            },
            {"role": "user", "content": prompt},
        ],
        model,
    ).strip()


def _render_prose_fallback(
    rows: list[LedgerRow],
    *,
    question: str,
    title: str,
) -> str:
    """Short prose report if the LLM rewrite is unavailable."""
    strong, weak, fail = _partition(rows)
    lines = [
        f"# {title}",
        "",
        f"**Question:** {question}",
        "",
        "## Executive summary",
        "",
    ]
    if strong:
        para = " ".join(r.claim.rstrip(".") + "." for r in strong[:5])
        lines.append(para)
        lines.append("")
        lines.append(
            f"Of {len(rows)} extracted claims from the research draft, "
            f"{len(strong) + len(weak)} could be confirmed in cited sources."
        )
        lines.append("")
        lines.extend(["## Findings", ""])
        for r in strong:
            src = f" ([source]({r.source_url}))" if r.source_url else ""
            lines.append(f"{r.claim}{src}")
            lines.append("")
        if weak:
            lines.extend(["## Additional context", ""])
            lines.append(
                "Secondary reporting also suggests the following, with thinner source support:"
            )
            lines.append("")
            for r in weak:
                src = f" ([source]({r.source_url}))" if r.source_url else ""
                lines.append(f"{r.claim}{src}")
                lines.append("")
    elif weak:
        lines.append(
            "Few claims could be confirmed in higher-quality sources. "
            "What follows is drawn from secondary reporting that still passed a receipt check."
        )
        lines.append("")
        lines.extend(["## Findings", ""])
        for r in weak:
            src = f" ([source]({r.source_url}))" if r.source_url else ""
            lines.append(f"{r.claim}{src}")
            lines.append("")
    else:
        lines.append(
            "This run did not produce claims that could be verified against their cited sources. "
            "Treat the research draft as exploratory only; see Needs review."
        )
        lines.append("")

    needs = _needs_review_block(fail)
    if needs:
        lines.append(needs)
    return _append_limits("\n".join(lines))


def _strip_needs_review_sections(text: str) -> str:
    """Remove model-written Needs review blocks so we can append a deterministic one."""
    # Drop <details>...</details> blocks that look like Needs review
    text = re.sub(
        r"<details>\s*<summary>[\s\S]*?</summary>[\s\S]*?</details>\s*",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"##\s*Needs review\b[\s\S]*?(?=##\s|\Z)",
        "",
        text,
        flags=re.I,
    )
    return text.rstrip() + "\n"


def render_structured_report(
    rows: list[LedgerRow],
    question: str,
    title: str = "Deep research report",
    draft: str = "",
    rewrite_model: str = DEFAULT_REWRITE_MODEL,
) -> str:
    """Product final report: trust-conditioned multi-section prose."""
    _, _, fail = _partition(rows)
    if draft.strip():
        try:
            text = _rewrite_prose_with_llm(
                draft=draft,
                rows=rows,
                question=question,
                title=title,
                model=rewrite_model,
            )
            if text:
                text = _strip_needs_review_sections(text)
                needs = _needs_review_block(fail)
                if needs:
                    text = text.rstrip() + "\n\n" + needs
                text = _append_limits(text)
                if not text.lstrip().startswith("#"):
                    text = f"# {title}\n\n{text}"
                return text
        except Exception as e:
            print(
                f"WARNING: prose rewrite failed ({e}); using prose fallback",
                file=sys.stderr,
            )

    return _render_prose_fallback(rows, question=question, title=title)


def ledger_to_jsonable(rows: list[LedgerRow]) -> list[dict[str, Any]]:
    return [asdict(r) for r in rows]


def ledger_from_jsonable(items: list[dict[str, Any]]) -> list[LedgerRow]:
    return [LedgerRow(**item) for item in items]


def title_from_question(question: str, fallback: str = "Deep research report") -> str:
    """Short report title derived from the question (not a hardcoded topic)."""
    q = (question or "").strip()
    if not q:
        return fallback
    q = re.split(r"[?\n]", q)[0].strip()
    q = re.sub(
        r"^(what are the|what is the|what are|what is|how do|how does|how is|is|are)\s+",
        "",
        q,
        flags=re.I,
    )
    if len(q) > 72:
        q = q[:69].rstrip() + "…"
    return q[:1].upper() + q[1:] if q else fallback
