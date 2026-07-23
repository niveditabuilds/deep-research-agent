"""Hard grounding checks: URL resolves + evidence appears in page text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests


@dataclass
class GroundingResult:
    ok: bool
    url_resolves: bool
    evidence_found: bool
    status_code: Optional[int]
    detail: str
    fetched_chars: int = 0


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _key_atoms(evidence: str) -> list[str]:
    """Extract numbers/names-ish tokens for fuzzy fallback."""
    atoms = re.findall(r"\b\d+(?:\.\d+)?%?\b|\b[A-Z][a-zA-Z]{2,}\b", evidence)
    return atoms


def check_grounding(
    url: str,
    evidence: str,
    timeout: int = 25,
    session: Optional[requests.Session] = None,
) -> GroundingResult:
    if not url or not url.startswith(("http://", "https://")):
        return GroundingResult(
            ok=False,
            url_resolves=False,
            evidence_found=False,
            status_code=None,
            detail="Missing or invalid URL",
        )

    sess = session or requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; DeepResearchTrustLayer/1.0; +local-mvp)"
        )
    }
    try:
        resp = sess.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        status = resp.status_code
        if status >= 400:
            return GroundingResult(
                ok=False,
                url_resolves=False,
                evidence_found=False,
                status_code=status,
                detail=f"HTTP {status}",
            )
        body = resp.text or ""
        # Prefer visible-ish text; strip scripts/styles coarsely
        body = re.sub(r"(?is)<script.*?>.*?</script>", " ", body)
        body = re.sub(r"(?is)<style.*?>.*?</style>", " ", body)
        body = re.sub(r"(?is)<[^>]+>", " ", body)
        norm_body = _normalize(body)
        norm_ev = _normalize(evidence or "")

        if not norm_ev:
            return GroundingResult(
                ok=False,
                url_resolves=True,
                evidence_found=False,
                status_code=status,
                detail="Empty evidence span",
                fetched_chars=len(norm_body),
            )

        found = False
        detail = "Evidence span not found in page text"
        if norm_ev in norm_body:
            found = True
            detail = "Exact evidence span found"
        else:
            # Light normalization: try without quotes
            stripped = norm_ev.strip("\"'")
            if stripped and stripped in norm_body:
                found = True
                detail = "Evidence found after quote strip"
            else:
                # Require at least one distinctive atom (number or Capitalized token)
                atoms = _key_atoms(evidence)
                if atoms and all(_normalize(a) in norm_body for a in atoms[:3]):
                    found = True
                    detail = f"Key atoms found: {atoms[:3]}"

        return GroundingResult(
            ok=found,
            url_resolves=True,
            evidence_found=found,
            status_code=status,
            detail=detail,
            fetched_chars=len(norm_body),
        )
    except requests.RequestException as e:
        return GroundingResult(
            ok=False,
            url_resolves=False,
            evidence_found=False,
            status_code=None,
            detail=f"Fetch failed: {type(e).__name__}: {e}",
        )
