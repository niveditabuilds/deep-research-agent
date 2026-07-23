# Research draft (Arm A)

**Question:** Is chain-of-thought prompting an effective reasoning strategy for LLMs, or does it primarily improve output formatting? The literature disagrees—find the real fault lines and explain what accounts for the conflicting results.

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

**Evidence from Schaeffer et al. (2023) - "Are Emergent Abilities a Mirage?"**

- Original claims: CoT is an "emergent ability" appearing only in models >100B parameters
- **Counter-evidence**: Apparent emergence may be artifact of discontinuous evaluation metrics
- With continuous metrics, performance shows smooth scaling rather than sharp emergence
- **Implication**: The "magical" appearance of CoT reasoning may be measurement artifact

### FAULT LINE 5: Procedural vs. Factual Knowledge

**Evidence from Ruis et al. (2024) - "Procedural Knowledge in Pretraining Drives Reasoning"**

Investigated what pretraining data influences model outputs:
- **Factual questions**: Models rely on distinct data for each question (retrieval-like)
- **Reasoning questions**: Same documents influence multiple questions within a task
- **Key finding**: Influential documents contain **procedural knowledge** (formulas, code, solution methods) rather than specific answers
- Answers to reasoning questions rarely appear in most influential training data
- **Interpretation**: CoT synthesizes procedural patterns from training data, not memorization

### FAULT LINE 6: Model Size and Training Method

**Evidence from multiple sources**:

1. **Original emergence claim**: CoT only works in models >100B parameters (Wei et al. 2022)
2. **Distillation findings**: Smaller models (7B-32B) can exhibit strong CoT reliance when distilled from reasoning models
3. **Training method matters**: 
   - Instruction-tuned models: Less CoT reliance
   - RL-trained reasoning models: Selective but effective CoT
   - Distilled models: Heavy CoT dependence

## What Accounts for Conflicting Results?

### 1. **Evaluation Methodology Differences**
- **Metric choice**: Discontinuous vs. continuous metrics produce different emergence patterns
- **Task selection**: Math-heavy benchmarks vs. commonsense reasoning show different CoT benefits
- **Distribution matching**: In-distribution vs. out-of-distribution testing yields vastly different results

### 2. **Model Architecture and Training**
- Different model families (instruction-tuned vs. reasoning vs. distilled) use CoT differently
- Training data composition affects what procedural knowledge is available
- RLHF may reduce faithfulness while improving human preference alignment

### 3. **Definition of "Reasoning"**
- **Genuine reasoning view**: CoT enables logical inference and problem decomposition
- **Pattern matching view**: CoT interpolates/extrapolates from training distribution patterns
- **Hybrid view**: CoT provides working memory/scratchpad for intermediate computation

### 4. **Confounding Factors**
- **Length effects**: Longer outputs may improve accuracy independent of reasoning quality
- **Format effects**: Step-by-step structure may help model attention mechanisms
- **Self-consistency**: Multiple sampling + majority voting improves results regardless of individual chain quality

## Candidate Interpretations

### INTERPRETATION A: CoT as Genuine Reasoning Enhancement
**Support**: 
- Improves performance on complex math/logic tasks
- Enables multi-step problem decomposition
- Distilled models show strong CoT dependence

**Against**:
- Fails on out-of-distribution tasks
- Often produces logically inconsistent chains
- Doesn't improve commonsense reasoning consistently

