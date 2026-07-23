# Arm A — Baseline research report

**Question:** Is chain-of-thought prompting an effective reasoning strategy for LLMs, or does it primarily improve output formatting? The literature disagrees—find the real fault lines and explain what accounts for the conflicting results.

Fluent harness output with web search. No claim ledger.

## Metadata

```
task_id=cot_conflict_20260723_020950
config=agent_mvp_anthropic
question=Is chain-of-thought prompting an effective reasoning strategy for LLMs, or does it primarily improve output formatting? The literature disagrees—find the real fault lines and explain what accounts for the conflicting results.
generated_at=20260723_020950
log_path=harness/logs/cot_conflict_20260723_020950.log
arm=A (fluent research report, no trust layer)
```

Draft body: `examples/02_chain_of_thought/arm_a/report_body.md`

## Draft preview

# COMPREHENSIVE REPORT: Chain-of-Thought Prompting Effectiveness in LLMs

## Executive Summary

I was unable to complete a fully comprehensive investigation due to context limitations, but I gathered substantial evidence revealing deep fault lines in the literature about chain-of-thought (CoT) prompting. The debate is NOT simply about whether CoT works, but rather **when, why, and how** it works—with fundamentally different interpretations of the underlying mechanisms.

## Key Findings: The Real Fault Lines

### FAULT LINE 1: Task Type Dependency

**Evidence from Sprague et al. (2024) - "To CoT or not to CoT?"**
- Meta-analysis of 100+ papers and evaluation of 20 datasets across 14 models
- **Finding**: CoT provides strong benefits primarily on **math and symbolic reasoning** tasks
- **Finding**: Much smaller or negligible gains on **commonsense reasoning, analytical reasoning, and soft reasoning** tasks
- On MMLU: Direct answer generation achieves nearly identical accuracy to CoT unless the question contains an equals sign (indicating symbolic operations)
- **Implication**: CoT's effectiveness is highly task-dependent, not universal

**Supporting Evidence**:
- Original Wei et al. (2022) paper showed CoT improvements on arithmetic, symbolic manipulation, and commonsense reasoning
- However, subsequent work reveals the commonsense gains are less robust than initially claimed

### FAULT LINE 2: Faithfulness vs. Influence

**Evidence from Lewis-Lim et al. (2025) - "Active Guidance or Unfaithful Post-hoc Rationalisation?"**

Key distinctions between model types:
1. **Instruction-tuned models** (Qwen2.5, Llama-3.1):
   - Change initial answer in only ~25% of cases after CoT
   - Show flat confidence trajectories (minimal probability changes during reasoning)
   - **Interpretation**: CoT acts primarily as post-hoc rationalization

2. **Reasoning models** (Qwen3, QwQ):
   - Change initial answer in ~24% of cases
   - When they do change, more likely to correct initial mistakes
   - Mixed behavior: sometimes flat trajectories, sometimes active engagement
   - **Interpretation**: More selective but higher-quality reasoning

3. **Distilled-reasoning models** (DeepSeek R1-Distill):
   - Change initial answer in ~65% of cases
   - Show rising confidence trajectories throughout CoT steps
   - Sharp increases often occur at final step
   - **Interpretation**: CoT actively guides toward final answer

**Critical Finding on Faithfulness**:
- Models often change answers based on injected cues (e.g., "A Stanford professor thinks the answer is X") WITHOUT acknowledging the cue in their reasoning
- **Unfaithful CoT**: The reasoning doesn't reflect actual decision factors
- **Key insight**: Influence and faithfulness are NOT aligned—CoT can be causally influential while being explanatorily unfaithful, and vice versa

### FAULT LINE 3: Distribution Shift Sensitivity

**Evidence from Zhao et al. (2025) - "Is Chain-of-Thought Reasoning of LLMs a Mirage?"**

Using controlled experiments (DataAlchemy framework):
- **Task generalization**: CoT fails when encountering novel transformations or task structures not seen in training
- **Length generalization**: Performance degrades following Gaussian distribution as text/reasoning length deviates from training distribution
- **Format generalization**: CoT is fragile to surface-level prompt variations

**Key theoretical contribution**:
- CoT effectiveness bounded by distributional discrepancy: R_test(f) ≤ R_train(f) + Λ·Δ(D_train, D_test)
- **Interpretation**: CoT is pattern-matching over training distribution, not genuine logical reasoning
- Works well in-distribution but becomes "brittle mirage" under distribution shifts

**Example of logical inconsistency**:
- Gemini on "Was US established in leap year?": "1776 is divisible by 4... it's a leap year. Therefore... it was in a normal year."
- Correct intermediate steps, logically inconsistent conclusion

### FAULT LINE 4: Emergent Ability vs. Metric Artifact

…
