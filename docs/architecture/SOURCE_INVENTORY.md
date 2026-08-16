# NeoFL Legacy Source Inventory

Audit date: 2026-08-16. Covers every `.mq5` / `.mqh` found on this workstation.
Originals remain in `~/Downloads`; `legacy/` holds a deduplicated, classified copy.

Per master spec §6 and §34, **nothing here is the current production architecture.** All of it is
reference material. The target architecture (separate Trend EA + ARK EA over a shared execution-state
protocol) does not exist in any of these files yet.

## Headline finding

The legacy source is **five unrelated strategy families**, not five versions of one system. Only
Family A is a Trend+ARK gold system, and it is monolithic — the exact shape §7 says not to return to.

| Family | Files | Relation to target architecture |
|---|---|---|
| A. GOLD dual-engine 5.2→6.6 | 15 | Closest ancestor. Monolithic Trend+ARK in one EA. Must be **split**, not extended. |
| B. ARK 7.1 standalone | 2 | Multi-asset scanner. ARK signal function is an empty stub. |
| C. Candle Revisit / Master Brain | 17 | Different strategy entirely (level revisit + straddle recovery). Not Trend, not ARK. |
| D. ARK + Jobbing backtest v3.00 | 6 | Named in spec §6/§34 as legacy-only. Opening-range strategy, unrelated to spec's ARK. |
| E. Observer Network | 2 | Non-trading risk/DD monitor. Reusable concept for `monitoring/`. |

## Family A — GOLD dual-engine (`legacy/gold-dual-engine-5.x-6.x/`)

Lineage 5.2 → 6.6, dated 2026-08-13. Two structural generations:

- **5.2 – 6.3** (~140–155 KB each): multi-symbol scanner heritage, carries NeoFL 4.3 "segregated
  capital" preamble. Scans M1/M5/M15/M30/H1/H4 and ranks markets. Large and accreted.
- **6.4 – 6.6** (~25–31 KB): deliberate rewrite. Header states the intraday-first architecture —
  Trend on M5 + synthetic M15 + actual M15 + M30 survival, M1 liquidity-sweep entry/trailing, ARK as
  an independent M15 event engine. Separate magic numbers (`InpMagicTrend=64001`, `InpMagicARK=64002`).

**`NeoFL_GOLD_6.6_ARK_PREEXECUTION_LOCK.mq5` is the most relevant legacy file in the entire inventory.**
Spec §12 (ARK reserves the execution slot *before* sending the order) is a direct description of what
6.6 was built to solve. It is the primary reference for the new ARK EA's locking behavior.

Caveat: 6.5 and 6.6 have stale internal version strings (`#property version "6.40"`, descriptions
still reading 6.4/6.5). Filenames are the reliable ordering, not the embedded metadata.

## Family B — ARK 7.1 standalone (`legacy/ark-7.1-standalone/`)

`NeoFL_ARK_7_1_MT5.mq5` and a `_CTrade` variant. ~11 KB. Multi-asset
(`BTCUSD,XAUUSD,NAS100,US30,GER40,ETHUSD`), M1 execution with re-entry.

The header says it plainly: the proprietary ARK rules are meant to be inserted into `ARKSignal()`.
**The actual ARK mathematics are not in this file.** It is a harness, not a strategy. This is the
single largest specification gap — see Open Questions.

Note the multi-asset default symbol list directly conflicts with spec §14 (gold only, never
BTCXAU-style synthetics). Do not carry that input list forward.

## Family C — Candle Revisit / Master Brain (`legacy/candle-revisit-master-brain/`)

The longest lineage (v1.00 → v3.85, 2026-08-13→16) and the most actively developed, but it implements
a **different strategy than the master spec describes**: M5 candle-level classification and revisit,
with opposite-entry recovery and — by v3.80+ — a straddle/basket recovery system.

Evolution: standalone concept → M1-within-M5 entries → monitor-only → opposite recovery → "institutional"
(risk governor, MT5 calendar, 0.01 lot cap, Observer Core include) → v3.85 backtest package with
`NeoFL_MasterBrain_v3_85.mqh` as a decision-only engine plus straddle/basket P&L authority.

