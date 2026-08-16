# Product Owner Decisions

Append-only record of decisions made in conversation rather than in the captured canon documents.

The canon files in this directory are verbatim transcripts and are never edited. Decisions taken
afterwards live here. Per `HANDOFF_DIRECTIVE.md`, a later decision supersedes an earlier one — so
entries below outrank the canon where they conflict, and the conflict must be stated explicitly.

Format: date, decision, rationale, and what it changes in practice.

---

## D-001 — AI processes data only; it holds no order authority

**Date:** 2026-08-16
**Decided by:** product owner
**Status:** active

### Decision

AI components process and analyze data. They do not place, modify, or close orders, and hold no
trade authority of any kind.

### Context

Raised after discovering that MetaTrader 5's built-in assistant was configured with
`PermissionsTrade = 1` — granting an AI trade authority through a third-party inference endpoint
(`api.inferdeck.net`). See `docs/testing/RUNNING.md`.

### Rationale

Confirms and sharpens what the canon already states in three places:

> Do NOT give an LLM unrestricted live order authority.
> No AI component should bypass risk controls or human live-deployment approval.
> External AI must not become a single point of failure.

Beyond principle, there is an evidence problem: if any AI can trade the account NeoFL trades, the
execution evidence NeoFL's own demo validation depends on becomes unattributable. NeoFL could not
prove which order came from which engine.

### What this changes in practice

**Permitted for AI — reading and analysis:**
- market data, symbols, contract specifications, history
- positions, orders, account state, logs
- telemetry and observer output
- diagnostics, research, backtest analysis, recommendations

**Not permitted for AI — any write that reaches the market:**
- opening, modifying, or closing positions
- placing, amending, or deleting pending orders
- changing SL/TP or trailing state on live positions
- altering live risk or capital parameters

Recommendations flow `AI → validation/policy → human approval → configuration → EA`. Never directly.

### Consequences

1. **MT5 MCP connection is aligned with this decision** when used for data access. Reading market
   data, symbols, positions, and history over the MetaTrader MCP server is explicitly in scope; using
   it to place orders is not. This makes the MCP route attractive rather than risky.
2. **`PermissionsTrade` should be `0`** in MT5's assistant configuration. It was `1` when discovered.
   Setting lives under Tools → Options. Owner action — NeoFL does not modify terminal settings.
3. The Agentic Brain (build step 17) remains advisory-only, as the canon already specifies.
4. Deterministic operation is unaffected: if every AI component is offline, NeoFL keeps trading.

---

## D-002 — The AI observes the data feed and verifies the engines process it correctly

**Date:** 2026-08-16
**Decided by:** product owner
**Status:** active
**Refines:** D-001

### Decision

The AI observes the data feed, and observes whether the engine scripts are processing that data as
they should. It is a correctness monitor, not merely a passive analyst.

### Why this is a sharpening, not a repetition

D-001 said what the AI may not do. D-002 says what it is *for*. The distinction matters because
"analyze the results" and "verify the processing was correct" demand different things of the system:

- Judging *results* needs outputs — P/L, trades taken, win rate.
- Judging *correctness* needs **inputs, the decision, and the reasoning** — enough to independently
  re-derive what the engine should have concluded and compare it against what it did conclude.

An engine that emits only `BUY XAUUSD 0.01` cannot be checked. An engine that emits *"M15 range
2412.30/2408.10, M5 close 2413.05 above range, CHOCH confirmed, therefore LONG"* can be, because a
verifier can evaluate whether that conclusion actually follows from those inputs.

### Engineering consequence: every Core engine emits decision provenance

This is now a design requirement for all Core modules, not something bolted on at build step 9.

On every meaningful decision, an engine emits:

| Field | Meaning |
|---|---|
| inputs | the data the decision was made from, with source and timestamp |
| data quality | `DATA_OK` / `DELAYED` / `INCOMPLETE` / `UNAVAILABLE` / `INVALID` |
| decision | what was concluded |
| reason | why — the rule or threshold that fired |
| rejections | what was considered and declined, **and why** |

The last row is the one most often skipped and the most valuable. Silence is ambiguous: an engine
emitting nothing might be correctly finding no setup, or might be broken and blind — and from the
outside those look identical. An engine that emits *"no trade: ATR 18 points, below minimum 50"* is
verifiably working.

**Absence of a signal must itself be an observable event.**

### The pattern already exists

`CORE/NeoFL_SymbolResolver` was built this way before this decision was recorded. It does not return
a bare boolean — it populates `reject_reason`:

```
BTCXAU -> rejected: "XAU present as quote currency, not base; not the gold instrument"
```

An observer reading that can confirm the resolver rejected `BTCXAU` for the *right* reason rather
than by accident. Had it merely returned `false`, a resolver that rejected everything would be
indistinguishable from a correct one.

This is the house pattern. Every subsequent Core engine follows it.

### Consequences

1. Engines are built observable from the first line, not instrumented afterwards.
2. The Observer Network (build step 9) becomes a consumer of a contract the engines already honor,
   instead of having to reverse-engineer intent from outputs.
3. Verification works offline: provenance records are replayable, so correctness can be checked
   against historical data without touching a live account — entirely within D-001.
4. This grants no authority to correct what it finds. Findings are reported; remediation still flows
   through human approval per D-001.

---

## D-003 — Sessions are global; gold's day spans Asian open to American close

**Date:** 2026-08-16
**Decided by:** product owner
**Status:** active
**Supersedes:** the US-only session assumption in the first Session engine build

### Decision

Session timing is a **global** concern, not a US one. The system must know the trading
hours of every market it touches.

- **Gold trades in every zone.** Its trading day **starts with the Asian session and ends
  with the American session.**
- **Global major indices each have their own hours** — the system must know each, not
  apply one schedule to all.

### Why the first build was wrong

`NeoFL_Session.mqh` modelled only the US cash session (09:30–16:00 ET). That is correct for
US indices and wrong for everything else:

- Gold would appear "closed" for the roughly 14 hours a day it is actively traded in Asia
  and Europe.
- DAX, FTSE and Nikkei would be evaluated against New York's clock.

### The hard part: DST is not one rule

Each region switches on different dates, and one does not switch at all. Applying US dates
globally is wrong for several weeks a year — precisely the weeks where a session boundary
silently shifts by an hour and nobody notices until a trade fires at the wrong time.

| Region | DST rule |
|---|---|
| US | second Sunday March → first Sunday November |
| EU / UK | last Sunday March → last Sunday October |
| Australia | first Sunday October → first Sunday April (southern hemisphere, inverted) |
| Japan | **no DST at all** |

There are also weeks where US and EU have switched but the other has not, so the
London–New York overlap moves. That overlap is the highest-liquidity window of the day, so
getting it wrong matters.

### What this changes in practice

1. Sessions are defined per market: local open/close, base UTC offset, and DST rule.
2. All comparisons happen in GMT. Broker server time remains untrusted.
3. The gold trading day is derived: **Asian session open → American session close.**
4. Session overlaps are exposed, because liquidity concentrates there.
5. Indices consult their own exchange's hours, never a shared default.

### Consequences

- The Jobbing strategy's US-open opening range is unaffected — it still keys off New York,
  which is now one market among several rather than the only one modelled.
- Strategies ask "is my market open?" rather than assuming. A strategy that cannot answer
  that for its instrument is not ready to trade it.
