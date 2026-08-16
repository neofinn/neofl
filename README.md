# NeoFL

An AI-native algorithmic trading platform for GOLD / XAUUSD on MetaTrader 5.

The goal is not a single Expert Advisor. It is an extensible platform in which AI agents continuously
develop, test, debug, and improve the trading system — under human approval, with MT5 as the only
execution boundary.

## Status

**Phase 1 of 12** — repository structure, legacy source inventory, AI development instructions.

No trading code has been written for the new architecture. Everything under `legacy/` is preserved
reference material from earlier development and none of it is the target architecture.

**Phase 2 is blocked.** The ARK engine's detection rules are not present in any source file or in the
specification — see the open questions in `docs/architecture/SOURCE_INVENTORY.md`.

## Start here

| Document | What it is |
|---|---|
| [`docs/product/MASTER_SPEC_v1.0.md`](docs/product/MASTER_SPEC_v1.0.md) | Product source of truth. Read before changing anything. |
| [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) | System shape and hard boundaries. |
| [`docs/architecture/SOURCE_INVENTORY.md`](docs/architecture/SOURCE_INVENTORY.md) | Audit of all legacy source, and what is missing. |
| [`CLAUDE.md`](CLAUDE.md) | Rules for AI agents working in this repo. |
| [`docs/ai/DEVELOPMENT_WORKFLOW.md`](docs/ai/DEVELOPMENT_WORKFLOW.md) | Branches, commits, tests, definition of done. |

## Architecture in one picture

```
External data (CME, TradingView, Calendar, News)
        -> Data Gateway (Python) -> Normalization -> Real-time state
        -> MT5 Data Bridge (validates, never decides)
        -> TREND EA  +  ARK EA   (separate EAs, shared execution-state protocol)
        -> MT5 (execution boundary)
```

Trend trades short-term intraday structure (M5 primary, M15 confirm, M30 survival, M1 execution).
ARK independently hunts liquidity and market-structure events (M15 context, M1 execution). ARK
reserves the execution slot before ordering so the two never race.

## Layout

```
docs/            product, architecture, strategies, data, execution, testing, ai
strategies/      trend/, ark/ — strategy logic
mt5/             TrendEA/, ARKEA/, DataBridge/ — MQL5 sources
external-data/   CME/, TradingView/, Calendar/, News/
agentic-brain/   advisory AI layer (Phase 8, not before)
backtesting/     replay/, historical-data/
tests/           unit/, integration/, failure/, regression/
infrastructure/  deployment and environment
monitoring/      observability
legacy/          preserved prior source — read-only reference
```

## Ground rules

- Trading logic is decided by the human product owner, never silently by an AI.
- MQL5 is the only execution authority; Python and AI components are advisory.
- No LLM has live order authority.
- Gold only — never BTCXAU, ETHXAU, or synthetic cross-pairs.
- No secrets in Git, ever.

## Tests

```bash
python3 -m unittest discover -s tests
```

MQL5 compilation cannot be verified on macOS — MetaEditor is Windows-only. Python tests here check
source contracts, not compilation or runtime behavior. Compilation and Strategy Tester results must
be reported separately from the Windows MT5 host.

## Environment

Development on macOS (Apple Silicon). MT5 execution runs on a Windows VPS/RDP host.
