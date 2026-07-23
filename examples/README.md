# Example outputs

Three assignment-style prompts. Each folder has:

| Path | Contents |
|---|---|
| `arm_a/` | Fluent research draft (pre-trust / ablation) |
| `arm_b/` | **Product final:** trust-aware prose report + internal ledger |
| `NOTES.md` | Quality notes / A vs B callouts |

| # | Prompt focus | Why it stresses the system |
|---|---|---|
| [01_synthetic_data](./01_synthetic_data/) | Risks/benefits of synthetic data for LLMs | Mixed source quality; easy Tier 1 vs Tier 3 demotions |
| [02_chain_of_thought](./02_chain_of_thought/) | CoT: reasoning vs formatting (literature disagrees) | Contradictory sources; trust layer should not paper over conflict |
| [03_inference_time_scaling](./03_inference_time_scaling/) | Inference-time compute scaling | Sparse / emerging; thin evidence should stay in Needs review |

Process log: [../DECISION_LOG.md](../DECISION_LOG.md).

Run one end-to-end MVP: `harness/.venv/bin/python scripts/run_mvp.py --out-dir examples/mvp_run`
