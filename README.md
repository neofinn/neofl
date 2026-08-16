# NeoFL

A modular algorithmic trading platform for MetaTrader 5.

NeoFL is not a collection of unrelated EAs. It is one shared trading engine with seven independent
strategies on top of it, an observer network that understands the whole system state, and an external
AI layer that analyzes without ever holding execution authority.

> **Don't duplicate infrastructure. Don't merge strategy logic.**

## Status

Repository scaffolding, preserved legacy source, and architecture canon. **No Core engine module has
been written yet.**

The build order starts with the Core. Two things are worth knowing before planning work:

- **ARK's signal rules are unspecified.** No file in this repository implements liquidity-flow
  detection; the legacy `ARKSignal()` is an empty stub. This blocks ARK (build step 10), not the Core.
- Four of the seven strategies (Price Action, FX, BTC, Indices) have no source at all.

Open questions are listed at the end of [`docs/architecture/SOURCE_INVENTORY.md`](docs/architecture/SOURCE_INVENTORY.md).

## Start here

| Document | What it is |
|---|---|
| [`docs/product/HANDOFF_DIRECTIVE.md`](docs/product/HANDOFF_DIRECTIVE.md) | **Highest authority.** How version conflicts are resolved. |
| [`docs/product/MASTER_ARCHITECTURE_v2.md`](docs/product/MASTER_ARCHITECTURE_v2.md) | Current architecture canon — strategy family and core. |
| [`docs/product/ENGINE_OBSERVER_SCRIPTS_LAYER.md`](docs/product/ENGINE_OBSERVER_SCRIPTS_LAYER.md) | Engine, observer, and scripts layers. |
| [`docs/product/MASTER_UNIVERSE_CANON.md`](docs/product/MASTER_UNIVERSE_CANON.md) | Universe structure and documentation index. |
| [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) | Derived summary of the above. |
| [`docs/architecture/SOURCE_INVENTORY.md`](docs/architecture/SOURCE_INVENTORY.md) | What every legacy file is — and what it isn't. |
| [`CLAUDE.md`](CLAUDE.md) | Rules for AI agents working here. |
| [`docs/ai/DEVELOPMENT_WORKFLOW.md`](docs/ai/DEVELOPMENT_WORKFLOW.md) | Branches, commits, tests, definition of done. |

[`docs/product/MASTER_SPEC_v1.0.md`](docs/product/MASTER_SPEC_v1.0.md) is **superseded** and retained
as historical reference only.

## Architecture

```
External sources (MT5, TradingView, PineConnector, APIs, Calendar)
      -> Data Engine        normalization · validation · instrument resolver
      -> Core Engine        signal · risk · capital · execution · position
                            bucket · straddle · stops · trailing · trade state
      -> Strategy EAs  +  Observer Network  +  Scripts
      -> Telemetry -> External Agentic Brain -> recommendations -> (approval) -> config
```

Seven strategies, each an independent EA with its own signal engine, all consuming the same Core:

**ARK / Liquid Flow** (liquidity + market structure, aimed at indices) · **Jobbing** (US-open
opening-range breakout) · **Price Action** (structure, BOS/CHOCH) · **Gold** · **FX** · **BTC** ·
**Indices** (US500/US100/US30)

## Two mechanisms worth understanding early

**Bucket** — a portfolio of related positions (original trade + straddle + linked positions) tracked
as one aggregate. Bucket P/L and individual trade P/L are different concepts.

**Straddle recovery** — the straddle opens with its SL at *its own* breakeven, not the bucket's. When
the bucket's floating P/L reaches zero, the straddle SL moves to the bucket zero-floating level, the
original losing trade closes, and the straddle survives as the profit runner and trails.

## Layout

```
CORE/           shared engines — risk, execution, bucket, straddle, symbol, session, ...
STRATEGIES/     ARK, JOBBING, PRICE_ACTION, GOLD, FX, BTC, INDICES
OBSERVER/       observer core/network, telemetry, market/trade/bucket/system observers
SCRIPTS/        timing, data, backtest, session, diagnostics utilities
DATA/           MT5, External, PineConnector, validation
EXTERNAL_BRAIN/ telemetry, event stream, analytics, recommendation interface
BACKTEST/       per-strategy backtests sharing the same core engine
DEPLOYMENTS/    self-contained per-EA packages (EA + all required .mqh in one folder)
python/         data pipeline, analytics, external APIs, MT5 bridge
legacy/         preserved prior source — read-only reference
tests/          unit, integration, failure, regression
docs/           product canon and architecture
```

## Ground rules

- Trading logic is decided by the human product owner, never silently by an AI.
- MQL5 is the only execution authority; Python and AI components are advisory.
- If the AI is offline, NeoFL keeps trading deterministically.
- Missing data means `DATA_UNAVAILABLE → NO TRADE` — never a fabricated value.
- Gold resolution is semantic: `GOLD` and XAUUSD variants valid, `BTCXAU` rejected.
- Every deployable EA ships as one self-contained folder.
- No secrets in Git, ever.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

MQL5 compilation cannot be verified on macOS — MetaEditor is Windows-only. These tests check source
and repository contracts, not compilation or runtime behavior. Compilation and Strategy Tester results
must be reported separately from the Windows MT5 host.

## Environment

Development on macOS (Apple Silicon). MT5 execution runs on a Windows VPS/RDP host.
