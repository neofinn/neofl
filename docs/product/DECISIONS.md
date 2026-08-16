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
