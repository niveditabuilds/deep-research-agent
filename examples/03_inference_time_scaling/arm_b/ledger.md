# Internal audit ledger (not user-facing)

Confidence = source tier. Grounding fail ⇒ unsupported regardless of tier.

| # | Claim | Evidence | Source | Tier (confidence) | Grounding | Coverage |
|---|---|---|---|---|---|---|
| 1 | DeepSeek-R1 achieved 79.8% accuracy on AIME 2024. | 79.8% on AIME 2024 | https://arxiv.org/html/2604.10739v1 | 1 | fail (unsupported) | ok |
| 2 | Marginal utility of inference-time compute turns negative beyond 12K tokens for DeepSeek-R1-32B. | Marginal utility turns negative beyond 12K tokens for DeepSeek-R1-32B | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 3 | The flip ratio (negative flips/positive flips) exceeds 1.0 at approximately 7K tokens, indicating overthinking. | Flip ratio (negative flips/positive flips) exceeds 1.0 at ~7K tokens | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 4 | 67.5% of negative flips involve genuine overthinking where models explicitly reconsider and reject correct answers. | 67.5% of negative flips involve genuine overthinking where models explicitly reconsider and reject correct answers | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 5 | Early tokens provide +3.2% accuracy per 500 tokens in inference-time compute scaling. | Early tokens provide +3.2% accuracy per 500 tokens | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 6 | Accuracy can drop 0.9% from 12K to 16K tokens due to overthinking. | Accuracy can drop 0.9% from 12K to 16K tokens | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 7 | Short-horizon models (R1, QwQ-32B, DAPO-32B) trained with GRPO show shorter traces that are consistently more accurate regardless of problem difficulty. | Short-horizon models (R1, QwQ-32B, DAPO-32B trained with GRPO): Shorter traces consistently more accurate regardless of problem difficulty | http://bair.berkeley.edu/blog/2026/05/08/adaptive-parallel-reasoning/ | 2 | fail (unsupported) | ok |
| 8 | Long-horizon models (Qwen3-32B, GPT-OSS-120B) trained with alternative RL methods show shorter traces better for easy problems but longer traces better for hard problems. | Long-horizon models (Qwen3-32B, GPT-OSS-120B trained with alternative RL methods): Shorter traces better for easy problems, longer traces better for hard problems | http://bair.berkeley.edu/blog/2026/05/08/adaptive-parallel-reasoning/ | 2 | fail (unsupported) | ok |
| 9 | Training algorithm (GRPO vs. GSPO) strongly correlates with length bias patterns in reasoning models. | Training algorithm (GRPO vs. GSPO) strongly correlates with length bias patterns | http://bair.berkeley.edu/blog/2026/05/08/adaptive-parallel-reasoning/ | 2 | fail (unsupported) | ok |
| 10 | Easy problems (Level 1-2 MATH) peak in performance at approximately 1.5K tokens. | Easy problems (Level 1-2 MATH): Peak at ~1.5K tokens | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 11 | Hard problems (Level 5 MATH) benefit from inference-time compute up to approximately 8K tokens. | Hard problems (Level 5 MATH): Benefit up to ~8K tokens | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 12 | The overthinking threshold is 2K tokens for easy problems versus 8K tokens for hard problems. | Overthinking threshold: 2K tokens for easy problems vs. 8K for hard problems | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 13 | Beam search shows inverse or no scaling for reasoning tasks, with performance degrading monotonically as beam size increases for short-horizon models. | Performance degrades monotonically as beam size increases for short-horizon models | http://bair.berkeley.edu/blog/2026/05/08/adaptive-parallel-reasoning/ | 2 | pass | ok |
| 14 | Self-consistency and majority voting methods consistently improve accuracy across benchmarks but have high token cost, often 10x versus single generation. | Trade-off: High token cost (often 10x vs. single generation) | https://magazine.sebastianraschka.com/p/categories-of-inference-time-scaling | 3 | fail (unsupported) | ok |
| 15 | Most validation studies on inference-time compute scaling are limited to less than 32K tokens. | Most studies limited to <32K tokens |  | 3 | fail (unsupported) | low |
| 16 | Statistical significance of overthinking effects was confirmed via bootstrap analysis with 95% confidence intervals. | Statistical significance confirmed via bootstrap analysis (95% CI) | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 17 | Studies on inference-time compute scaling primarily focus on models ranging from 7B to 235B parameters. | Studies primarily on 7B-235B parameter models |  | 3 | fail (unsupported) | low |
| 18 | R1-32B is a distilled model that shows similar patterns to R1. | R1-32B (distilled) shows similar patterns to R1 | https://arxiv.org/html/2604.10739v1 | 1 | fail (unsupported) | ok |
| 19 | Most inference-time compute scaling research has been validated on mathematical reasoning benchmarks including AIME, MATH-500, and GPQA. | Multiple studies across AIME, MATH-500, GPQA benchmarks | https://arxiv.org/html/2604.10739v1 | 1 | pass | ok |
| 20 | Short-m@k (selecting shortest k traces from N samples) can outperform full majority voting in some settings. | Short-m@k: Selecting shortest k traces from N samples can outperform full majority voting in some settings | http://bair.berkeley.edu/blog/2026/05/08/adaptive-parallel-reasoning/ | 2 | fail (unsupported) | ok |

## Tier counts

- Tier 1: 12
- Tier 2: 5
- Tier 3: 3
- Unsupported (grounding fail): 9
