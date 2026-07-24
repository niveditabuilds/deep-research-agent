# Harness configuration (MVP)

Primary config file: [`harness/config/agent_mvp_anthropic.yaml`](./harness/config/agent_mvp_anthropic.yaml)  
Selected by default in `scripts/run_arm_a.py` (`--config agent_mvp_anthropic`) and `./demo`.

This doc covers **our MVP knobs only** — not every unused benchmark/tool preset under `harness/config/`.

---

## Mental model

```
one research run
  └─ up to max_turns agent loops
        └─ each loop: 1 LLM call → up to max_tool_calls_per_turn tool calls
  └─ stop → final summary (Arm A draft)
```

| Knob | Unit | Our value |
|---|---|---|
| `max_turns` | Agent loop turns for the **whole run** | `25` |
| `max_tool_calls_per_turn` | Tool calls **inside one turn** | `10` |
| `keep_tool_result` | How many recent tool-result messages stay in context | `-1` (keep all) |

`max_turns` is **not** “per tool.” It is the cap on think → act → observe cycles for one question.

---

## Who calls the LLM (research loop)

Every harness turn goes through the official Anthropic SDK — not a hand-rolled HTTP client.

```
./demo or scripts/run_arm_a.py
  → harness orchestrator (tool loop)
    → ClaudeAnthropicClient   # provider_class in agent_mvp_anthropic.yaml
      → AsyncAnthropic.messages.create(...)
        → https://api.anthropic.com   # or ANTHROPIC_BASE_URL
```

| Piece | Value |
|---|---|
| Client class | `ClaudeAnthropicClient` (`harness/src/llm/providers/claude_anthropic_client.py`) |
| Auth | `ANTHROPIC_API_KEY` |
| Model | `claude-sonnet-4-5-20250929` |
| Per-call timeout | SDK client timeout **600s** |
| What is sent | System prompt + in-run message history (question, prior tool results) |

The orchestrator calls this **once per turn**. The model replies with text and/or a tool call; if it returns **no tool call**, the loop treats that as the final answer and stops.

**Not the same path:** the trust layer (`trust_layer/claims.py`, `ledger.py`) calls Anthropic via raw REST `/v1/messages` after the harness finishes. That path does not use `ClaudeAnthropicClient` or the tenacity retries below.

---

## Retry & failure behavior (harness)

These are code defaults in the harness client/orchestrator/tools — not YAML keys — but they are part of how the MVP actually runs.

### LLM API retry
| | |
|---|---|
| Where | `@retry` on `ClaudeAnthropicClient._create_message` |
| Policy | Up to **5 attempts**, **10s** wait between tries |
| Covers | Transient Anthropic/network failures on the **same** request |
| Does not cover | Bad model answers, or “think again with a new plan” |

### Bad tool-call format
Malformed tool JSON → harness returns an error observation (“format incorrect… try again”) → **same LLM**, next turn, can correct. Soft rollback; run continues.

### Tool execution failure (search / read)
Timeout or exception → error string logged and returned as the tool result → loop **continues**. Model may search differently or skip that source. Does not kill the whole run.

### `read_file` download retry (inside the tool)
HTTP download: up to **~3 retries** with exponential backoff, then scrape fallback (Serper/Jina). Still failing → error text back to the agent.

### Final summary / context overflow
- Summary network blips: retry up to **5×** (with wait)  
- Context too large: drop recent assistant–user pairs and retry summary so an answer still emits  

### What is *not* retried in the harness
- Trust/grounding failures do **not** auto-trigger another research pass  
- No full “restart from turn 1” on a bad plan  

---

## Stop conditions

| Condition | Behavior |
|---|---|
| Model returns **no tool call** | Soft stop — that message is the draft (Arm A) |
| `max_turns` reached (`25`) | Hard stop — force final summary |
| Unrecoverable LLM failure mid-loop | Mark failed, still attempt summary path |

Typical demo timing: ~**5s/turn** for tool turns; full research wall clock ~**3–7 min** (shallow single-agent loop, not a 30‑min multi-worker crawl).

---

## Full MVP YAML (annotated)

