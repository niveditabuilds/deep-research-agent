# Ablation comparison — Example 1

**Question:** synthetic data risks/benefits for LLM training (assignment Example 1)

## Arms

| Arm | Path | Description |
|---|---|---|
| A | `arm_a/report_body.md` | Fluent research draft (pre-trust) |
| B | `arm_b/report.md` | **Product final:** trust-aware multi-section **prose** report; failed receipts under collapsed **Needs review**; audit in `ledger.md` |

## Quality difference

| Signal | Result |
|---|---|
| Extracted claims | 20 |
| Grounding fail (Needs review) | 15 |
| Verified strong (pass + tier ≤ 2) | subset stated as findings in prose |
| Readability | B reads as a deep-research brief (paragraphs), not a claim bullet board |

## One concrete demotion

- Claim (smooth in A): Research reveals at least eight distinct definitions of model collapse in the literature.
- What B did: Tier 1, grounding=fail — Evidence span not found in page text → **Needs review**
- Source: https://arxiv.org/html/2503.14023v1

## Notes

- A optimizes for completeness/fluency; B optimizes for what can be stood behind.
- Fetch 403s / span mismatches cause hard-grounding false negatives.

See [../../DECISION_LOG.md](../../DECISION_LOG.md).
