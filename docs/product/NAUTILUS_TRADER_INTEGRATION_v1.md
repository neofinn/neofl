# NeoFL — NautilusTrader Integration Specification v1

**Status:** Approved architectural amendment  
**Date:** 2026-08-20  
**Scope:** Trading-engine, account-universe, market-data and execution infrastructure

## 1. Decision

NeoFL adopts **NautilusTrader as the external multi-asset trading-engine foundation** for the new account-connected execution/data plane.

This does **not** merge NeoFL strategy logic into NautilusTrader. NautilusTrader supplies deterministic trading infrastructure; NeoFL supplies the strategy/decision layer and product-specific risk/recovery semantics.

The existing MT5 architecture remains valid for legacy/self-contained EAs. The Nautilus integration is an additional execution/data path and becomes the preferred foundation for the connected-account universe.

## 2. New canonical architecture

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
                    normalized market state
                             │
                             ▼
                     NEOFL AGENTIC BRAIN
                             │
                      strategy decisions
                             │
                             ▼
                    NEOFL POLICY / RISK GATE
                             │
                             ▼
                    NAUTILUS EXECUTION ENGINE
                             │
                             ▼
                  BROKER / EXCHANGE / VENUE
                             │
                             ▼
               orders / fills / positions / account
                             │
                             └──────────► Brain state
```

## 3. Account universe rule

A connection is **not** bound to a single chart, symbol, strategy, or instrument.

For every connected trading account, the system must discover and maintain the **whole authorized tradable universe exposed by that connection**.

The universe contains, where the venue exposes them:

- instruments/symbols
- instrument identifiers and venue mappings
- asset class
- quote/base currency metadata
- trading status
- price/tick specifications
- quantity/lot specifications
- contract specifications
- margin/risk metadata
- trading hours/session metadata
- supported order types
- account permissions
- current positions and working orders

### Hard rule

> **MCP and the Brain receive the account's authorized tradable universe, not merely the instrument displayed on a chart.**

A chart is a visualization context only. It is never the boundary of what the Brain may analyze or what the execution layer may make available.

The Brain may select **any instrument in the connected account's authorized universe**, subject to policy, risk, market-data availability, and execution constraints.

## 4. Connection ownership

Credentials and connection state belong to the **Admin Panel / connection manager**.

No strategy or Brain component should hard-code broker/API credentials.

The Admin Panel manages:

- connection creation
- credential/token storage and rotation
- account discovery
- permissions
- connection health
- venue selection
- allowed-universe policy
- audit metadata

The Brain receives connection capabilities through a controlled interface; it does not own secrets.

## 5. MCP rule

MCP is a **data feeder and context channel** and therefore has a direct data connection to the Brain.

MCP does not become the execution authority.

```text
MCP → Brain
MCP → approved data services

Brain → policy/risk → Nautilus execution

Admin Panel → connection management
```

## 6. Execution authority

NautilusTrader becomes the execution/data-plane foundation for connected-account trading.

The Brain must never speak directly to an individual broker protocol when a Nautilus adapter exists.

Execution flow:

```text
Brain decision
    ↓
canonical order intent
    ↓
NeoFL policy/risk gate
    ↓
Nautilus order submission
    ↓
venue adapter
    ↓
broker/exchange
    ↓
ack / reject / fill
    ↓
Nautilus state
    ↓
NeoFL state + Brain telemetry
```

## 7. Separation of responsibilities

### NeoFL Brain

- market reasoning
- cross-instrument analysis
- strategy selection
- regime interpretation
- signal generation
- portfolio-level decisions
- research and diagnostics

### NeoFL policy/risk gate

- account permissions
- instrument eligibility
- exposure limits
- capital rules
- order validation
- safety controls
- kill switches
- strategy/account restrictions

### NautilusTrader

- market-data handling
- venue adapters
- order lifecycle
- execution routing
- fills
- positions/orders state
- reconciliation and trading-engine mechanics

### Admin Panel

- connections
- credentials/tokens
- account discovery
- user permissions
- universe policy
- operational controls

### MCP

- external/connected data delivery to the Brain
- normalized context requests
- Brain-facing data tools

## 8. Universe discovery lifecycle

When a connection starts:

```text
CONNECT
  ↓