```yaml
defaults:
  - benchmark: example_dataset   # Hydra default; unused for live ./demo runs
  - override hydra/job_logging: none
  - _self_

main_agent:
  prompt_class: MainAgentPromptBoxedAnswer   # system / boxed-answer prompt

  llm:
    provider_class: "ClaudeAnthropicClient"
    model_name: "claude-sonnet-4-5-20250929"
    async_client: true
    temperature: 0.3
    top_p: 1.0              # Anthropic rejects temp + non-default top_p together
    min_p: 0.0
    top_k: -1               # unused for Anthropic client path
    max_tokens: 16000       # max tokens per LLM response
    anthropic_api_key: "${oc.env:ANTHROPIC_API_KEY,???}"
    anthropic_base_url: "${oc.env:ANTHROPIC_BASE_URL,https://api.anthropic.com}"
    disable_cache_control: false
    keep_tool_result: -1    # also set under main_agent (see below)
    oai_tool_thinking: false

  tool_config:
    - tool-searching-serper   # web search via Serper MCP
    - tool-reading            # fetch / read page text

  max_turns: 25
  max_tool_calls_per_turn: 10

  input_process:
    hint_generation: false    # no pre-run “hint” LLM pass
    hint_llm_base_url: "${oc.env:HINT_LLM_BASE_URL,https://api.openai.com/v1}"
  output_process:
    final_answer_extraction: false   # no post-hoc answer extractor LLM
    final_answer_llm_base_url: "${oc.env:FINAL_ANSWER_LLM_BASE_URL,https://api.openai.com/v1}"

  openai_api_key: "${oc.env:OPENAI_API_KEY,}"   # only needed if hint/extract enabled
  add_message_id: true
  keep_tool_result: -1        # context trimming policy (see Memory)
  chinese_context: "false"

sub_agents: null              # single-agent MVP — no worker fan-out

output_dir: logs/             # harness/logs/ when run from harness/
data_dir: "${oc.env:DATA_DIR,data}"
```

---

## Parameter reference

### Loop & tools

| Key | MVP | Meaning |
|---|---|---|
| `max_turns` | `25` | Max **agent turns** for one research run. Each turn = one LLM call, optionally with tools. Stop earlier if the model returns no tool calls. `-1` = unlimited. |
| `max_tool_calls_per_turn` | `10` | Cap on tool calls executed from a single assistant turn. Extra calls in that turn are ignored. |
| `tool_config` | Serper + reading | Which MCP tool packs the main agent may call. |
| `sub_agents` | `null` | No workers. In multi-agent configs, each worker has its own `max_turns` / tools. |

### Memory / context

| Key | MVP | Meaning |
|---|---|---|
| `keep_tool_result` | `-1` | How many recent tool-result messages to keep when calling the LLM. `-1` = keep all (no mid-run trim). `≥ 0` = keep first user message + last *N* tool/user payloads; older tool bodies get stubbed. Set on both `main_agent` and `main_agent.llm` in this file. |
| (overflow path) | harness built-in | On context-limit errors: drop recent turns / force summary and still emit an answer. |

**What counts as memory in MVP:** in-run message history only. Trace under `harness/logs/` is durable for debugging, not agent memory.

### LLM sampling

| Key | MVP | Meaning |
|---|---|---|
| `provider_class` | `ClaudeAnthropicClient` | Direct Anthropic API client. |
| `model_name` | `claude-sonnet-4-5-20250929` | Model for the research loop. |
| `temperature` | `0.3` | Sampling temperature. |
| `top_p` | `1.0` | Kept at default so Anthropic accepts `temperature`. |
| `max_tokens` | `16000` | Max completion tokens per LLM response. |
| `async_client` | `true` | Async Anthropic client. |
| `disable_cache_control` | `false` | Allow prompt-cache hints on Anthropic messages. |
| `oai_tool_thinking` | `false` | OpenAI-specific; unused on Anthropic path. |
| `min_p` / `top_k` | `0.0` / `-1` | Unused on this Anthropic path. |

### Prompts & I/O processing

