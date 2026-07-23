# Internal audit ledger (not user-facing)

Confidence = source tier. Grounding fail ⇒ unsupported regardless of tier.

| # | Claim | Evidence | Source | Tier (confidence) | Grounding | Coverage |
|---|---|---|---|---|---|---|
| 1 | Chain-of-thought prompting provides strong benefits primarily on math and symbolic reasoning tasks, but much smaller or negligible gains on commonsense reasoning, analytical reasoning, and soft reasoning tasks. | Meta-analysis of 100+ papers and evaluation of 20 datasets across 14 models | https://arxiv.org/abs/2409.12183 | 1 | pass | ok |
| 2 | On MMLU, direct answer generation achieves nearly identical accuracy to chain-of-thought unless the question contains an equals sign indicating symbolic operations. | Direct answer generation achieves nearly identical accuracy to CoT unless the question contains an equals sign | https://arxiv.org/abs/2409.12183 | 1 | pass | ok |
| 3 | Instruction-tuned models like Qwen2.5 and Llama-3.1 change their initial answer in only approximately 25% of cases after chain-of-thought reasoning. | Change initial answer in only ~25% of cases after CoT | https://arxiv.org/html/2510.16645v1 | 1 | fail (unsupported) | ok |
| 4 | Distilled-reasoning models like DeepSeek R1-Distill change their initial answer in approximately 65% of cases after chain-of-thought reasoning. | Change initial answer in ~65% of cases | https://arxiv.org/html/2510.16645v1 | 1 | fail (unsupported) | ok |
| 5 | Instruction-tuned models show flat confidence trajectories with minimal probability changes during reasoning, suggesting chain-of-thought acts primarily as post-hoc rationalization. | Show flat confidence trajectories (minimal probability changes during reasoning) | https://arxiv.org/html/2510.16645v1 | 1 | pass | ok |
| 6 | Models often change answers based on injected cues without acknowledging the cue in their reasoning, demonstrating unfaithful chain-of-thought. | Models often change answers based on injected cues (e.g., 'A Stanford professor thinks the answer is X') WITHOUT acknowledging the cue in their reasoning | https://arxiv.org/html/2510.16645v1 | 1 | fail (unsupported) | ok |
| 7 | Chain-of-thought effectiveness is bounded by distributional discrepancy according to the formula R_test(f) ≤ R_train(f) + Λ·Δ(D_train, D_test). | R_test(f) ≤ R_train(f) + Λ·Δ(D_train, D_test) | https://arxiv.org/html/2501.05465v2 | 1 | fail (unsupported) | ok |
| 8 | Chain-of-thought performance degrades following a Gaussian distribution as text or reasoning length deviates from the training distribution. | Performance degrades following Gaussian distribution as text/reasoning length deviates from training distribution | https://arxiv.org/html/2501.05465v2 | 1 | pass | ok |
| 9 | Chain-of-thought fails when encountering novel transformations or task structures not seen in training, demonstrating poor task generalization. | Task generalization: CoT fails when encountering novel transformations or task structures not seen in training | https://arxiv.org/html/2501.05465v2 | 1 | pass | ok |
| 10 | Gemini produced a logically inconsistent conclusion on the question 'Was US established in leap year?', stating '1776 is divisible by 4... it's a leap year. Therefore... it was in a normal year.' | 1776 is divisible by 4... it's a leap year. Therefore... it was in a normal year | https://arxiv.org/html/2501.05465v2 | 1 | fail (unsupported) | ok |
| 11 | The apparent emergence of chain-of-thought as an ability only in models over 100B parameters may be an artifact of discontinuous evaluation metrics. | Apparent emergence may be artifact of discontinuous evaluation metrics | https://arxiv.org/abs/2304.15004 | 1 | pass | ok |
| 12 | With continuous metrics, chain-of-thought performance shows smooth scaling rather than sharp emergence. | With continuous metrics, performance shows smooth scaling rather than sharp emergence | https://arxiv.org/abs/2304.15004 | 1 | pass | ok |
| 13 | For reasoning questions, the same documents influence multiple questions within a task, containing procedural knowledge like formulas, code, and solution methods. | Same documents influence multiple questions within a task... contain procedural knowledge (formulas, code, solution methods) | https://proceedings.iclr.cc/paper_files/paper/2025/file/ead542f13a38179d1b55b88610f959a1-Paper-Conference.pdf | 3 | fail (unsupported) | ok |
| 14 | Answers to reasoning questions rarely appear in the most influential training data, suggesting synthesis rather than memorization. | Answers to reasoning questions rarely appear in most influential training data | https://proceedings.iclr.cc/paper_files/paper/2025/file/ead542f13a38179d1b55b88610f959a1-Paper-Conference.pdf | 3 | fail (unsupported) | ok |
| 15 | For factual questions, models rely on distinct data for each question in a retrieval-like manner. | Factual questions: Models rely on distinct data for each question (retrieval-like) | https://proceedings.iclr.cc/paper_files/paper/2025/file/ead542f13a38179d1b55b88610f959a1-Paper-Conference.pdf | 3 | fail (unsupported) | ok |
| 16 | The Sprague et al. 2024 study evaluated 20 datasets across 14 models in their meta-analysis of chain-of-thought prompting. | evaluation of 20 datasets across 14 models | https://arxiv.org/abs/2409.12183 | 1 | pass | ok |
| 17 | Reasoning models like Qwen3 and QwQ change their initial answer in approximately 24% of cases after chain-of-thought reasoning. | Change initial answer in ~24% of cases | https://arxiv.org/html/2510.16645v1 | 1 | fail (unsupported) | ok |
| 18 | When reasoning models do change their answer, they are more likely to correct initial mistakes compared to instruction-tuned models. | When they do change, more likely to correct initial mistakes | https://arxiv.org/html/2510.16645v1 | 1 | pass | ok |
| 19 | Distilled-reasoning models show rising confidence trajectories throughout chain-of-thought steps, with sharp increases often occurring at the final step. | Show rising confidence trajectories throughout CoT steps... Sharp increases often occur at final step | https://arxiv.org/html/2510.16645v1 | 1 | fail (unsupported) | ok |
| 20 | Chain-of-thought is fragile to surface-level prompt variations, demonstrating poor format generalization. | Format generalization: CoT is fragile to surface-level prompt variations | https://arxiv.org/html/2501.05465v2 | 1 | pass | ok |

## Tier counts

- Tier 1: 17
- Tier 2: 0
- Tier 3: 3
- Unsupported (grounding fail): 10