AUTHENTICATE
  ↓
DISCOVER ACCOUNT(S)
  ↓
DISCOVER INSTRUMENTS
  ↓
DISCOVER PERMISSIONS / TRADING STATUS
  ↓
NORMALIZE INSTRUMENT METADATA
  ↓
BUILD ACCOUNT UNIVERSE
  ↓
PUBLISH UNIVERSE TO BRAIN
  ↓
STREAM MARKET / ACCOUNT / ORDER STATE
```

Universe changes must be event-driven or periodically reconciled so newly listed, disabled, or permission-restricted instruments are reflected without redeploying the Brain.

## 9. Canonical instrument identity

NeoFL must not assume broker symbol names are globally unique or portable.

The canonical identity should include:

```text
venue
instrument_id
raw_symbol
normalized_symbol
asset_class
base_currency
quote_currency
contract_spec
connection_id
```

Human-readable aliases remain useful, but execution must use the venue-specific canonical identifier.

## 10. Chart independence

The following is explicitly prohibited:

```text
current chart = only tradable instrument
```

The correct model is:

```text
Current chart
     │
     └── visualization/context only

Connected account
     │
     └── full authorized tradable universe
              │
              ├── instrument A
              ├── instrument B
              ├── instrument C
              └── ...
```

## 11. Safety boundary

The Brain may only submit an order for an instrument that is present in the current connection universe and passes the NeoFL policy/risk gate.

If universe data is unavailable, stale beyond policy, contradictory, or missing required instrument metadata:

```text
DATA_UNAVAILABLE / UNRESOLVED
          ↓
       NO TRADE
```

No symbol may be inferred from a chart name alone.

## 12. Existing NeoFL strategies

The existing strategy family remains independent:

- ARK / Liquid Flow
- Jobbing
- Price Action
- Gold
- FX
- BTC
- Indices

NautilusTrader is infrastructure. It does not collapse these strategies into one signal engine.

## 13. MT5 coexistence

MT5 remains supported for the existing deterministic EA deployments and legacy strategy work.

The architecture therefore has two execution planes during migration:

```text
LEGACY / SELF-CONTAINED MT5 PLANE
Strategy EA → NeoFL Core → MT5

CONNECTED MULTI-VENUE PLANE
Brain → NeoFL Policy/Risk → NautilusTrader → Venue
```

Shared NeoFL concepts such as account risk, strategy identity, bucket/recovery state, telemetry and canonical instrument identity should converge over time, but migration must not break existing MT5 EAs.

## 14. Migration order

1. Add Nautilus integration boundary and connection abstraction.
2. Implement account and full-universe discovery.
3. Normalize instruments and permissions.
4. Connect MCP directly to the Brain data interface.
5. Feed Nautilus market/account state into the canonical Brain state model.
6. Add policy/risk validation before order submission.
7. Add one venue adapter and paper/sandbox validation.
8. Validate order lifecycle, fills, reconciliation and failure recovery.
9. Expand venue coverage.
10. Migrate strategies incrementally without merging strategy logic.

## 15. Non-negotiable constraints

- The Brain is not restricted to the chart instrument.
- The connected account's authorized universe is the tradable boundary.
- Credentials remain outside the Brain.
- MCP feeds the Brain directly but does not execute orders.
- NautilusTrader is the execution/data-plane foundation for the new connected-account path.
- NeoFL policy/risk remains the final pre-trade gate.
- Strategy logic remains independent.
- Missing/invalid universe data means no trade.
- Existing MT5 deployments remain operational during migration.
