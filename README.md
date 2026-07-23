# Deep Research Agent — MVP

Trust-aware research agent for the Reinforce Labs take-home.

**Product path:** harness researches → trust layer (tier + grounding) → **prose final report (Arm B)**.  
**Ablation baseline:** the fluent pre-trust draft from the same run (**Arm A**).

## Ablation

| Arm | What |
|---|---|
| **A** | Same research run’s fluent draft (no trust filter) |
| **B** | Product final: trust-conditioned **multi-section prose** report + collapsed Needs review; internal ledger |

## Example outputs (3)

See [examples/README.md](./examples/README.md):

1. Synthetic data risks/benefits (full A/B)
2. Chain-of-thought literature conflict
3. Inference-time compute scaling (sparse/emerging)

## Decision log

[DECISION_LOG.md](./DECISION_LOG.md)

## Setup

```bash
cp .env.example .env
# ANTHROPIC_API_KEY=...
# SERPER_API_KEY=...

cd harness && uv sync --python 3.12 && cd ..
python3 -m pip install -r requirements.txt
chmod +x demo
```

## Run live on any question

```bash
# from repo root (keys in .env)
./demo "Your research question here"

# or:
harness/.venv/bin/python scripts/run_mvp.py "Your research question here"

# or interactive prompt:
./demo
```

Writes a fresh folder under `examples/live_<timestamp>_.../` with:
- `arm_a/report_body.md` — fluent draft  
- `arm_b/report.md` — **product** trust-aware prose report  
- `arm_b/ledger.md` — audit table  

Expect several minutes (search loop + grounding + prose rewrite).

## Or step by step

```bash
# Arm A — fluent research draft
harness/.venv/bin/python scripts/run_arm_a.py \
  --task "Your research question here" \
  --task-id-prefix live \
  --out-dir examples/live_manual/arm_a

# Arm B — product final prose report
harness/.venv/bin/python scripts/run_trust_layer.py \
  --input examples/live_manual/arm_a/report_body.md \
  --out-dir examples/live_manual/arm_b
```

## Design

See [DESIGN.md](./DESIGN.md).

## Layout

```
DESIGN.md          Full design + MVP cut
DECISION_LOG.md    Key decisions that changed output
demo               Live entrypoint for any query
harness/           Research harness (tool loop, retries, traces)
trust_layer/       Claims, tiers, grounding, prose final report
scripts/           run_mvp / run_arm_a / run_trust_layer
examples/          01 / 02 / 03 demo outputs + live_* runs
```
