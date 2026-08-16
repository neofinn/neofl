# NeoFL Architecture

Derived from the master spec (`docs/product/MASTER_SPEC_v1.0.md`). Where this document and the master
spec disagree, the master spec wins and this document is the bug.

## System shape

```
                 EXTERNAL DATA SOURCES
        (CME futures/order-flow, TradingView, Calendar, News)
                          |
                     DATA GATEWAY            [Python: external-data/]
                          |
                  NORMALIZATION LAYER        common schema, §20
                          |
                   REAL-TIME STATE           [Redis]
                          |
                      MT5 BRIDGE             [mt5/DataBridge/]  validate/timestamp/map — NEVER decides
                          |
              +-----------+-----------+
              |                       |
          TREND EA                 ARK EA    [mt5/TrendEA/, mt5/ARKEA/]
       M5 + M15 + M30           M15 event engine
              |                       |
             M1                      M1
              |                       |
        Trend trades             ARK trades
              +-----------+-----------+
                          |
                    SHARED STATE              execution-slot protocol, §12
                          |
                        MT5                   execution boundary
```

## Non-negotiable boundaries

These come straight from the spec and constrain every later decision:

1. **Trend and ARK are separate EAs.** Not a monolith with two modules. The legacy GOLD 5.x/6.x line
   is monolithic and must be split rather than extended (§7).
2. **MQL5 is the only execution authority.** Python, the gateway, and any AI component are advisory.
   Nothing external may bypass risk controls or place orders (§21, §22, §25).
3. **The Data Bridge makes no trading decisions.** It validates, timestamps, maps symbols, and exposes
   state. That is all (§21).
4. **No LLM gets live order authority.** The Agentic Brain is advisory output only (§25).
5. **No strategy conflict engine.** Coordination is a lightweight shared execution-state protocol,
   nothing more (§12).
6. **Symbol mapping is configuration, never hard-coded in strategy logic** (§14).

## Trend / ARK coordination

The single piece of shared state between the two EAs. ARK reserves the execution slot *before*
sending its order — this is the fix for the historical race where both engines executed simultaneously.

```
ARK_STATE:  0 IDLE | 1 EVENT_DETECTED | 2 PRE_EXECUTION_LOCK
            3 POSITION_ACTIVE | 4 EXITING | 5 ERROR

ARK_DIRECTION:  -1 SHORT | 0 NONE | +1 LONG
```

```
ARK detects qualified event
  -> ARK_STATE = PRE_EXECUTION_LOCK
  -> TREND blocks NEW entries
  -> ARK sends order
       success -> POSITION_ACTIVE
       failure -> error/release state
  -> ARK manages position -> closes
  -> ARK_STATE = IDLE
  -> TREND resumes NEW entries
```

Two rules that are easy to get wrong:

- The lock blocks **new Trend entries only**. Existing Trend positions are *not* closed because ARK
  saw an event (§12).
- Every path out of `PRE_EXECUTION_LOCK` must release the lock, including failures and errors. A
  wedged lock is a permanent deadlock, which §13 forbids. Whatever transport carries this state needs
  a staleness timeout as a backstop.

Transport is undecided. MT5 global variables (the legacy Observer/MasterBrain approach) are the
obvious low-friction option for two EAs in one terminal. To be settled in Phase 3.

## Engine responsibilities

**Trend EA** — short-term intraday. M5 identifies trend (primary), M15 confirms direction, M30 judges
whether the trend survives, M1 times execution and trails. Emits `BULLISH | BEARISH | NEUTRAL` plus
confidence. Explicitly must *not* accrue slow confirmation layers that leave it idle (§8, §9).

**ARK EA** — independent event engine. Liquidity, sweeps, BOS, CHOCH, SMC, supply/demand,
displacement, order blocks. M15 for event context, M1 for execution. ARK need not agree with Trend
and may trade alone (§10, §11).

> ⚠️ The ARK detection mathematics are **not specified anywhere in the source or the spec**. Legacy
> `ARKSignal()` is an empty stub; the v3.00 backtest "ARK" is an unrelated opening-range strategy.
> Phase 2 cannot complete without the product owner supplying these rules. See `SOURCE_INVENTORY.md`.

## Live vs replay

External APIs are not available inside the MT5 Strategy Tester, so the same strategy logic must run
against two data paths: live gateway state, and a replay engine feeding historical external data in
the same normalized schema (§23). Designing for this from the start is cheaper than retrofitting it —
strategy code must never call an external API directly.

## Storage

- **PostgreSQL** — history, events, trades, logs, strategy states.
- **Redis** — live state: `ARK_STATE`, `TREND_STATE`, news, CME.

Neither is needed before Phase 5. Do not stand them up early (§4).

## Phases

0 workstation · **1 repo + inventory + AI instructions** · 2 formal Trend/ARK specs ·
3 standalone Trend + ARK · 4 MT5 bridge · 5 data gateway · 6 CME/TradingView/calendar ·
7 replay engine · 8 Agentic Brain · 9 automated research · 10 demo execution · 11 human approval ·
12 controlled live.

Phase 1 is in progress. The Agentic Brain is not to be jumped to (§31).

## Current state

Scaffolding and legacy preservation only. No Trend EA, no ARK EA, no bridge, no gateway. Everything
under `legacy/` is reference material and none of it is the target architecture.
