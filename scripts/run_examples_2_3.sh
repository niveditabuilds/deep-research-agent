#!/usr/bin/env bash
# Run Arm A + Arm B for examples 02 and 03 (sequential; long-running).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/harness/.venv/bin/python"
cd "$ROOT"

Q2='Is chain-of-thought prompting an effective reasoning strategy for LLMs, or does it primarily improve output formatting? The literature disagrees—find the real fault lines and explain what accounts for the conflicting results.'
Q3='What is the current state of inference-time compute scaling for LLM reasoning? Separate what has been empirically validated from what is still speculative, and identify where the evidence is too thin to draw conclusions.'

echo "=== Example 02 Arm A ==="
"$PY" scripts/run_arm_a.py \
  --task "$Q2" \
  --task-id-prefix cot_conflict \
  --out-dir examples/02_chain_of_thought/arm_a

echo "=== Example 02 Arm B ==="
"$PY" scripts/run_trust_layer.py \
  --input examples/02_chain_of_thought/arm_a/report_body.md \
  --out-dir examples/02_chain_of_thought/arm_b

echo "=== Example 03 Arm A ==="
"$PY" scripts/run_arm_a.py \
  --task "$Q3" \
  --task-id-prefix inference_scaling \
  --out-dir examples/03_inference_time_scaling/arm_a

echo "=== Example 03 Arm B ==="
"$PY" scripts/run_trust_layer.py \
  --input examples/03_inference_time_scaling/arm_a/report_body.md \
  --out-dir examples/03_inference_time_scaling/arm_b

echo "DONE"