Architectural rule carried in these headers since v3.66 — worth noting because it *contradicts* spec §9:

> M5 is the ONLY initial-entry engine. M1 has NO initial-entry pathway. M1 is strictly an
> existing-trade monitor/protection/reassessment engine.

Spec §9 gives M1 an entry-confirmation role. See Open Questions.

Genuinely reusable ideas here: decision/execution separation (`MasterBrain` decides, `CTrade` alone
executes) matches spec §21/§25; the hard lot ceiling and account risk governor match §30.

`v3.85_BACKTEST_READY_PACKAGE/` is the extracted zip, kept intact with its README and presets.

## Family D — ARK + Jobbing backtest v3.00 (`legacy/ark-jobbing-backtest-v3.00/`)

The file spec §34 calls out by name: `NeoFL_ARK_Backtest_v3_00.mq5`. Small (~3.7 KB each), with
`.set` presets and a README. Two independent Strategy Tester EAs:

- ARK: US 09:30–16:00 ET with DST, first M15 candle as opening range, first M5 close outside it sets
  direction, M5 EMA/RSI confirmation, persistent position with reversal on opposite breakout.
- Jobbing: tick-driven M1 micro-context, 60-second max hold, cooldown after timeout.

**This "ARK" is an opening-range breakout strategy. It shares only a name with the liquidity/SMC event
engine in spec §10.** This is precisely the confusion §34 warns against — flagged here so no future
agent mistakes it for the target ARK.

## Family E — Observer Network (`legacy/observer-network/`)

`NeoFL_Observer_Network_v1_20_Institutional.mq5` + `NeoFL_Observer_Core.mqh`. A script that never
trades: M1 observation, drawdown, realized P&L, win/loss probability, safe-withdrawal monitoring,
published via MT5 global variables.

The "observe and publish, never execute" split is a good precedent for `monitoring/` (§27) and for
the Data Bridge's non-decision-making constraint (§21).

## Duplicates

Byte-identical copies were dropped (browser `(1)`/`(2)` re-downloads): three copies of
Candle Revisit v3.67, three of v3.80 Institutional, three of `M1WithinM5_v3_31`, two of
`StopAndReverse_EA`. Originals are untouched in `~/Downloads` if any need recovery.

`StopAndReverse_EA.mq5` and the `Candle_Level_Revisit_*` files predating the NeoFL prefix are kept for
lineage. Note: `StopAndReverse_EA` was independently reimplemented in the unrelated Neokart repo at
`~/Documents/New project/mt5_stop_reverse_ea/` — not part of NeoFL.

## Not found

Spec §6 lists builds that are **not present on this machine**:

- NeoFL GOLD 7.0 Trend Engine
- NeoFL GOLD 7.0 ARK Engine
- NeoFL Indices / BTC / FX source

7.0 matters: §6 implies the Trend/ARK split was already attempted there. If those files exist in a
prior chat session or another machine, they supersede 6.6 as the primary reference and should be
recovered before Phase 3 starts.

## Classification against spec §34

| Requested label | Files |
|---|---|
| current | none — no file implements the target architecture |
| legacy | all 42 |
| backtest | Family D; Family C v3.85 package |
| Trend | Family A only (embedded, not separable as-is) |
| ARK | Family A (embedded), Family B (stub), Family D (different strategy, name collision) |
| Indices / BTC / FX | none, except Family B's multi-asset input list |

## Open questions for the product owner

These block Phase 2. None can be answered by reading code.

1. **What are the actual ARK rules?** `ARKSignal()` is empty in 7.1; Family D's ARK is opening-range;
   spec §10 describes liquidity sweeps/BOS/CHOCH/SMC/supply-demand. The real mathematics exist only
   with you. This is the critical path item.
2. **Do the GOLD 7.0 builds exist?** If yes, recover them — they likely already did the split.
3. **M1's role — spec §9 or Family C's rule?** §9 has M1 confirming entries; Family C forbids M1
   initial entry outright. Direct contradiction; §9 is assumed authoritative pending your call.
4. **Does the straddle/basket recovery system carry forward?** It is the most-developed legacy
   machinery but appears nowhere in the master spec.
5. **Which broker/symbol is authoritative for the demo account?** Needed for the §14 symbol map.
