# AnthroVest AI Backend CLI MVP

AnthroVest AI is a LangGraph-orchestrated multi-agent CLI prototype for U.S. equity research workflows.

This backend is intentionally isolated from the current frontend UI:

- It does not modify the Start Screen.
- It does not connect to the existing frontend yet.
- It focuses on a CLI-based multi-agent MVP.

## What this prototype does

The CLI runs a multi-agent graph:

MemoryLoadNode  
→ IntentAgent  
→ SlotAgent  
→ DecisionAgent  
→ PlannerAgent  
→ MarketDataAgent  
→ NewsSentimentAgent  
→ FinancialAgent  
→ TechnicalAgent  
→ RiskAgent  
→ ReportAgent  
→ MemoryWriteNode

It supports commands such as:

```bash
python -m app.main_cli "Analyze NVDA"
python -m app.main_cli "帮我分析一下 TSLA 最近怎么样，重点看技术面"
python -m app.main_cli "帮我设置价格提醒"
python -m app.main_cli "记住，我更关注半导体和 AI 股票"
```

## Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Configure OpenRouter

1. Generate an API key from OpenRouter.
2. Copy `.env.example` to `.env`.
3. Fill in:

```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
OPENROUTER_FALLBACK_MODELS=openrouter/free,qwen/qwen3-coder:free,deepseek/deepseek-r1:free,meta-llama/llama-3.3-70b-instruct:free
```

OpenRouter is optional.

If no key is present:

- IntentAgent falls back to rule-based intent classification.
- SlotAgent falls back to regex and keyword extraction.
- ReportAgent falls back to a deterministic template report.

If a free model fails or is temporarily unavailable, the code automatically tries the next model in `OPENROUTER_FALLBACK_MODELS`.

## Run the CLI

From inside `backend/`:

```bash
python -m app.main_cli "Analyze NVDA"
```

Or:

```bash
python app/main_cli.py "Analyze NVDA"
```

## What is real vs mock

### Real data paths

- `MarketDataAgent`: uses `yfinance` for quote and historical price data
- `FinancialAgent`: uses `yfinance` info fields
- `TechnicalAgent`: computes indicators with `pandas` and `numpy`

### Mock paths

- `NewsSentimentAgent`: uses mock news generation
- `MemoryLoadNode`: includes a mock knowledge base
- `MarketDataAgent`: falls back to mock market data if `yfinance` fails

## Memory files

The backend writes local memory artifacts into `backend/data/`:

- `long_term_memory.json`
- `message_history.jsonl`

Each run appends:

- timestamp
- session_id
- user_input
- intent
- slots
- plan
- per-agent outputs
- final_report
- tool_calls
- observations
- agent_status
- errors

## Future MCP upgrade path

This MVP uses local tools and mock data for speed.

Later, you can replace the current tool layer with MCP-backed tools such as:

- market data MCP providers
- news search MCP tools
- filings / fundamentals MCP tools
- alerting MCP integrations
- vector knowledge retrieval MCP services

The cleanest replacement points are:

- `app/tools/stock_tools.py`
- `app/tools/mock_news_tools.py`
- `app/memory/*`
- `app/core/llm.py`
