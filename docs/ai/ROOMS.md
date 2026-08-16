# Working rooms

NeoFL is developed across several sessions rather than one. This file says which room owns what, so
two sessions don't edit the same thing from different assumptions.

## The rooms

| Room | Open a session in | Owns |
|---|---|---|
| **Infrastructure** (this one) | repository root | CORE engines, OBSERVER, DATA, SCRIPTS, EXTERNAL_BRAIN, build tooling, canon, decisions, tests |
| ARK | `STRATEGIES/ARK/` | ARK signal logic only |
| Jobbing | `STRATEGIES/JOBBING/` | Jobbing signal logic only |
| Price Action | `STRATEGIES/PRICE_ACTION/` | Price Action signal logic only |
| Gold | `STRATEGIES/GOLD/` | Gold signal logic only |
| FX | `STRATEGIES/FX/` | FX signal logic only |
| BTC | `STRATEGIES/BTC/` | BTC signal logic only |
| Indices | `STRATEGIES/INDICES/` | Indices signal logic only |

Each strategy directory has its own `CLAUDE.md`. A session opened there picks it up automatically and
arrives knowing that strategy's rules, its legacy ancestors, and its traps — without having to be
told again that `NeoFL_ARK_Backtest_v3_00.mq5` is not ARK.

## Why the split

The canon's golden rule is *don't duplicate infrastructure, don't merge strategy logic*. Rooms
enforce the second half structurally: a session scoped to one strategy is far less likely to reach
into another's signal engine, or to "fix" one EA by changing a shared engine six others depend on.

## The rule that keeps it safe

**Shared code changes in the infrastructure room. Only there.**

A strategy room that needs something from CORE — a new engine, a changed signature, a bug fix —
does not edit CORE. It writes down what it needs and hands it to the infrastructure room. That room
can see every consumer; a strategy room cannot.

If a strategy room finds itself editing outside its own directory, that is the signal it is doing
infrastructure work in the wrong place.

## Handing work between rooms

Sessions can message each other directly. From any room:

> "Send this to the infrastructure session: Jobbing needs a CHOCH detector in CORE — the legacy
> `RequireM5CHoCH` input was never implemented."

The message lands as a user turn in the target session, labelled with its origin. Use it for handoffs
and findings, not to run work remotely.

## Starting a strategy room

Open a new Claude Code session with its working directory set to that strategy folder, for example:

```bash
cd ~/Desktop/NeoFL/STRATEGIES/JOBBING
```

Then start there. The room's `CLAUDE.md` loads automatically. Worth saying in the first message which
strategy it is and what you want built, so the session's title reflects it.

## Build order still applies

Strategies are consumers of a stable engine. Steps 1–9 are Core, Observer, and Logging; strategies
begin at step 10. A strategy room opened before its dependencies exist will be blocked on CORE — which
is expected, and is a reason to keep the infrastructure room ahead of the others.

Current state: Symbol Resolver done (step 2). Market Data + Session + Calendar in progress (step 3).
ARK's signal rules remain unspecified and block step 10 regardless of Core progress.
