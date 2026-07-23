"""Source tier (= confidence) from URL host rules."""

from __future__ import annotations

from urllib.parse import urlparse

TIER_LABELS = {
    1: "Tier 1 (highest confidence) — papers / official / gov",
    2: "Tier 2 — reputable news / tech press",
    3: "Tier 3 (lowest confidence) — social / forums / blogs / unknown",
}

# Host suffixes / exact hosts → tier
TIER1_SUFFIXES = (
    "arxiv.org",
    "gov",  # handled specially for *.gov
    "acm.org",
    "ieee.org",
    "neurips.cc",
    "mlr.press",
    "openreview.net",
    "nature.com",
    "science.org",
    "pnas.org",
    "springer.com",
    "sciencedirect.com",
    "wiley.com",
    "nih.gov",
    "nist.gov",
)

TIER1_EXACT = {
    "arxiv.org",
    "export.arxiv.org",
    "aclanthology.org",
    "proceedings.mlr.press",
    "dl.acm.org",
    "ieeexplore.ieee.org",
    "openreview.net",
    "papers.nips.cc",
    "proceedings.neurips.cc",
}

TIER2_EXACT = {
    "nytimes.com",
    "www.nytimes.com",
    "wsj.com",
    "www.wsj.com",
    "reuters.com",
    "www.reuters.com",
    "bbc.com",
    "www.bbc.com",
    "bbc.co.uk",
    "theguardian.com",
    "www.theguardian.com",
    "bloomberg.com",
    "www.bloomberg.com",
    "ft.com",
    "www.ft.com",
    "economist.com",
    "www.economist.com",
    "techcrunch.com",
    "www.techcrunch.com",
    "wired.com",
    "www.wired.com",
    "arstechnica.com",
    "www.arstechnica.com",
    "theverge.com",
    "www.theverge.com",
    "mit.edu",
    "news.mit.edu",
    "stanford.edu",
    "openai.com",
    "www.openai.com",
    "anthropic.com",
    "www.anthropic.com",
    "deepmind.google",
    "blog.google",
    "ai.googleblog.com",
    "huggingface.co",
    "www.huggingface.co",
    "microsoft.com",
    "www.microsoft.com",
    "meta.com",
    "ai.meta.com",
    "nvidia.com",
    "www.nvidia.com",
    "towardsdatascience.com",
    "medium.com",  # borderline; treat as tier 2 only for known pubs — keep medium as 3 by default
}

# Remove medium from tier2 - it's often low quality
TIER2_EXACT.discard("medium.com")

TIER3_HINTS = (
    "reddit.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "tiktok.com",
    "quora.com",
    "substack.com",
    "medium.com",
    "blogspot.",
    "wordpress.",
    "tumblr.",
    "discord.com",
    "linkedin.com",
)


def _host(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def assign_tier(url: str) -> int:
    """Return 1, 2, or 3. Unknown → 3."""
    if not url or not url.startswith(("http://", "https://")):
        return 3
    host = _host(url)
    if not host:
        return 3

    for hint in TIER3_HINTS:
        if hint in host:
            return 3

    if host in TIER1_EXACT or host.endswith(".gov") or host.endswith(".gov.uk"):
        return 1
    for suf in TIER1_SUFFIXES:
        if suf == "gov":
            continue
        if host == suf or host.endswith("." + suf):
            return 1

    # edu paper/docs paths often tier 1-ish; keep edu as tier 2 unless known venue
    if host.endswith(".edu"):
        return 2

    if host in TIER2_EXACT:
        return 2
    for known in TIER2_EXACT:
        if host.endswith("." + known) or known.endswith(host):
            return 2

    return 3