### INTERPRETATION B: CoT as Sophisticated Pattern Matching
**Support**:
- Performance bounded by training distribution similarity
- Relies on procedural knowledge in pretraining data
- Fails under distribution shifts
- Can be unfaithful (doesn't reflect actual decision process)

**Against**:
- Does enable novel problem solving within learned patterns
- Shows genuine error correction in some models
- Procedural knowledge synthesis is more than pure memorization

### INTERPRETATION C: CoT as Working Memory/Scratchpad
**Support**:
- Provides space for intermediate computation
- Helps with tasks requiring state tracking
- Analogous to human working memory

**Against**:
- Doesn't explain task-type dependency
- Doesn't explain why it fails on some reasoning types

### INTERPRETATION D: CoT as Output Formatting Improvement
**Support**:
- Instruction-tuned models show flat confidence trajectories
- Post-hoc rationalization common
- May primarily help human interpretability

**Against**:
- Distilled models show genuine influence on answers
- Does improve accuracy on specific task types
- More than just reformatting for some models

## Uncertainties and Open Questions

1. **Mechanism uncertainty**: Exact computational mechanisms during CoT generation remain unclear
2. **Generalization boundaries**: Precise conditions for when CoT generalizes vs. fails not fully mapped
3. **Training data role**: Exact procedural knowledge patterns needed for different reasoning types unknown
4. **Faithfulness-performance tradeoff**: Whether faithful CoT is necessary for good performance unclear
5. **Scaling laws**: How CoT effectiveness scales with future model sizes uncertain

## Conclusion

The literature conflict stems from **fundamentally different evaluation contexts and interpretations**:

- CoT IS effective for **math and symbolic reasoning** in **in-distribution or near-distribution** settings
- CoT effectiveness DECREASES for **commonsense/soft reasoning** and **out-of-distribution** tasks
- CoT mechanism varies by **model type**: post-hoc rationalization (instruction-tuned) vs. active guidance (distilled)
- CoT is NOT always faithful, even when influential
- CoT appears to work through **procedural knowledge synthesis** from training data rather than pure retrieval or pure logical reasoning

**The real answer**: CoT is neither purely "effective reasoning" nor purely "output formatting"—it's a **distribution-dependent pattern synthesis mechanism** that works well within learned procedural knowledge boundaries but fails as a general reasoning strategy.

\boxed{Chain-of-thought prompting is effective for math and symbolic reasoning tasks within training distribution boundaries, working through procedural knowledge synthesis rather than genuine logical reasoning, with effectiveness varying by model type and training method, and often producing unfaithful explanations that don't reflect actual decision processes}

## Sources consulted (from tool trail)

- https://gregrobison.medium.com/chain-of-thought-in-large-language-models-elicited-reasoning-or-constrained-imitation-5e4ee0c811ad
- https://arxiv.org/html/2510.16645v1
- https://www.facebook.com/groups/vibecodinglife/posts/1913520232569838/
- https://www.facebook.com/groups/claudeaicommunity/posts/1232337722266726/
- https://www.facebook.com/groups/MontrealAI/posts/2261060901022396/
- https://www.reddit.com/r/artificial/comments/1txp7ah/the_strange_thing_about_llm_reasoning_research/
- https://www.linkedin.com/posts/ujjyainimitra_what-if-prompting-llms-was-a-battlefield-activity-7426476173402079232-i662
- https://aclanthology.org/2025.findings-acl.640.pdf
- https://www.promptingguide.ai/techniques/cot
- https://www.lesswrong.com/posts/vRpLPZpmECCfxHfv6/paper-prompt-optimization-makes-misalignment-legible
- https://link.springer.com/article/10.1007/s44443-025-00353-3
- https://openreview.net/forum?id=emjPKK11Oo
- https://www.mindstudio.ai/blog/what-is-chain-of-thought-faithfulness-ai-reasoning
- https://donaldye.com/nldd
- https://www.jdhwilkins.com/why-think-step-by-step-no-longer-works-for-modern-ai-models/
- https://www.researchgate.net/publication/401457121_Chain-Of-Thought_Prompting_Elicits_Reasoning_in_Large_Language_Models
- https://aclanthology.org/2025.emnlp-main.1516.pdf
- https://www.preprints.org/manuscript/202512.2242
- https://github.com/samlewislim/
- https://arxiv.org/html/2508.01191v3
- https://www.facebook.com/MontrealAI/posts/chain-of-thought-prompting-elicits-reasoning-in-large-language-modelswei-et-al-a/1108272151483169/
- https://www.projectpro.io/article/chain-of-thought-prompting-in-llms/981
- http://scis.scichina.com/en/2026/161101.pdf
- https://www.mercity.ai/blog-post/guide-to-chain-of-thought-prompting/
- https://dev.to/abhishek_gautam-01/tree-of-thought-prompting-4l08
- https://www.emergentmind.com/topics/zero-shot-cot-settings
- https://dl.acm.org/doi/10.1145/3832753
- https://aclanthology.org/2025.findings-acl.782.pdf
- https://arxiv.org/abs/2409.12183
- https://www.semanticscholar.org/paper/To-CoT-or-not-to-CoT-Chain-of-thought-helps-mainly-Sprague-Yin/7362b81b808ebafd403eaec6f60a124340d68d71
- https://www.linkedin.com/pulse/cot-chain-of-thought-helps-mainly-math-symbolic-vlad-bogolin-uepmc
- https://proceedings.iclr.cc/paper_files/paper/2025/file/ead542f13a38179d1b55b88610f959a1-Paper-Conference.pdf
- https://github.com/Zayne-sprague/To-CoT-or-not-to-CoT
- https://x.com/ZayneSprague/status/1915586487548338577
- https://www.facebook.com/groups/698593531630485/posts/1339083867581445/
- https://huggingface.co/papers/2409.12183
- https://levelup.gitconnected.com/to-cot-or-not-to-cot-do-llms-really-need-chain-of-thought-5a59698c90bb
- https://www.emergentmind.com/topics/chain-of-thoughts-cot-data
- https://arxiv.org/abs/2409.12183v3
- https://www.reddit.com/r/LocalLLaMA/comments/1odq73r/is_chain_of_thought_still_an_emergent_behavior/
- https://www.reddit.com/r/LocalLLaMA/comments/1odq73r/is_chain_of_thought_still_an_emergent_behavior/nkvsrnq/
- https://www.instagram.com/reel/DVCmvuzk9V_/
- https://www.emergentmind.com/topics/few-shot-and-chain-of-thought-prompting
- https://www.linkedin.com/pulse/week-10-scaling-laws-emergent-abilities-model-kausik-kumar-qeldc
- https://arxiv.org/html/2501.05465v2
- https://www.facebook.com/61568751478861/posts/-a-new-open-model-is-quietly-getting-attention-in-the-ai-community-and-it-might-/122174374778625049/
- https://dl.acm.org/doi/full/10.1145/3744746
- https://aclanthology.org/2025.emnlp-main.1659.pdf
- https://arxiv.org/abs/2304.15004
- https://www.dhiria.com/en/blog/emergent-abilities-in-large-language-models-reality-or-mirage
- https://medium.com/@marketing_novita.ai/are-emergent-abilities-of-large-language-models-a-mirage-or-not-c53cd56d8686
- https://openreview.net/forum?id=ITw9edRDlD
- https://www.clawrxiv.io/abs/2603.00378
- https://www.researchgate.net/publication/401456948_Are_Emergent_Abilities_of_Large_Language_Models_a_Mirage
- https://iotdigitaltwinplm.com/emergent-abilities-llm-scale-explained-2026/
- https://memx.app/glossary/emergent-capabilities/
- https://vinayakajyothi.com/blog/2026-02-04-emergent-abilities-llms/
- https://arxiv.org/abs/2304.15004v2
- https://marcohkvanhurne.medium.com/a-field-trip-through-the-inner-world-of-an-llm-we-dont-fully-understand-5dbb0d1b8f72
- https://www.instagram.com/reel/DaVcwJQiSuZ/
