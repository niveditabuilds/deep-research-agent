# Deep Research Agent

Deep research agent: given an open-ended question, it searches the live web, drafts a research brief, then **filters what may be stated as findings** using source quality and citation checks.

**Docs**
- Full architecture + MVP cut: [DESIGN.md](./DESIGN.md)
- What we tried / reversed: [DECISION_LOG.md](./DECISION_LOG.md)
- Harness knobs (`max_turns`, tools, env): [HARNESS_CONFIG.md](./HARNESS_CONFIG.md)
- Example index: [examples/README.md](./examples/README.md)

---

## Problem

Typical deep-research agents already plan, search, and write fluent reports. The failure mode that matters:

- Claims are buried in confident prose
- Citations look real but don’t support the sentence
- A peer-reviewed paper and a random blog look equally “cited”

Readers can’t tell what to trust.

## Approach

Two layers:

1. **Research harness** — plan → search/read → retries → fluent draft  
2. **Trust layer** — claim/evidence/URL split → **source tier = confidence** → hard **grounding** check → prose final report

| Signal | Meaning |
|---|---|
| **Source tier (1 / 2 / 3)** | Confidence from source type (papers/gov → news → blogs/unknown) |
| **Grounding pass/fail** | Page loads **and** the evidence span appears on the page |

Grounding is a hard gate: Tier 1 still fails if the receipt doesn’t check out.

---

## How it works

```
User question
  → Research harness (Claude + Serper search/read)
  → Fluent draft …………………………… Arm A (ablation baseline)
  → Trust layer
        claim extract → tier → grounding → ledger
  → Prose rewrite (verified claims only)
  → Final report ………………………… Arm B (product)
        + collapsed Needs review for failed checks
```

**Live path:** `./demo "your question"` runs this end-to-end and writes `arm_a/` + `arm_b/` under `examples/live_.../`.

---

## Architecture (MVP)

### Research harness
- Single main agent (no worker fan-out in MVP)
- Tools: web search (Serper), page read/fetch
- Loop: think → tool call → observe; retry/rollback on bad tool turns
- Stop: no more tool calls or `max_turns`
- Trace logged under `harness/logs/` (gitignored)

### Trust layer
- Extract ~20 factual `(claim, evidence, url)` triples from the draft
- Assign tier from URL host rules
- Ground each claim (HTTP fetch + span/key-atom match)
- Write a **multi-section prose** report from pass claims; fails → **Needs review**
- Internal audit: `ledger.md` / `ledger.json`

See diagrams and full design in [DESIGN.md](./DESIGN.md).

---

## Why this is better than the baseline

**Baseline (Arm A)** = same research run’s fluent draft (what a normal deep-research agent ships).

**Our product (Arm B)** = same evidence, after trust.

| | Arm A (baseline) | Arm B (ours) |
|---|---|---|
| Goal | Complete, fluent story | Claims you can stand behind |
| Structure | Long thematic report | Thematic **prose** report |
| Weak / unchecked cites | Still stated confidently | Demoted to **Needs review** |
| Confidence | Implicit in tone | Explicit via source tier + grounding |
| Ablation | — | Isolates trust (same search/draft) |

**Concrete demotion example (synthetic data):**  
A states “at least eight distinct definitions of model collapse” as a key finding.  
B: Tier 1 URL, grounding **fail** (evidence span not found) → Needs review only.

---

## Metrics (ablation on 3 prompts)

Same draft → extract 20 claims → trust outcomes for Arm B:

| Example | Kept as findings | Needs review | Share kept |
|---|---:|---:|---:|
| [Synthetic data for LLMs](./examples/01_synthetic_data/) | 5 | 15 | **25%** |
| [Chain-of-thought debate](./examples/02_chain_of_thought/) | 10 | 10 | **50%** |
| [Inference-time compute scaling](./examples/03_inference_time_scaling/) | 11 | 9 | **55%** |

**Takeaway:** A maximizes fluent completeness; B keeps **25–55%** of extracted claims as findings. The drop is the product signal, not a bug.

Per-example notes and demotion callouts: each folder’s `NOTES.md`.

---

## Example outputs

| # | Prompt focus | Why it stresses the system | Paths |
|---|---|---|---|
| 01 | Synthetic data risks/benefits | Mixed source quality; Tier 1 vs Tier 3 | [`examples/01_synthetic_data/`](./examples/01_synthetic_data/) |
| 02 | CoT: reasoning vs formatting | Contradictory literature | [`examples/02_chain_of_thought/`](./examples/02_chain_of_thought/) |
| 03 | Inference-time compute scaling | Sparse / emerging evidence | [`examples/03_inference_time_scaling/`](./examples/03_inference_time_scaling/) |
| Live | Ecommerce site search (ad-hoc) | Any-query demo | [`examples/live_.../`](./examples/) |

In each example folder:

| File | Contents |
|---|---|
| `arm_a/report_body.md` | Fluent research draft (baseline) |
| `arm_b/report.md` | **Product** trust-aware prose report |
| `arm_b/ledger.md` | Internal claim audit (tier + grounding) |
| `NOTES.md` | Quality notes + one demotion |

---

## Full design vs MVP boundaries

| In MVP (shipped) | Full design (not built) |
|---|---|
| Single-agent harness + Claude + Serper | Multi-worker delegation for broad questions |
| End-of-research trust pass | Verify while browsing / mid-loop |
| Hard grounding (fetch + span) | Soft “does quote support claim?” judge |
| One trust pass, then stop | Second search pass on failed grounding |
| Same-run A/B ablation | Multi-seed eval suite |
| Prose B + Needs review | Richer UI / production memory store |

Details: [DESIGN.md](./DESIGN.md) § MVP vs full design.

Process choices that changed the output: [DECISION_LOG.md](./DECISION_LOG.md).

---

## Setup

```bash
git clone https://github.com/niveditabuilds/deep-research-agent.git
cd deep-research-agent

cp .env.example .env
# ANTHROPIC_API_KEY=...
# SERPER_API_KEY=...

cd harness && uv sync --python 3.12 && cd ..
python3 -m pip install -r requirements.txt
chmod +x demo
```

## Run live on any question

```bash
./demo "Your research question here"
# or interactive: ./demo
```

Writes `examples/live_<timestamp>_.../` with Arm A + Arm B. Expect several minutes.

Step-by-step:

```bash
harness/.venv/bin/python scripts/run_arm_a.py \
  --task "Your question" --out-dir examples/manual/arm_a

harness/.venv/bin/python scripts/run_trust_layer.py \
  --input examples/manual/arm_a/report_body.md \
  --out-dir examples/manual/arm_b
```

---

## Repo layout

```
README.md              ← you are here
DESIGN.md              Full architecture + MVP cut
DECISION_LOG.md        Key decisions (worked vs failed)
HARNESS_CONFIG.md      MVP YAML / loop / memory / env knobs
demo                   Live entrypoint for any query
harness/               Research harness (tool loop, traces)
trust_layer/           Claims, tiers, grounding, prose final
scripts/               run_mvp / run_arm_a / run_trust_layer
examples/              A/B outputs + NOTES for demos
```

---

## Interview one-liner

> Deep research agents already write fluent briefs. Ours adds a trust layer so the **final report only states what we can receipt-check**, with source-type confidence and a clear place for everything that didn’t check out.
