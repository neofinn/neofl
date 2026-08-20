# NeoFL Master Universe — Canonical Amendment

**Date:** 2026-08-20  
**Supersedes conflicting connected-account assumptions in earlier universe descriptions.**

This amendment is part of the NeoFL Master Universe. The historical `MASTER_UNIVERSE_CANON.md` remains preserved, while this dated amendment defines the current connected-account execution/data architecture.

## 1. Parent universe — updated

```text
NEOFL UNIVERSE
│
├── NEOFL ADMIN / CONNECTION PLANE
│   ├── User Panel
│   ├── Admin Panel
│   ├── Connection Manager
│   ├── Credential / Token Management
│   ├── Account Discovery
│   ├── Permission / Policy Management
│   └── Full Tradable-Universe Discovery
│
├── MCP DATA PLANE
│   ├── Direct Brain Data Connection
│   ├── External Data Feeds
│   ├── Context / Market Data
│   └── Data Normalization
│
├── NEOFL AGENTIC BRAIN
│   ├── Market Reasoning
│   ├── Strategy Selection
│   ├── Signal / Order Intent
│   ├── Portfolio Analysis
│   ├── Research
│   └── Diagnostics
│
├── NEOFL POLICY / RISK GATE
│   ├── Account Permission Validation
│   ├── Instrument Eligibility
│   ├── Capital / Exposure Limits
│   ├── Safety Controls
│   └── Kill Switches
│
├── NAUTILUS TRADING ENGINE
│   ├── Data Engine
│   ├── Execution Engine
│   ├── Venue Adapters
│   ├── Order Lifecycle
│   ├── Fill Lifecycle
│   ├── Position / Account State
│   └── Reconciliation
│
├── VENUE UNIVERSE
│   ├── Broker Accounts
│   ├── Exchanges
│   ├── FX Venues
│   ├── Crypto Venues
│   ├── Equities / Futures / Options where supported
│   └── Other Connected Markets
│
├── STRATEGY UNIVERSE
│   ├── NeoFL ARK / Liquid Flow
│   ├── NeoFL Jobbing
│   ├── NeoFL Price Action
│   ├── NeoFL Gold
│   ├── NeoFL FX
│   ├── NeoFL BTC
│   └── NeoFL Indices
│
├── OBSERVER / TELEMETRY UNIVERSE
│   ├── Market State
│   ├── Account State
│   ├── Orders / Fills
│   ├── Positions
│   ├── Bucket / Straddle State
│   └── System / Connection State
│
└── LEGACY MT5 PLANE
    ├── Existing NeoFL EAs
    ├── MT5 Core
    └── Deterministic MT5 Execution
```

## 2. Full account universe — hard rule

The connected account is the **universe boundary**.

The chart is not.

```text
CONNECTED ACCOUNT
       ↓
AUTHORIZED TRADABLE UNIVERSE
       ↓
┌────────┬────────┬────────┬──────────┐
│ Symbol │ Symbol │ Symbol │   ...    │
│   A    │   B    │   C    │          │
└────────┴────────┴────────┴──────────┘
       ↓
       BRAIN
       ↓
SELECT ANY ELIGIBLE INSTRUMENT
       ↓
POLICY / RISK
       ↓
NAUTILUS EXECUTION
```

The Brain is therefore **not a chart-bound agent**.

A user viewing EURUSD does not prevent the Brain from analyzing or trading another authorized instrument such as XAUUSD, BTCUSD, US100, or another venue instrument when that instrument exists in the connected account universe and passes policy/risk/data checks.

## 3. Canonical connection identity

Every connected account must expose a connection-scoped identity:

```text
connection_id
venue
account_id
account_type
permissions
currency
balance/equity state
instrument universe
connection health
```

Every instrument must retain venue-specific identity:

```text
connection_id
venue
instrument_id
raw_symbol
normalized_symbol
asset_class
base_currency
quote_currency
contract_spec
trading_status
permissions
```

## 4. MCP relationship

MCP is now explicitly part of the **data plane** and has a direct connection to the Brain.

```text
MCP ───────────────► Brain
 │                    │
 └── data/context     └── order intent
                              │
                              ▼
                         Policy/Risk
                              │
                              ▼
                          Nautilus
```

MCP does not hold execution authority merely because it supplies data.

## 5. Admin Panel relationship

Nothing connects directly to the Brain for credential management.

```text
User
 ↓
Admin/User Panel
 ↓
Connection Manager
 ↓
Credentials / Tokens / Permissions
 ↓
Nautilus adapters + approved Brain capabilities
```

The Brain receives capabilities and account state, not uncontrolled credential ownership.

## 6. NautilusTrader position in the universe

NautilusTrader is an **infrastructure layer**, not a NeoFL strategy.

Its role is to provide the connected-account trading/data engine so NeoFL does not rebuild broker/exchange execution plumbing.

```text
NeoFL Strategy / Brain
        ↓
NeoFL Order Intent
        ↓
NeoFL Policy / Risk
        ↓
NautilusTrader
        ↓
Venue Adapter
        ↓
Broker / Exchange
```

## 7. Strategy independence remains unchanged

The seven strategy universes remain independent.

NautilusTrader does not change:

- ARK signal rules
- Jobbing opening-range rules
- Price Action signal rules
- Gold semantic symbol rules
- FX strategy rules
- BTC strategy rules
- Indices strategy rules

It changes the **infrastructure available underneath them**.

## 8. MT5 coexistence

Existing MT5 deployments are not deleted or silently rewritten.

During migration:

```text
MT5 EAs ─────────► MT5 execution plane

Brain ───────────► NeoFL Policy/Risk
                         │
                         ▼
                    Nautilus plane
```

The two paths may coexist until each strategy/venue has passed its own validation gates.

## 9. Data-quality boundary

If the account universe or required instrument metadata is unavailable:

```text
UNIVERSE_UNAVAILABLE
        ↓
DATA_UNAVAILABLE
        ↓
NO TRADE
```

The system must never guess an instrument, permissions, contract specification, or venue from a chart label.

## 10. Current implementation target

The next engineering sequence is:

1. Connection abstraction.
2. Account discovery.
3. Full tradable-universe discovery.
4. Canonical instrument normalization.
5. MCP → Brain direct data channel.
6. Nautilus market/account state → Brain.
7. NeoFL policy/risk gate.
8. Paper/sandbox execution.
9. Order/fill/reconciliation verification.
10. Incremental live-venue rollout.

This amendment is the active universe direction for the new connected-account plane as of **2026-08-20**.
