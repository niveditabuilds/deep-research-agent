# Example 02 — Chain-of-thought conflict

**Question:** Is CoT an effective reasoning strategy, or primarily formatting / rationalization?

## Arms

| Arm | Path |
|---|---|
| A | `arm_a/report_body.md` — fluent draft |
| B | `arm_b/report.md` — product prose final |

## Counts (Arm B ledger)

- Tier 1: 17 · Tier 2: 0 · Tier 3: 3
- Grounding fail (Needs review): 10
- Verified strong (pass + tier ≤ 2): 10

## One concrete demotion

- Claim (smooth in A): Instruction-tuned models like Qwen2.5 and Llama-3.1 change their initial answer in only ~25% of cases after…
- What B did: Tier 1, grounding=fail — evidence span not found → **Needs review**
- Source: https://arxiv.org/html/2510.16645v1

## Signal

Arm A narrates both sides fluently. Arm B writes a prose fault-line brief from receipt-checked claims only; punchy unverified numbers stay in Needs review.
