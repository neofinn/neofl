# NeoFL

A modular algorithmic trading platform for MetaTrader 5, with a new multi-venue connected-account execution/data plane built around NautilusTrader.

NeoFL is not a collection of unrelated EAs. It is one shared trading architecture with independent strategies, a full-account universe model, an observer network, an external agentic Brain, and deterministic execution infrastructure.

> **Don't duplicate infrastructure. Don't merge strategy logic.**

## Status

Repository scaffolding, preserved legacy source, architecture canon, and the **NautilusTrader connected-account architecture amendment** are now established. The Nautilus integration is being introduced as an additional execution/data plane; existing MT5 deployments remain supported during migration.

The new connected-account rule is fundamental:

> **The Brain is bound to the whole authorized tradable universe of the connected account, not to the instrument shown on a chart.**

See [`docs/product/NAUTILUS_TRADER_INTEGRATION_v1.md`](docs/product/NAUTILUS_TRADER_INTEGRATION_v1.md).

## Start here

| Document | What it is |
|---|---|
| [`docs/product/HANDOFF_DIRECTIVE.md`](docs/product/HANDOFF_DIRECTIVE.md) | Highest-authority historical architecture governance. |
| [`docs/product/MASTER_ARCHITECTURE_v2.md`](docs/product/MASTER_ARCHITECTURE_v2.md) | Current NeoFL architecture canon. |
| [`docs/product/MASTER_UNIVERSE_CANON.md`](docs/product/MASTER_UNIVERSE_CANON.md) | Existing canonical universe and strategy structure. |
| [`docs/product/NAUTILUS_TRADER_INTEGRATION_v1.md`](docs/product/NAUTILUS_TRADER_INTEGRATION_v1.md) | **Current connected-account / full-universe / NautilusTrader amendment.** |
| [`docs/product/ENGINE_OBSERVER_SCRIPTS_LAYER.md`](docs/product/ENGINE_OBSERVER_SCRIPTS_LAYER.md) | Engine, observer, and scripts layers. |
| [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) | Derived architecture summary. |
| [`docs/architecture/SOURCE_INVENTORY.md`](docs/architecture/SOURCE_INVENTORY.md) | Legacy source inventory. |
| [`CLAUDE.md`](CLAUDE.md) | Rules for AI agents working here. |

## Connected-account architecture

```text
                         NEOFL ADMIN PANEL
                               │
                 connections / credentials / policy
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
        MCP DATA PLANE                   ACCOUNT CONNECTIONS
              │                                 │
              │                                 ▼
              │                         NAUTILUS ADAPTERS
              │                                 │
              └──────────────┬──────────────────┘
                             ▼
                    NAUTILUS DATA ENGINE
                             │
                             ▼
                     NEOFL AGENTIC BRAIN
                             │
                             ▼
                    NEOFL POLICY / RISK GATE
                             │
                             ▼
                    NAUTILUS EXECUTION ENGINE
                             │
                             ▼
                  BROKER / EXCHANGE / VENUE
```

### Universe rule

A connected account exposes a **full authorized tradable universe**. The Brain may analyze and select any instrument in that universe, subject to permissions, data availability, NeoFL policy, and risk controls.

The chart is only a visualization/context selection. It is **not** the execution boundary.

The system must discover and maintain, where available:

- instruments and venue identifiers
- asset class and currency metadata
- trading status and permissions
- tick/price/quantity specifications
- contract and margin metadata
- sessions/trading hours
- supported order types
- current orders and positions

No instrument may be inferred from a chart name alone.

## Responsibility split

**Admin Panel** — owns connections, credentials/tokens, account discovery, permissions, and universe policy.

**MCP** — feeds data/context directly to the Brain; it is not execution authority.

**Brain** — performs market reasoning, strategy selection, analysis and order-intent generation.

**NeoFL Policy/Risk Gate** — validates account permissions, instrument eligibility, exposure, capital and safety constraints.

**NautilusTrader** — supplies the connected-account market-data and execution infrastructure, including venue adapters and order/fill lifecycle.

**MT5** — remains the deterministic execution plane for existing/self-contained EA deployments during migration.

## Existing strategy universe

Seven strategies remain independent:

**ARK / Liquid Flow** · **Jobbing** · **Price Action** · **Gold** · **FX** · **BTC** · **Indices**

NautilusTrader is infrastructure. It does not merge their signal logic.

## Legacy architecture

The existing MT5 architecture remains valid:

```text
External sources (MT5, TradingView, PineConnector, APIs, Calendar)
      -> Data Engine        normalization · validation · instrument resolver
      -> Core Engine        signal · risk · capital · execution · position
                            bucket · straddle · stops · trailing · trade state
      -> Strategy EAs  +  Observer Network  +  Scripts
      -> Telemetry -> External Agentic Brain -> recommendations -> controlled config
```

## Safety and data-quality rules

- The Brain is never limited to the chart instrument.
- The connected account's authorized universe is the tradable boundary.
- Credentials are never embedded in strategy/Brain code.
- MCP has direct Brain connectivity for data/context but cannot execute orders.
- NautilusTrader is the execution/data-plane foundation for the new connected-account path.
- NeoFL policy/risk is the final pre-trade gate.
- Missing, stale, contradictory, or unresolved universe data means `DATA_UNAVAILABLE → NO TRADE`.
- Gold resolution remains semantic: `GOLD` and XAUUSD variants valid, `BTCXAU` rejected.
- Strategy logic remains isolated.
- Every deployable MT5 EA ships as one self-contained folder.
- No secrets in Git, ever — **this repository is public**.

## Layout

```text
CORE/           shared NeoFL engines
STRATEGIES/     ARK, JOBBING, PRICE_ACTION, GOLD, FX, BTC, INDICES
OBSERVER/       observer core/network and telemetry
SCRIPTS/        timing, data, backtest, session and diagnostics
DATA/           MT5, external and validation data
EXTERNAL_BRAIN/ telemetry, event stream, analytics, Brain interfaces
BACKTEST/       per-strategy backtests
DEPLOYMENTS/    self-contained per-EA packages
python/         data pipeline, analytics, external APIs, MT5 bridge and future Nautilus integration
legacy/         preserved prior source — read-only reference
tests/          unit, integration, failure and regression tests
docs/           product canon and architecture
```

## Build and test

```bash
python3 -m unittest discover -s tests -t .
tools/mql5_compile.sh <dir-or-file.mq5>
```

MQL5 compilation remains the validation path for MT5 EA deployments. Nautilus integration will be validated separately through its Python/Rust trading-engine test path before any live connected-account execution is enabled.

## Migration

The migration is incremental:

1. Establish connection and full-universe discovery.
2. Normalize account/instrument metadata.
3. Connect MCP directly to the Brain data interface.
4. Feed Nautilus market/account state into the canonical Brain state model.
5. Add NeoFL policy/risk gating.
6. Validate paper/sandbox execution and complete order lifecycle.
7. Add venue adapters incrementally.
8. Migrate strategies without merging their signal logic.

Existing MT5 trading must not be broken merely to introduce the new connected-account plane.