| Key | MVP | Meaning |
|---|---|---|
| `prompt_class` | `MainAgentPromptBoxedAnswer` | Prompt class under `harness/config/agent_prompts/`. |
| `input_process.hint_generation` | `false` | If true, a separate LLM rewrites “hints” before the run (needs OpenAI-compatible key). |
| `output_process.final_answer_extraction` | `false` | If true, a separate LLM extracts a short final answer after the run. |
| `add_message_id` | `true` | Tag messages with ids in history. |
| `chinese_context` | `"false"` | Toggle Chinese-oriented prompt variants. |

### Paths

| Key | MVP | Meaning |
|---|---|---|
| `output_dir` | `logs/` | Where run traces are written (`harness/logs/` in practice). Gitignored. |
| `data_dir` | `data` / `$DATA_DIR` | Benchmark data root; unused for live demos. |
| `defaults.benchmark` | `example_dataset` | Hydra compose default; live `./demo` path does not score a benchmark. |

---

## Tool configs used by MVP

### `tool-searching-serper` — [`harness/config/tool/tool-searching-serper.yaml`](./harness/config/tool/tool-searching-serper.yaml)

| Key | Value |
|---|---|
| Command | `npx -y serper-search-scrape-mcp-server` |
| Env | `SERPER_API_KEY` (required) |

### `tool-reading` — [`harness/config/tool/tool-reading.yaml`](./harness/config/tool/tool-reading.yaml)

| Key | Value |
|---|---|
| Command | `python -m src.tool.mcp_servers.reading_mcp_server` |
| Env | `SERPER_API_KEY` (optional), `JINA_API_KEY` (optional) |

Other tool YAMLs under `harness/config/tool/` (code, audio, browsing, …) are **not** wired into the MVP agent.

---

## Environment variables

Loaded from repo-root `.env` (see [`.env.example`](./.env.example)). `run_arm_a.py` copies it into `harness/.env` for the subprocess.

| Variable | Required | Used by |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Research LLM + trust-layer extract/rewrite |
| `SERPER_API_KEY` | Yes | Web search (and reading helper) |
| `ANTHROPIC_BASE_URL` | No | Override Anthropic API base (default `https://api.anthropic.com`) |
| `JINA_API_KEY` | No | Optional reading/fetch path |
| `OPENAI_API_KEY` | No | Only if hint / final-answer extraction enabled |
| `DATA_DIR` | No | Benchmark data root |
| `TRUST_LAYER_MODEL` | No | Override trust extract model (see below) |
| `OPENROUTER_API_KEY` | No | Alternate trust extract path if set |

---

## Trust layer knobs (not in the YAML; live next to the harness)

These are code/env defaults in `trust_layer/`, not Hydra:

| Knob | Default | Where |
|---|---|---|
| Max extracted claims | `20` | `trust_layer/claims.py` |
| Extract / rewrite model | `claude-sonnet-4-5-20250929` (or `$TRUST_LAYER_MODEL`) | `claims.py`, `ledger.py` |
| Grounding HTTP timeout | `25s` | `trust_layer/grounding.py` |
| Rewrite HTTP timeout | `300s` | `trust_layer/ledger.py` |

Trust runs **after** the harness finishes. It does not share `max_turns` with the research loop.

---

## How to change a knob

1. Edit `harness/config/agent_mvp_anthropic.yaml`, or  
2. Override on the CLI when calling the harness, e.g.  
   `main_agent.max_turns=40`  
   (Hydra-style overrides via `uv run main.py trace --config_file_name=agent_mvp_anthropic ...`)

Or point `scripts/run_arm_a.py --config <other_yaml_name>` at a different agent file under `harness/config/`.

---

## Interview short answers

- **LLM path:** orchestrator → `ClaudeAnthropicClient` → Anthropic SDK each turn (`ANTHROPIC_API_KEY`).  
- **Loop budget:** 25 turns for the whole run; up to 10 tools per turn; stop when no tool call or hit cap.  
- **Memory:** full message history (`keep_tool_result: -1`); logs on disk; no vector/long-term memory.  
- **Retry:** API 5×/10s; bad tool JSON and tool errors surfaced back to the model; read download retries inside the tool.  
- **Tools:** Serper search + page read only; trust layer re-checks citations after the draft.  
- **Workers:** off (`sub_agents: null`).
