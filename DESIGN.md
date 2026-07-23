# Deep Research Agent — Design Doc (V2)

**Status:** Draft  
**Scope:** Full system design + thin MVP cut

---

## 1. Goal

Build a research agent that answers an open-ended question using the live web, then returns a report where every claim is tied to evidence and labeled by **source tier** and **grounding**.

We optimize for trustworthiness under time pressure, not for longest reports.

---

## 2. Problem

Tool-using research agents already plan, search, and summarize. The failure mode that matters in practice:

- Claims are mixed into fluent prose
- Citations look real but don’t support the sentence
- A Reddit thread and a peer-reviewed paper look equally “cited”

Readers can’t tell what to trust.

---

## 3. Approach

Two layers:

1. **Research harness** — plan, call tools, optionally delegate to workers, retry failures, log the run, synthesize a draft report.
2. **Trust layer (ours)** — split claims from evidence, assign a source tier, check grounding, emit a claim ledger.

The harness gets information. The trust layer decides how much to trust each claim.

**Confidence = source tier (+ grounding).** We do not use a separate high/medium/low confidence score. Tier is the confidence signal the reader sees. Grounding is the gate: if the receipt fails, the claim is **unsupported** regardless of tier.

---

## 3.1 How this differs from related systems

**Anthropic multi-agent research**
- Similar: lead agent + isolated workers, tools, final synthesis.
- Different: their verification/citation pass is largely a **final audit**; effort scaling is mostly **prompt heuristics**. We add an explicit **claim ledger** where each claim carries a **source tier as confidence**, and grounding can fail a claim even when a citation looks present.

**OpenAI Deep Research**
- Similar: multi-step web research and a polished long-form report.
- Different: output is optimized for a fluent brief. Ours is optimized for an **auditable ledger** — claim / evidence / url / tier — so a Reddit-backed sentence cannot look as trusted as an arXiv-backed one.

---

## 4. Architecture

```
User question
    → Main agent (plan / decide)
        → Tools (search, fetch/read)  and/or  Worker agents
    → Draft findings + sources
    → Trust layer
        → Claim–evidence split
        → Source tier
        → Grounding check
    → Final report (prose + claim ledger)
```

### 4.1 Main agent

Owns the run. Each turn it either:

- calls a tool, or
- delegates a subtask to a worker, or
- stops and synthesizes

It keeps the global plan and final assembly. Workers do not talk to each other.

### 4.2 Worker agents (optional)

Specialists with their own tool access (usually search + read).  
Main agent invokes a worker when a chunk of research should be isolated (e.g. “find primary sources on bias in synthetic data”).

**When to use workers at all:** only if the question splits into several independent research paths and one context window is not enough. Simple questions stay single-agent.

### 4.3 Tools

Minimum set:

| Tool | Job |
|---|---|
| Search | Find candidate URLs |
| Fetch / read | Pull page or doc text |
| (Optional) Code sandbox | Tables, light analysis |

**Failure behavior:** retry with backoff → if still failing, mark that facet **low coverage** (search/fetch did not yield usable evidence) and continue. Surface it in the report. Do not drop it silently.

### 4.4 Run loop, stopping, and context

- Structured turns: think → act → observe
- On bad tool calls / timeouts / stuck repeats: roll back the bad turn and retry with the error surfaced
- Full trace logged (plan, tool calls, worker calls, raw results)

**Stopping (harness defaults we keep):**
- Stop the tool loop when the model returns no more tool calls, or `max_turns` is hit, then generate a final summary
- On context overflow: summarize / trim and still emit a final answer rather than dying mid-run  
  (MVP does not add a custom “earned re-search” stop policy; that is full design.)

**Context / memory (what the harness does today):**
- In-run message history only — not a long-term memory DB
- Workers return condensed findings so the main agent is not flooded with raw pages
- Old bulky tool payloads can be trimmed (`keep_tool_result`) as the run grows
- Trace log is the durable record for debugging

### 4.5 Trust layer

Runs **after** the research draft is produced.

**MVP:** one trust pass, then emit the ledger. No automatic second search.  
**Full design:** if many claims are unsupported or Tier-3-only, trigger one more targeted search pass.

**Claim–evidence split**  
LLM proposes rows from the draft; grounding is the gate (no match → unsupported):

- `claim`
- `evidence` (short quote or span)
- `source_url`

**Source tiers (= confidence labels)**

| Tier (confidence) | Examples | How we assign (MVP rules) |
|---|---|---|
| **1** (highest) | Papers, arXiv, official docs, standards, government | Host matches: `arxiv.org`, `*.gov`, `*.edu` paper/docs paths, known standards bodies, publisher domains on an allowlist |
| **2** | Reputable news, established tech press, major eng blogs, conference talks | Allowlist of known outlets (e.g. major news/tech pubs); conference/talk domains |
| **3** (lowest) | Social, forums, Reddit, random blogs, SEO content | Default for anything not matched above |

Tier is taken from the **best grounding source** for that claim. Unknown host → Tier 3.

**Grounding check (MVP = hard checks only)**

1. URL resolves
2. Evidence span (or key number/name/date) appears in the fetched text

Soft “does this span actually support the claim?” judge is **full design only** (see risks).

