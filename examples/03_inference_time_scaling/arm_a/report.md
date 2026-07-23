# Arm A — Baseline research report

**Question:** What is the current state of inference-time compute scaling for LLM reasoning? Separate what has been empirically validated from what is still speculative, and identify where the evidence is too thin to draw conclusions.

Fluent harness output with web search. No claim ledger.

## Metadata

```
task_id=inference_scaling_20260723_021344
config=agent_mvp_anthropic
question=What is the current state of inference-time compute scaling for LLM reasoning? Separate what has been empirically validated from what is still speculative, and identify where the evidence is too thin to draw conclusions.
generated_at=20260723_021344
log_path=/Users/nivedita/Desktop/Interviews /Reinforce Labs/harness/logs/inference_scaling_20260723_021344.log
arm=A (fluent research report, no trust layer)
```

Draft body: `examples/03_inference_time_scaling/arm_a/report_body.md`

## Draft preview

Based on my comprehensive research, I'll now provide you with a detailed report on the current state of inference-time compute scaling for LLM reasoning, clearly separating empirically validated findings from speculative claims and identifying areas with insufficient evidence.

---

# Comprehensive Report: Inference-Time Compute Scaling for LLM Reasoning

## Executive Summary

Inference-time compute scaling (also called test-time compute or test-time scaling) has emerged as a major research direction in 2024-2026, with substantial empirical validation but also significant open questions. The core finding—that allocating more compute at inference time can improve reasoning performance—is well-established, but the relationship is far more nuanced than initially believed.

---

## I. EMPIRICALLY VALIDATED FINDINGS

### A. Core Scaling Behaviors

**1. Basic Positive Scaling (VALIDATED)**
- **Finding**: Increasing inference compute generally improves performance on mathematical and coding tasks up to a point
- **Evidence**: 
  - Multiple studies across AIME, MATH-500, GPQA benchmarks show accuracy improvements with increased compute
  - DeepSeek-R1 achieved 79.8% on AIME 2024 (vs. baseline ~30-40%)
  - OpenAI's o1 and o3 models demonstrate substantial improvements on reasoning benchmarks
- **Scope**: Well-validated for mathematical reasoning, competitive programming, and formal logic tasks

**2. Diminishing Returns and Overthinking (VALIDATED)**
- **Finding**: Marginal utility decreases substantially at higher compute budgets; extended reasoning can degrade performance
- **Evidence from "Overthinking in LLM Test-Time Compute Scaling" (Zhou et al., 2026)**:
  - Marginal utility turns negative beyond 12K tokens for DeepSeek-R1-32B
  - "Flip ratio" (negative flips/positive flips) exceeds 1.0 at ~7K tokens, indicating overthinking
  - 67.5% of negative flips involve genuine overthinking where models explicitly reconsider and reject correct answers
  - Statistical significance confirmed via bootstrap analysis (95% CI)
- **Key metrics**: 
  - Early tokens provide +3.2% accuracy per 500 tokens
  - Beyond 12K tokens: negative marginal utility
  - Accuracy can drop 0.9% from 12K to 16K tokens

**3. Model-Dependent Behavior (VALIDATED)**
- **Finding**: Different model families exhibit distinct "reasoning horizons" based on training methodology
- **Evidence from "The Art of Scaling Test-Time Compute" (Agarwal et al., 2025)**:
  - **Short-horizon models** (R1, QwQ-32B, DAPO-32B trained with GRPO): Shorter traces consistently more accurate regardless of problem difficulty
  - **Long-horizon models** (Qwen3-32B, GPT-OSS-120B trained with alternative RL methods): Shorter traces better for easy problems, longer traces better for hard problems
  - Training algorithm (GRPO vs. GSPO) strongly correlates with length bias patterns
- **Implication**: No universal optimal strategy exists

**4. Problem Difficulty Modulation (VALIDATED)**
- **Finding**: Optimal compute allocation varies dramatically with problem difficulty
- **Evidence**:
  - Easy problems (Level 1-2 MATH): Peak at ~1.5K tokens
  - Hard problems (Level 5 MATH): Benefit up to ~8K tokens
  - Overthinking threshold: 2K tokens for easy problems vs. 8K for hard problems
- **Correlation**: Problem difficulty correlates with trace length across all models (validated across AIME 2024, 2025-I, 2025-II, GPQA)

**5. Parallel Sampling Methods (VALIDATED)**
- **Self-Consistency/Majority Voting**: Well-established improvements
  - Generates multiple reasoning paths, selects most frequent answer
  - Consistently improves accuracy across benchmarks
  - Trade-off: High token cost (often 10x vs. single generation)
- **Best-of-N sampling**: Empirically validated but compute-intensive
- **Short-m@k**: Selecting shortest k traces from N samples can outperform full majority voting in some settings

**6. Beam Search Limitations (VALIDATED)**
- **Finding**: Beam search shows inverse or no scaling for reasoning ta…
