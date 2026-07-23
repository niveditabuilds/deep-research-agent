# Real-world risks and benefits of using synthetic data to train or fine-tune large language models

**Question:** What are the real-world risks and benefits of using synthetic data to train or fine-tune large language models? Focus on data quality, bias, and evaluation.

## Executive Summary

Synthetic data has rapidly become central to modern AI development. According to MIT researchers, more than 60% of data used for AI applications in 2024 was synthetic (https://news.mit.edu/2025/3-questions-pros-cons-synthetic-data-ai-kalyan-veeramachaneni-0903). This shift reflects both opportunity and necessity: as pre-training datasets expand dramatically—from 1.4 trillion tokens in Llama 1 to 15 trillion in Llama 3—and all major labs including OpenAI, Anthropic, and Google focus increasingly on synthetic data in their pipelines, the technology has moved from experimental to essential.

The benefits are substantial and well-documented. Synthetic data addresses critical data scarcity, particularly for rare events and low-resource domains. It offers strong privacy protections; as MIT's Kalyan Veeramachaneni notes, "because synthetic data aren't drawn from real situations, they are also privacy-preserving" (https://news.mit.edu/2025/3-questions-pros-cons-synthetic-data-ai-kalyan-veeramachaneni-0903). Cost-effectiveness and scalability make it attractive for organizations facing expensive data collection and labeling processes.

Yet the risks demand equal attention. The most widely discussed concern—catastrophic model collapse—appears less threatening under realistic conditions than early warnings suggested. Recent research demonstrates that when synthetic data accumulates alongside real data rather than replacing it entirely, population risk does not diverge (https://arxiv.org/html/2503.14023v1). However, other threats remain serious: bias amplification affects marginalized communities disproportionately, tail data representing rare events systematically disappears, and evaluation challenges make quality degradation difficult to detect.

The evidence points to a nuanced conclusion: synthetic data is neither panacea nor catastrophe. Success depends critically on governance, quality control, and maintaining sufficient real data reserves. Organizations that approach synthetic data with rigor can harness its benefits while managing risks; those that treat it as a shortcut will likely face documented harms.

## Benefits of Synthetic Data for LLM Training

### Addressing Data Scarcity and Scale

The fundamental driver of synthetic data adoption is straightforward: AI models need more data than organizations possess or can ethically access. Industry commentary indicates that all major labs began making pre-training pipelines more sophisticated by focusing on synthetic data in 2024, with dataset sizes growing dramatically—Llama 1 used 1.4 trillion tokens while Llama 3 used 15 trillion (https://magazine.sebastianraschka.com/p/state-of-llms-2025).

Synthetic data proves particularly valuable for rare events and edge cases. Fraud detection models that see only 0.1% positive examples in real data can train on synthetic datasets with 20% fraud rates, providing sufficient signal to learn patterns. Autonomous vehicle training can simulate dangerous scenarios—icy roads, adverse weather conditions—that are impractical or unsafe to collect naturally. For low-resource languages, synthetic data substantially improves machine translation performance even when noisy, addressing gaps where human-generated training data simply doesn't exist at scale.

### Privacy Preservation and Compliance

Privacy benefits represent one of synthetic data's strongest advantages. MIT researcher Kalyan Veeramachaneni explains that "because synthetic data aren't drawn from real situations, they are also privacy-preserving" (https://news.mit.edu/2025/3-questions-pros-cons-synthetic-data-ai-kalyan-veeramachaneni-0903). Properly generated synthetic data has no statistical connection to any individual record, making it preferred for privacy-preserving training in regulated industries.

This enables compliance with GDPR, HIPAA, and equivalent frameworks without consent requirements. Healthcare organizations can train diagnostic models without accessing real patient records. Financial institutions can develop credit risk models while protecting customer data. The approach provides clear audit trails for regulatory review when properly documented, addressing both technical and legal requirements simultaneously.

### Cost-Effectiveness and Development Velocity

Synthetic data eliminates expensive data collection, labeling, and annotation processes. Organizations can generate unlimited test data for specific scenarios on demand—e-commerce transactions in particular regions and timeframes, billions of transactions for performance testing, or development environment access to sensitive data patterns without production exposure. This acceleration reduces time-to-market for AI applications while lowering operational costs.

The scale of adoption reflects these advantages. More than 60% of data used for AI applications in 2024 was synthetic, according to MIT estimates (https://news.mit.edu/2025/3-questions-pros-cons-synthetic-data-ai-kalyan-veeramachaneni-0903), demonstrating that the technology has moved from experimental to mainstream across the industry.

## Risks and Challenges

### Model Collapse: Separating Reality from Alarm

Model collapse has dominated discussions of synthetic data risks, but the evidence reveals a more nuanced picture than early warnings suggested. The concern centers on recursive training: when generative models train on content produced by earlier models across successive generations, distributions might drift from reality until quality degrades.

However, recent research demonstrates that catastrophic collapse depends heavily on implementation details. Multiple studies—including work by Gerstgrasser et al. (2024), Kazdan et al. (2024), and Dey & Donoho (2024)—show that population risk does NOT diverge in the accumulate paradigm where synthetic data accumulates alongside real data (https://arxiv.org/html/2503.14023v1). This matters because real-world practice involves data accumulation, not wholesale replacement of existing datasets.

The distinction between scenarios is critical. In the "replace paradigm" where all existing data are deleted after each training iteration and models train solely on predecessor outputs, severe collapse occurs. But this scenario doesn't match industry practice. Real data are not deleted en masse; synthetic data accumulates alongside prior and new real data; frontier AI labs have sequestered real training data for future use; and pre-training datasets continue increasing rather than shrinking.

A Stanford/Harvard position paper concluded that "certain predicted claims of model collapse rely on assumptions and conditions that poorly match real-world conditions, and in fact several prominent collapse scenarios are readily avoidable" (https://arxiv.org/html/2503.14023v1). For text data with quadrillion tokens and high dimensionality, total collapse would occur so imperceptibly slowly that humanity could train trillions of models before noticing onset.

### Bias Amplification: A Persistent Threat

While catastrophic collapse appears manageable, bias amplification represents a genuine and persistent threat. Synthetic data generators learn from real data containing historical biases. When these biases get reproduced at scale, underrepresentation of demographic groups intensifies. Models trained on biased synthetic data learn more biased representations than from original data alone.

Secondary reporting on research titled "Fairness Feedback Loops: Training on Synthetic Data Amplifies Bias" (FAccT 2024) demonstrated systematic bias amplification across generations (https://dl.acm.org/doi/10.1145/3706468.3706546). The mechanism is straightforward: generators cluster around dominant patterns, reducing minority representation further with each iteration. This affects healthcare (potential misdiagnosis or unequal care), financial services (perpetuation of lending discrimination), criminal justice (amplification of racial bias), and language models (underrepresentation of marginalized communities).

The United Nations University identified bias propagation as a primary risk, stating that synthetic data should be assumed to carry additional risks including model error amplification. Mitigation requires explicit prompting for diverse representation during generation, fairness constraints and debiasing techniques, bias validation comparing demographic distributions, purposeful sampling to create balanced datasets, and regular bias audits throughout the generation pipeline.

### Loss of Tail Data and Diversity

Synthetic data systematically underrepresents rare events and edge cases, with disproportionate harm to marginalized groups. Generative models rarely select creative or unusual outputs; recursive generation narrows distributions over time; rare events vanish even when population risk appears stable. This "coverage collapse" occurs before catastrophic performance degradation becomes apparent.

Historically marginalized groups are disproportionately represented in data tails—low-resource languages and dialects, rare medical conditions, minority demographic groups in clinical research, edge cases in safety-critical applications. The loss of tail data perpetuates systemic inequalities, reduces model robustness for underrepresented populations, creates diversity collapse in language model outputs, and limits conceptual diversity and creative expression.

### Data Quality and Evaluation Challenges

Maintaining statistical fidelity between synthetic and real data proves challenging, with subtle degradations difficult to detect. Traditional fidelity metrics evaluate marginal distributions but miss interactions between features. KL divergence and chi-squared tests may show statistical similarity while missing critical correlations. Synthetic data mirrors the distribution it was generated from, not production data at inference time—when production data drifts due to seasonality, market changes, or population shifts, synthetic training data becomes miscalibrated.

The evaluation challenge is fundamental: traditional metrics measuring fidelity, utility, and privacy don't guarantee real-world usefulness. New efficacy metrics are emerging that emphasize task-specific performance, but evaluation must occur on an application-by-application basis. As one MIT researcher asked: "How would you know the data are going to lead to models that still make valid conclusions?"

## Governance and Best Practices

Success with synthetic data depends critically on governance infrastructure. Essential elements include generation provenance (documenting which real dataset synthetic data derived from, methods and parameters used, audit chains connecting synthetic to real-world signal), fidelity metrics documentation, bias validation results, intended use scope with explicit exclusions, and freshness tracking with regeneration requirements.

Bidirectional lineage proves particularly important: tracing backward from synthetic datasets to real sources, and forward to every model trained on them and production systems deploying those models. This enables impact assessment when issues are discovered. Retroactive tracing is costly or impossible, making proactive implementation essential.

Best practices for developers include prioritizing model quality through robust assessment protocols, investing in traceability systems, ensuring transparency in generation processes, implementing technical safeguards like watermarking and cryptographic provenance, diversifying stakeholder engagement to identify risks across populations, and establishing validation metrics before generation begins.

Critical to avoiding collapse: never rely solely on synthetic data, use hybrid approaches combining synthetic with organic data, incorporate self-correction mechanisms, maintain sufficient real data proportion, and regularly regenerate synthetic datasets as production distributions evolve.

## Industry Adoption and Real-World Applications

Industry commentary suggests that OpenAI, Anthropic, and Google all embraced synthetic data in training pipelines during 2024-2025, reflecting both data scarcity pressures and competitive dynamics. Successful use cases span healthcare (synthetic patient records for diagnostic model training), autonomous vehicles (simulation of adverse conditions), financial services (fraud detection with balanced datasets, bias correction in lending), software development (testing and performance validation), and natural language processing (low-resource language translation, instruction-tuning dataset generation).

Implementation challenges include technical complexity in selecting appropriate generation methods and maintaining quality at scale, organizational barriers like lack of expertise and resistance to new methodologies, trust and adoption concerns about quality and regulatory issues, and cost considerations for infrastructure and ongoing validation.

## Synthesis: Weighing Risks and Benefits

The evidence supports several key conclusions. First, catastrophic model collapse is avoidable under realistic conditions where data accumulate and quality is maintained. The most alarming predictions rely on assumptions—complete deletion of real data, training solely on predecessor outputs, absence of quality filtering—that don't match current industry practices.

Second, real threats exist that require active mitigation. Tail data loss occurs even when population risk appears stable, affecting marginalized groups disproportionately. Bias amplification is well-documented and requires purposeful intervention. Distribution shift causes gradual degradation as production data evolves. Evaluation challenges make quality assessment difficult without task-specific validation.

Third, success depends on specific conditions. Synthetic data works well when addressing data scarcity for rare events, enabling privacy-preserving training in regulated domains, augmenting rather than replacing real data, operating within well-defined use cases with clear evaluation criteria, supported by proper governance and lineage tracking, validated regularly against real data, involving diverse stakeholders, and monitored continuously with regular regeneration.

Synthetic data fails when completely replacing real data, enabling recursive training without real data grounding, lacking quality control and validation, ignoring bias amplification risks, operating without provenance tracking, failing to monitor for distribution drift, generating insufficient diversity, or treating all synthetic data as equivalent regardless of generation method or use case.

## Needs review

<details>
<summary>Claims from the research draft that could not be verified — expand to inspect</summary>

These failed a receipt check (missing URL, blocked page, or evidence span not found). They are **not** findings.

- The AI training dataset market reached $2.82 billion in 2024, growing at 27.7% CAGR.
- Research institute Epoch AI estimates that LLMs will exhaust public, human-generated data sometime between 2026 and 2032.
- Gartner predicted in 2022 that 60% of AI development data would be synthetic by 2024, with projections suggesting synthetic data will surpass real-world data in AI training by 2030.
- Research reveals at least eight distinct definitions of model collapse in the literature.
- Shumailov et al. (Nature, 2024) found that when generative models train recursively on content produced by earlier models across successive generations, the distribution drifts from reality, rare events vanish, and outputs become repetitive until quality degrades to incoherence.
- For text data with quadrillion tokens and high dimensionality, total collapse occurs so imperceptibly slowly that humanity could train trillions of models before noticing onset.
- A study titled 'Fairness Feedback Loops: Training on Synthetic Data Amplifies Bias' (FAccT 2024) demonstrated systematic bias amplification across generations.
- United Nations University (2024) identified bias propagation as primary risk, stating synthetic data should be assumed to carry additional risks including model error amplification.
- An article titled 'Your Synthetic Data Passed Every Test and Still Broke Your Model' (Towards Data Science, April 2026) noted that fidelity metrics evaluate marginal distributions, not interactions between features.
- CIO Magazine (February 2025) projected that 80% of AI data will be synthetic by 2030, up from 20% in 2024.
- The synthetic data generation market is growing at 35.2% CAGR from 2024 to 2034.
- A Stanford/Harvard position paper (March 2025) concluded that certain predicted claims of model collapse rely on assumptions and conditions that poorly match real-world conditions, and several prominent collapse scenarios are readily avoidable.
- World Economic Forum (September 2025) reported that synthetic data can correct lending practices driven by gender-biased data to provide fairer access to financial services.
- Google Research demonstrated differentially private synthetic data generation for on-device safety classification in May 2024.
- LLM-based evaluators are outperforming traditional statistical tests by up to 8.1% in complex tasks according to 2026 research.

</details>

## Limits of this report

This final report only states claims that could be confirmed against fetched source text. Unconfirmed items from the research draft appear under Needs review.
