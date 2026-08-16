# NeoFL — instructions for AI agents

NeoFL is an AI-native algorithmic trading platform targeting GOLD/XAUUSD on MT5. Real money is the
eventual endpoint, so the constraints below are hard rules, not style preferences.

**Read first:** `docs/product/MASTER_SPEC_v1.0.md` (product source of truth),
`docs/architecture/ARCHITECTURE.md`, `docs/architecture/SOURCE_INVENTORY.md`.

## The line you do not cross

**Trading logic belongs to the human product owner.** You may not add, remove, or alter an entry rule,
exit rule, filter, threshold, or risk parameter because you believe it performs better.

If you think a strategy is wrong: state the problem, give evidence, propose the change, explain the
expected effect and the risk, and **ask**. Then wait.

Implementation detail — data structures, refactors, tests, tooling, docs — is yours to decide.

## Do not fabricate

An unverified claim about a trading system is worse than no claim.

- Never say code compiled unless it actually compiled. MQL5 compilation requires MetaEditor on
  Windows and **cannot be verified on this Mac**. Say so plainly.
- Never say a trade executed unless you verified the execution.
- Never invent market data, broker behavior, or API responses.
- Report failures honestly, including your own.

Static checks over `.mq5` text are useful, but they verify *contract presence*, not correctness.
Never describe them as compilation or as proof the strategy works.

## Architecture constraints

From the master spec; violating these is a defect regardless of how well it works:

1. Trend and ARK are **separate EAs**. Do not merge them or extend the legacy monolith.
2. MQL5 is the **only** execution authority. Python and AI components are advisory.
3. The Data Bridge **never** makes trading decisions.
4. No LLM gets live order authority.
5. Coordination is the lightweight `ARK_STATE` protocol — do not build a conflict engine.
6. Symbol mapping is configuration, never hard-coded in strategy logic.
7. Gold only. Never trade `BTCXAU`, `ETHXAU`, or synthetic cross-pairs.

## Legacy code

`legacy/` is **read-only reference**. Preserve it; never edit or delete it. Nothing in it is the
current architecture, and two things in it will actively mislead you:

- `NeoFL_ARK_Backtest_v3_00.mq5` is an opening-range strategy that shares only a *name* with the ARK
  engine described in the spec. It is not ARK.
- The Candle Revisit / Master Brain family (v3.x) is a different strategy altogether, despite being
  the most actively developed legacy line.

The genuinely relevant reference is `NeoFL_GOLD_6.6_ARK_PREEXECUTION_LOCK.mq5`, which is the closest
ancestor of the spec's ARK pre-execution lock.

## Secrets

Never request, log, echo, commit, or place in code: broker credentials, API keys or secrets, exchange
credentials, AI API keys, SSH keys, or account passwords. Environment variables and untracked local
config only. `.gitignore` covers the common cases — do not work around it.

## Workflow

- Git is the source of truth; commit meaningful changes.
- Use branches for significant work.
- Write tests for new functionality; run them before claiming completion.
- Keep `CHANGELOG.md` current.
- Any change to trading behavior must state: what changed, why, expected effect, risk, tests
  performed, and whether product approval is required.

## Approval gates

GATE 1 product behavior · GATE 2 code review · GATE 3 demo execution validation · GATE 4 live
deployment. Automate everything else that is safe to automate.

## Current phase

**Phase 1** — repository, inventory, AI instructions. Phase 2 (formal Trend/ARK specifications) is
**blocked** on the product owner supplying the actual ARK detection rules; they exist in no file here.

Do not start writing Trend or ARK strategy code until Phase 2 is agreed.
