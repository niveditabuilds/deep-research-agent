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

1. **Research harness** — plan, call tools, delegate to worker instances when useful, retry failures, log the run, synthesize a draft report. Built for long multi-step retrieval.
2. **Trust layer** — split claims from evidence, assign a source tier, check grounding, emit the final prose report + ledger.

The harness gets information. The trust layer decides how much to trust each claim.

Because grounding is a **separate** step after research, the full design keeps a **deep research harness** (workers, rich tools, high turn budget). The MVP uses a thinner harness only to finish demos under time/cost limits — not because trust requires a weak research loop.

**Confidence = source tier (+ grounding).** No separate high/medium/low score. Tier is the confidence signal; grounding is the gate: if the receipt fails, the claim is **unsupported** regardless of tier.

---

## 3.1 How this differs from Claude Research and OpenAI Deep Research

Sources for how those systems work **today** (product/engineering posts, not speculation):

- Anthropic — [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Jun 13, 2025): Claude **Research** is a multi-agent product (LeadResearcher + parallel subagents + CitationAgent).
- OpenAI — [Introducing deep research](https://openai.com/index/introducing-deep-research/) (Feb 2, 2025, with later product updates) and [Deep research API guide](https://developers.openai.com/api/docs/guides/deep-research): ChatGPT/API **Deep research** is a long-running browsing agent that returns a cited report.

This section compares **research products**, not plain Claude/ChatGPT chat without Research/Deep research enabled.

### Claude Research (Anthropic) — how it works

From Anthropic’s engineering write-up:

1. **LeadResearcher** plans; can **save the plan to Memory** so it survives context truncation (~200k).
2. Spawns **Subagents in parallel** (often ~3–5 for complex queries; more when needed). Each has its own context, searches iteratively, returns condensed findings.
3. Lead may loop: synthesize → spawn more subagents or refine → until enough information.
4. **CitationAgent** runs after research: reads the **report plus source documents** and attaches citations so claims are **attributed to sources**.
5. Effort and **source-quality preferences** are steered heavily by **prompts / heuristics** (Anthropic describes teaching agents to prefer authoritative sources after humans saw SEO content farms win too often). Internal evals also score “source quality,” but that is an evaluation rubric, not a user-visible tier label on each claim.

**What that optimizes for:** breadth, parallel coverage, and cited synthesis at product scale.

### OpenAI Deep Research — how it works

From OpenAI’s launch post and API docs:

1. A **single long-running research agent** (models such as `o3-deep-research` / lightweight `o4-mini-deep-research`), trained with RL for multi-step browsing and analysis.
2. Plans, searches/browses (text, images, PDFs), can use **code interpreter**, and (in API/product) other data tools; pivots as it learns.
3. Typical wall clock on the order of **~5–30 minutes**; returns a **comprehensive report with citations** and a visible trail of steps/thinking.
4. Product updates add things like **restricting web search to trusted sites**, MCP/app connectors, and interrupt/refine — i.e. control over *where* search may go and how the run proceeds.
5. Public docs emphasize **cited, analyst-style reports**, not an exported per-claim ledger with explicit source-tier labels and pass/fail grounding gates.

**What that optimizes for:** deep autonomous browsing + polished, cited long-form answers.

### This agent — how it works

```
Research harness (main ± worker instances, search/read, …)
  → fluent draft
Trust layer
  → extract (claim, evidence, url)
  → assign source tier 1/2/3 from URL host rules  (= confidence)
  → hard grounding: URL fetches AND evidence span/key fact appears
  → prose final from passes only; fails → collapsed Needs review
  → internal ledger for audit / ablation
```

MVP ships a thinner harness; full design keeps a deep multi-step harness and the same trust contract (§6).

### Side-by-side

| Dimension | Claude Research (Anthropic) | OpenAI Deep Research | **This agent** |
|---|---|---|---|
| Research shape | Lead + **parallel subagents** + loop | Long **single-agent** browse/reason loop | Harness: main ± worker instances (full design); MVP single-agent |
| Primary output | Cited research answer | Cited long-form report | **Trust-filtered prose** + **Needs review** + **ledger** |
| Citations | **CitationAgent** attributes claims to source locations after drafting | Inline/cited report; user can open sources | Citations only for claims that **pass grounding**; fails do not stay as findings |
| Source quality | Mostly **prompt heuristics** (+ internal judge rubrics); not a fixed public 1/2/3 label per claim | Can **restrict search to trusted sites** (product update); not a post-hoc tier on each claim | **Explicit tier = confidence** from host rules (paper/gov → press → blog/unknown) |
| If cite looks good but text doesn’t check out | Citation pass aims at correct **attribution**; Anthropic does **not** publish a “failed receipt → demote from main report” product surface like ours | Report remains a fluent cited narrative; no public “Needs review” demotion lane for failed span checks | **Hard gate:** no span / no fetch ⇒ **unsupported** → **Needs review** only (even Tier-1 hosts) |
| Audit artifact | Final cited answer (+ their internal tracing) | Report + step/source trail in product/API | Machine-readable **ledger** (`tier`, `grounding`, `coverage`) for every extracted claim |
| Eval story we show | Their blog: LLM-as-judge on accuracy, citation, completeness, source quality, tool use | Product quality via long RL’d browse + citations | **Same-run A/B:** fluent draft vs trust-filtered final |

### What we are *not* claiming

- That Claude Research or OpenAI Deep Research “never verify sources.” Both care about citations; Anthropic even isolates a CitationAgent; OpenAI markets cited, documentable outputs and trusted-site controls.
- That our harness is deeper or more parallel than Anthropic’s production Research stack. Their published system is explicitly multi-agent and highly optimized for coverage/latency.
- That hard span-matching equals full entailment. Soft “does this quote support the claim?” is full design only; Anthropic’s citation location pass and our span check are **different mechanisms**.

### Close

> We are not claiming a better search engine than Claude Research or OpenAI Deep Research. We are claiming a stricter trust contract: after research, every finding must pass a source-tier label and a hard receipt check, or it leaves the main report.

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

**Failure behavior:** see §4.3.1 (graceful degradation). Do not drop failures silently.

### 4.3.1 Graceful degradation (when / what / where listed)

“Graceful degradation” means: **keep the run alive, shrink what we claim, and write the gap somewhere inspectable** — never invent certainty to fill a hole.

Conditions are detected in code (harness client, orchestrator, tools, trust layer). They are **listed** in three places depending on severity:

| Surface | Who sees it | What it holds |
|---|---|---|
| **Harness trace** (`harness/logs/`) | Engineers / debug | Every retry, tool error string, worker failure, overflow trim |
| **Claim ledger** (`arm_b/ledger.md` / `.json`) | Ablation / audit | Per-claim `tier`, `grounding` pass/fail, `coverage` ok/low |
| **User report** (`arm_b/report.md`) | Reader | Verified prose only; fails under collapsed **Needs review**; optional coverage note in Limits |

#### Condition table

| # | When (trigger) | What happens | Where listed |
|---|---|---|---|
| 1 | Anthropic/API call fails transiently | Same request retried up to **5×**, **10s** apart | Trace only (unless all retries fail → #6) |
| 2 | Model emits malformed tool JSON | Error observation returned (“format incorrect… try again”); **next turn** model may correct | Trace + next message in agent history |
| 3 | Search/read throws or times out | Error string returned as tool result; loop **continues**; model may retry a different query/URL | Trace; if that facet never recovers → ledger `coverage: low` and/or Needs review |
| 4 | `read_file` HTTP download fails | Up to ~3 download retries with backoff, then scrape fallback; still fail → error to agent | Trace |
| 5 | Worker instance fails or returns empty (full design) | Main **does not abort**; continues with other facets; that subtask marked incomplete | Trace (worker session); main may note gap in draft; trust may leave related claims unsupported |
| 6 | Context overflow / summary call fails | Drop recent assistant–user pairs / retry summary; still try to emit an answer | Trace; report may be thinner |
| 7 | Hit `max_turns` before model stops | Force final summary with whatever evidence exists | Trace (`max_turns_reached`); report may note limits |
| 8 | Claim URL missing / page won’t load / evidence span not found | Claim **not** stated as a finding | Ledger: `grounding=fail`, often `coverage=low`; report: **Needs review** `<details>` block |
| 9 | Claim only backed by Tier-3 sources but grounding passes | Keep claim, softer framing; tier stays in ledger (not printed as a badge in user prose) | Ledger: tier=3; report: included carefully |
| 10 | Many claims fail grounding or are Tier-3-heavy (**full design**) | One **targeted re-search** on weak claims, then re-run grounding once | Trace (second pass); updated ledger + report |

#### How the user-facing list is produced

1. Trust layer builds rows: `{claim, evidence, url, tier, grounding, coverage}`.
2. `grounding=fail` → excluded from main prose; appended under:

```markdown
## Needs review
<details>
<summary>N items could not be verified…</summary>
- claim … (reason / url)
</details>
```

3. `coverage=low` is recorded on the ledger row when URL resolve/fetch is weak; the report’s **Limits of this report** states that only receipt-checked claims are asserted.
4. Harness-only failures (retries that eventually succeeded) stay in the **trace**, not the reader report.

#### Non-goals

- Do **not** promote a Tier-1 URL that failed the receipt check into Findings (reversed; see `DECISION_LOG.md`).
- Do **not** put Needs review items as a peer section that skimmers read as answers (collapsed on purpose).

### 4.4 Run loop, stopping, memory, and traces

**Loop:** think → act (one tool or one worker subtask) → observe → repeat.

**Stop conditions (harness):**

| Condition | What happens |
|---|---|
| Model returns **no tool call** | Soft stop → treat response as draft / trigger final summary |
| **`max_turns` reached** (main and each worker instance have their own cap) | Hard stop → force summary from whatever is in history (`ExceedMaxTurn`-style path) |
| Unrecoverable LLM failure after retries | Mark failed; still attempt summary if possible |
| Context overflow | Trim recent turns / summarize; still emit an answer |

Trust-driven **re-search** after a weak ledger is full design only (§4.3.1 #10) — not a harness stop rule.

**Memory (what the agent keeps):**

| Kind | Full design | MVP |
|---|---|---|
| **Working memory** | In-run message history (system + user + assistant + tool results) for main; **separate history per worker instance** | Same, but only main (no workers) |
| **Cross-agent handoff** | Worker returns a **condensed summary** into main’s history (not raw page dumps) | N/A |
| **Tool-result retention** | `keep_tool_result` (default **-1** = keep all tool payloads in context; set ≥0 to stub older bulky results) | `-1` |
| **Long-term / cross-query store** | Optional production store for long-running or repeated topics (follow-up) | None |
| **Durable debug record** | Trace on disk (below) — not fed back as agent memory by default | Same |

**Traces (where the run is recorded):**

| | |
|---|---|
| **What** | Structured run log: task id, timestamps, each turn, tool/worker calls, errors/retries, final answer |
| **Where** | On disk under the harness `output_dir` (shipped MVP: `harness/logs/<task_id>.log`) |
| **Who uses it** | Engineers debugging “what failed three steps ago”; not the reader-facing report |
| **Git** | Local only (gitignored) |

Reader-facing honesty lives in the **ledger** + **Needs review**, not in the trace.

Shipped MVP knob file: [HARNESS_CONFIG.md](./HARNESS_CONFIG.md).

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

Same agent architecture. Different **operating points**.

### Operating point table

| Knob | Full design (deep research) | MVP (shipped demos) |
|---|---|---|
| **Agents** | Main + **worker type** `agent-worker`; main may spawn **multiple instances** (one subtask each; parallel when independent) | Main only (`sub_agents: null`) |
| **Main tools** | Often light (e.g. reasoning); delegates heavy IO to workers | Search (Serper) + reading |
| **Worker tools** | Search, reading, code, and other MCP tools as needed (vision/audio when the question needs them) | N/A |
| **`max_turns`** | High / unlimited (`-1`) on main **and** each worker instance so long research can finish | **25** on main (demo cost/time ceiling) |
| **`max_tool_calls_per_turn`** | 10 | 10 |
| **`keep_tool_result`** | `-1` (keep all) unless context pressure requires trimming | `-1` |
| **Stop** | No tool call **or** turn cap → forced summary | Same rules, tighter cap |
| **Hints / answer extract** | Optional (on for some eval pipelines) | Off |
| **Trace** | `output_dir` / `logs/<task_id>.log` | Same |
| **Trust** | End-of-run pass + optional re-search if ledger is weak; soft support judge | One hard-grounding pass → prose B + Needs review |

Grounding does **not** replace long research. It filters what long research may assert.

### Full design — research harness (detailed)

**Topology**
```
Main agent
  ├─ own tools (optional)
  └─ agent-worker.execute_subtask(subtask)
        → new worker instance (own message history, own max_turns)
        → search / read / other tools
        → returns condensed summary to main
Main synthesizes draft → Trust layer
```

- One **worker type**, many **instances** (not a roster of differently named specialists unless we add more YAML entries later).
- Workers do not talk to each other; main merges.
- Independent subtasks may run as concurrent instances so wall time ≈ slowest worker, not the sum.

**Turns & stop**
- Each node (main, each worker instance) has `max_turns`.
- Soft stop: model emits final content with no tool call.
- Hard stop: turn budget exhausted → summary generator still produces a draft.
- Bad tool JSON / tool timeout: error surfaced into history; loop continues (§4.3.1).

**Memory & traces**
- Working memory = message histories (main + per instance).
- Handoff memory = worker summaries.
- Optional trim via `keep_tool_result` when context grows.
- Trace on disk for every run (turns, tools, errors) under `harness/logs/`.

**Trust additions in full design (on top of that harness)**
- Second targeted search when many claims fail grounding or are Tier-3-heavy
- Soft “does the span support the claim?” judge + human spot-checks
- Optional cross-query memory store for long-running products
- Multi-question eval / regression on demotions

### MVP (what we ship now)

- Config: `harness/config/agent_mvp_anthropic.yaml` — see [HARNESS_CONFIG.md](./HARNESS_CONFIG.md)
- Single-agent, Serper + reading, `max_turns: 25`
- One trust pass → prose report + Needs review + ledger
- Three demos + same-run A/B ablation + decision log

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
| Harness + trust layer | Separates retrieval from permission to assert | Extra post-pass latency |
| Source tier as confidence | Easy to explain and audit; matches how readers judge sources | Coarse; good paper can still be misused |
| Thin harness in MVP only | Fits take-home time; clearer ablation | Understates full-design coverage |
| Same-run A/B (fluent vs ledger) | Isolates trust layer; both arms are deep research | Doesn’t measure a second retrieval policy |

---

## 9. Risks

- **Wrong tier:** domain heuristics mis-label a source → keep allowlists short and editable; default unknown → Tier 3
- **Grounding false negative:** quote paraphrased → allow light normalization; don’t require exact prose match for all claims
- **Grounding false positive:** span present but doesn’t support claim → soft support judge is full design only
- **Thin / low coverage:** search or fetch failed for a facet → label `coverage: low` rather than inventing certainty (see §4.3.1)

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
