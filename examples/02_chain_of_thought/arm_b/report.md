# Chain-of-thought prompting: effective reasoning strategy or improved output formatting?

**Question:** Is chain-of-thought prompting an effective reasoning strategy for LLMs, or does it primarily improve output formatting? The literature disagrees—find the real fault lines and explain what accounts for the conflicting results.

## Executive Summary

The debate over chain-of-thought (CoT) prompting has produced sharply conflicting claims about whether it enables genuine reasoning or merely improves output presentation. Recent large-scale empirical work reveals that this framing misses the real story: CoT effectiveness depends critically on task type, model architecture, and distributional context. A meta-analysis of over 100 papers evaluating 20 datasets across 14 models shows that CoT provides strong benefits primarily on math and symbolic reasoning tasks, but negligible gains on commonsense and analytical reasoning (https://arxiv.org/abs/2409.12183). Meanwhile, studies of model confidence trajectories reveal that instruction-tuned models show flat probability changes during reasoning—suggesting post-hoc rationalization rather than active inference—while different model families exhibit fundamentally different reasoning behaviors (https://arxiv.org/html/2510.16645v1).

The literature conflicts stem from researchers evaluating different task types, using different model architectures, and testing under different distributional conditions. What appears as disagreement about whether CoT "works" is actually evidence of a more nuanced reality: CoT is neither universal reasoning enhancement nor pure formatting trick, but rather a distribution-dependent capability that succeeds within specific boundaries and fails outside them.

## The Task-Type Fault Line

The most fundamental division in the literature concerns which tasks benefit from chain-of-thought prompting. Sprague et al.'s 2024 meta-analysis provides the clearest resolution: chain-of-thought prompting provides strong benefits primarily on math and symbolic reasoning tasks, but much smaller or negligible gains on commonsense reasoning, analytical reasoning, and soft reasoning tasks (https://arxiv.org/abs/2409.12183). This finding emerged from systematic evaluation across diverse benchmarks and model families, revealing a pattern obscured by earlier work that focused heavily on mathematical domains.

The distinction becomes stark when examining specific benchmarks. On MMLU, direct answer generation achieves nearly identical accuracy to chain-of-thought unless the question contains an equals sign indicating symbolic operations (https://arxiv.org/abs/2409.12183). This suggests that CoT's value lies not in general reasoning enhancement but in providing computational workspace for explicit symbolic manipulation—a finding that reconciles many apparently contradictory results in the literature.

The task-type dependency explains why early enthusiasm about CoT as a universal reasoning breakthrough gave way to more skeptical assessments. Researchers working primarily with mathematical and logical reasoning tasks observed genuine improvements, while those evaluating commonsense or analytical reasoning found minimal benefits. Both groups were correct within their evaluation contexts; the conflict arose from overgeneralizing domain-specific findings.

## The Faithfulness and Influence Divide

A second major fault line concerns whether chain-of-thought reasoning reflects genuine cognitive processes or serves as post-hoc rationalization. Analysis of model confidence trajectories reveals striking differences across model families. Instruction-tuned models show flat confidence trajectories with minimal probability changes during reasoning, suggesting chain-of-thought acts primarily as post-hoc rationalization (https://arxiv.org/html/2510.16645v1). These models appear to reach conclusions early and then generate explanatory text, rather than using the reasoning process to arrive at answers.

The picture becomes more complex when examining models trained with different objectives. When reasoning models do change their answer during chain-of-thought generation, they are more likely to correct initial mistakes compared to instruction-tuned models (https://arxiv.org/html/2510.16645v1). This suggests that training methodology fundamentally shapes how models use intermediate reasoning steps—some architectures treat CoT as genuine working memory, while others use it primarily for output formatting.

This distinction between influence and faithfulness matters because it reveals that chain-of-thought can be causally important for final answers while simultaneously being explanatorily unfaithful about the actual decision process. The reasoning chains may improve accuracy without accurately representing how the model reached its conclusion—a finding with significant implications for interpretability and trust.

## Distribution Shift Sensitivity

Perhaps the most damaging evidence against viewing CoT as genuine reasoning comes from controlled experiments on distribution shifts. Chain-of-thought fails when encountering novel transformations or task structures not seen in training, demonstrating poor task generalization (https://arxiv.org/html/2501.05465v2). Similarly, chain-of-thought performance degrades following a Gaussian distribution as text or reasoning length deviates from the training distribution (https://arxiv.org/html/2501.05465v2). These findings suggest that CoT success depends heavily on pattern matching against training data rather than flexible logical inference.

The fragility extends to superficial variations: chain-of-thought is fragile to surface-level prompt variations, demonstrating poor format generalization (https://arxiv.org/html/2501.05465v2). If CoT enabled genuine reasoning, it should be robust to rephrasing and formatting changes. The observed brittleness indicates that models have learned specific patterns of reasoning presentation rather than underlying logical principles.

This distribution sensitivity explains why CoT appears highly effective in some studies but fails in others. Evaluations using in-distribution test sets—where problems closely resemble training examples—show strong CoT benefits. Evaluations probing generalization to novel problem structures reveal sharp performance degradation. The conflicting results reflect different choices about how far to push models beyond their training distribution.

## The Emergence Controversy

Early claims that chain-of-thought reasoning emerged suddenly in models exceeding 100 billion parameters suggested a qualitative shift in model capabilities. However, the apparent emergence of chain-of-thought as an ability only in models over 100B parameters may be an artifact of discontinuous evaluation metrics (https://arxiv.org/abs/2304.15004). When researchers use continuous rather than threshold-based metrics, chain-of-thought performance shows smooth scaling rather than sharp emergence (https://arxiv.org/abs/2304.15004).

This finding reframes the emergence debate: what appeared as a sudden capability breakthrough was partially an artifact of how researchers measured performance. The underlying capability scales smoothly with model size, but discontinuous metrics created the illusion of a phase transition. This methodological insight explains why some researchers observed dramatic emergence while others found gradual improvement—they were using different measurement approaches on the same underlying phenomenon.

The emergence controversy illustrates a broader pattern in the CoT literature: apparently fundamental disagreements often trace to differences in evaluation methodology rather than genuine contradictions about model behavior. Recognizing these methodological fault lines is essential for interpreting conflicting claims.

## What Accounts for Conflicting Results

The literature conflicts arise from several systematic sources. First, task selection dramatically affects observed CoT effectiveness—studies emphasizing mathematical reasoning find strong benefits, while those focusing on commonsense reasoning find minimal gains. Second, model architecture and training methodology matter enormously: instruction-tuned models use CoT differently than models trained with reinforcement learning or distillation. Third, evaluation methodology choices about metrics, distribution matching, and generalization testing produce divergent results from the same underlying model capabilities.

These factors interact in complex ways. A study using instruction-tuned models on commonsense reasoning tasks with out-of-distribution test cases will find minimal CoT benefits. A study using distilled reasoning models on mathematical tasks with in-distribution evaluation will find strong benefits. Both results are valid within their contexts, but neither generalizes to all settings.

The conflicting results also reflect genuinely different interpretations of what constitutes "reasoning." Researchers who define reasoning as multi-step symbolic manipulation find that CoT enables it. Researchers who define reasoning as flexible inference from principles find that CoT fails to demonstrate it. These definitional differences ensure continued debate even as empirical evidence accumulates.

## Synthesis: A Bounded Capability

The evidence supports viewing chain-of-thought prompting as a bounded capability rather than either universal reasoning enhancement or pure formatting trick. CoT provides genuine computational benefits for tasks involving explicit symbolic manipulation, particularly mathematics and formal logic. It works by providing workspace for intermediate steps and by activating procedural knowledge patterns learned during training. However, it fails to enable flexible reasoning about novel problem structures or domains far from the training distribution.

The effectiveness varies systematically with model architecture: instruction-tuned models often use CoT as post-hoc rationalization, while models trained specifically for reasoning show more genuine engagement with intermediate steps. The capability scales smoothly with model size rather than emerging suddenly, though discontinuous metrics can create the appearance of sharp transitions.

This synthesis explains the literature conflicts: researchers observing CoT in its effective domain (mathematical reasoning, in-distribution tasks, appropriately trained models) see genuine benefits, while those probing its boundaries (commonsense reasoning, distribution shifts, instruction-tuned models) find limitations. Both perspectives capture real aspects of a complex, context-dependent phenomenon.

## Needs review

<details>
<summary>Claims from the research draft that could not be verified — expand to inspect</summary>

These failed a receipt check (missing URL, blocked page, or evidence span not found). They are **not** findings.

- Instruction-tuned models like Qwen2.5 and Llama-3.1 change their initial answer in only approximately 25% of cases after chain-of-thought reasoning.
- Distilled-reasoning models like DeepSeek R1-Distill change their initial answer in approximately 65% of cases after chain-of-thought reasoning.
- Models often change answers based on injected cues without acknowledging the cue in their reasoning, demonstrating unfaithful chain-of-thought.
- Chain-of-thought effectiveness is bounded by distributional discrepancy according to the formula R_test(f) ≤ R_train(f) + Λ·Δ(D_train, D_test).
- Gemini produced a logically inconsistent conclusion on the question 'Was US established in leap year?', stating '1776 is divisible by 4... it's a leap year. Therefore... it was in a normal year.'
- For reasoning questions, the same documents influence multiple questions within a task, containing procedural knowledge like formulas, code, and solution methods.
- Answers to reasoning questions rarely appear in the most influential training data, suggesting synthesis rather than memorization.
- For factual questions, models rely on distinct data for each question in a retrieval-like manner.
- Reasoning models like Qwen3 and QwQ change their initial answer in approximately 24% of cases after chain-of-thought reasoning.
- Distilled-reasoning models show rising confidence trajectories throughout chain-of-thought steps, with sharp increases often occurring at the final step.

</details>

## Limits of this report

This final report only states claims that could be confirmed against fetched source text. Unconfirmed items from the research draft appear under Needs review.