Rules:

- Grounding fail → **unsupported** (tier does not save it)
- Only Tier 3 support → keep the claim, label Tier 3 (low confidence) explicitly
- Tier is source-quality confidence, not proof the claim is true

**Final report (Arm B / product output)**

A normal deep-research brief in **prose**, shaped by internal trust signals:

- **Verified + stronger sources** → stated clearly in thematic sections with links
- **Verified + weaker sources** → included with softer framing
- **Failed grounding** → collapsed **Needs review** (not presented as fact)
- Tier labels stay **out** of the user report; the audit ledger is internal/ablation-only

Arm A is the fluent **pre-trust draft** from the same research run (ablation baseline), not a separate product.

---

## 5. End-to-end flow

**MVP path**

1. Interpret the question and form a short plan
2. Search and read sources (main agent; workers off in MVP)
3. Draft findings with URLs attached
4. Split into claims
5. Assign source tier (= confidence) per supporting URL
6. Run hard grounding checks
7. Write the **prose final report** (Arm B) from verified claims; fold fails under Needs review; keep internal ledger
8. Stop (harness stop: no more tool calls or max turns; trust layer does not re-search). Arm A = step-3 draft kept for ablation.

**Full design only:** after step 7, if many claims are unsupported or Tier-3-heavy, run one targeted re-search pass and re-check.

---

## 6. MVP vs full design

### MVP (what we ship now)

- Single-agent harness + Claude + web search/read
- End-of-research trust pass → **prose** final report (product = Arm B)
- Three assignment-style demos (synthetic data; CoT conflict; inference-time scaling)
- Ablation: fluent draft (A) vs trust-aware prose final (B) from the **same** research run
- Decision log of choices that changed output
- Trace or log retained for the demo

### Full design (not in MVP)

- Multi-worker delegation
- Extra search pass driven by failed grounding
- Richer soft “support” judge with human spot-checks
- Production memory store for long runs
- Broader tool set (code, docs corpora)
- Multi-question eval suite

---

## 7. Evaluation

### Demo test cases (MVP)

1. Synthetic data risks/benefits for LLM training (assignment Example 1) — primary ablation  
2. Chain-of-thought: reasoning vs formatting; literature disagrees (Example 2)  
3. Inference-time compute scaling; validated vs speculative (Example 3)

Why these: (1) mixed source quality, (2) contradictory literature, (3) sparse/emerging evidence. Together they stress tier + grounding differently.

Outputs live under `examples/01_*` … `examples/03_*`. Process notes: `DECISION_LOG.md`.

### Success criteria for the demo

- Both arms use real web search (deep research, not chat-only)
- Arm B includes a claim ledger with tier + grounding
- Clear difference vs Arm A on at least one claim (A states it smoothly in prose; B marks it Tier 3 or unsupported)
- We can explain every component in the path above

### Ablation (MVP)

Same assignment question. Same harness + Claude + web search. Only the trust layer changes.

| Arm | Setup | Output |
|---|---|---|
| **A — Fluent draft** | Harness + Claude + search/read | Pre-trust deep research draft |
| **B — Product final** | Same research, then trust layer + prose writer | Multi-section prose report + Needs review; internal ledger |

**What it isolates:** value of claim–evidence split, source tiers, and grounding — not “whether search helps.”  
**How we compare:**

1. In A, claims are embedded in prose with links
2. In B, count claims by Tier 1 / 2 / 3 / unsupported
3. Call out one claim that looks fine in A but B marks Tier 3 or unsupported

Fastest way to run it: **one research run**, export A as the fluent report, run the trust layer on that same draft for B.

No multi-seed study. One question, one research run, two views.

### Quality notes we will attach

- Our short assessment of A vs B
- Any failure we hit (bad page, wrong tier, quote mismatch) and what we did

---

## 8. Tradeoffs

| Choice | Why | Cost |
|---|---|---|
| Harness + trust layer | Separates retrieval from trust | Extra post-pass latency |
| Source tier as confidence | Easy to explain and audit; matches how readers judge sources | Coarse; good paper can still be misused |
| Single-agent MVP | Fits time; fewer moving parts | Weaker on broad multi-hop questions |
| Same-run A/B (fluent vs ledger) | Isolates trust layer; both arms are deep research | Doesn’t measure a second retrieval policy |

---

## 9. Risks

- **Wrong tier:** domain heuristics mis-label a source → keep allowlists short and editable; default unknown → Tier 3
- **Grounding false negative:** quote paraphrased → allow light normalization; don’t require exact prose match for all claims
- **Grounding false positive:** span present but doesn’t support claim → soft support judge is full design only
- **Thin / low coverage:** search or fetch failed for a facet → label `coverage: low` rather than inventing certainty

---

## 10. Open follow-ups

- Second pass only on unsupported / Tier-3-heavy claims
- Multi-source agreement before promoting a claim’s visibility
- Worker fan-out when the question clearly splits into independent paths

---

## 11. Doc map for presentation

1. Goal and problem (2 min)  
2. Architecture diagram + components (8 min)  
3. Trust layer: tiers + grounding (5 min)  
4. MVP demo + A/B outputs (10 min)  
5. What we’d build next (3 min)  
6. Q&A
