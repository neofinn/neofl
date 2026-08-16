# Changelog

## 2026-08-16 (build step 3) — Market Data, Session, Data Quality; rooms; packaging tool

### Added — Core
- `CORE/NeoFL_DataValidation/NeoFL_DataQuality.mqh` — the five data-quality states and the
  `NeoFLDecision` provenance record every engine emits (D-002). Verdicts distinguish DECLINE
  (evaluated, conditions not met — normal) from BLOCKED (could not evaluate) and ERROR.
- `CORE/NeoFL_MarketData/NeoFL_MarketData.mqh` — bars and quotes that report quality instead of
  assuming it. Refuses shift=0 (the forming bar), validates OHLC consistency, reports INCOMPLETE
  rather than silently returning fewer bars, and assesses tick staleness against a freshness budget.
- `CORE/NeoFL_Session/NeoFL_Session.mqh` — US session timing derived from GMT with DST computed,
  never from broker server time. Opening range = the first M15 candle (09:45 ET), per canon.
- `CORE/NeoFL_MarketData/NeoFL_CoreSelfTest.mq5` — MT5 Script, places no orders, exercises all three
  against the live broker.
- `python/neofl_core/session.py` + `tests/unit/test_session.py` — DST and session-window mirror.

### Added — tooling
- `tools/mql5_package.sh` — builds a self-contained deployment package per the canon's hard
  single-folder rule: walks the include graph from an entry `.mq5`, copies every dependency flat,
  rewrites include paths, detects basename collisions, then compiles to prove it deploys.
- `tools/mql5_compile.sh` now stages the parent tree when cross-directory `../` includes are present,
  so CORE modules compile in place during development.

### Added — workspace
- Per-strategy `CLAUDE.md` in all seven `STRATEGIES/*` directories, so a session opened in a
  strategy room arrives knowing that strategy's rules, ancestors and traps.
- `docs/ai/ROOMS.md` — which room owns what. Shared code changes in the infrastructure room only.

### Verified
- MQL5 compile: 0 errors, 0 warnings, both self-tests packaged and deployed.
- Python suite: 38 tests pass.
- DST boundaries asserted against the real calendar for 2024–2027, not recomputed by the logic
  under test.
- NOT verified: behavior against live broker data — needs a human to run the script in MT5.

Trading-behavior change: no (data access, timing, and observability only; no entry/exit/risk rule)

## 2026-08-16 (later still) — first Core module: Symbol Resolver

First NeoFL source code. Build step 2 of the canon order (Symbol / Instrument Resolver).

### Added
- `CORE/NeoFL_SymbolResolver/NeoFL_SymbolResolver.mqh` — resolves a broker symbol to an
  `NeoFLInstrument` descriptor. Semantic base-symbol matching, not substring: XAU counts as gold
  only when it is the BASE, i.e. immediately followed by a recognized quote currency. This is what
  makes `BTCXAU` reject (XAU there is the quote of a crypto cross) while `PREFIX_XAUUSD_SUFFIX`
  resolves.
- `CORE/NeoFL_SymbolResolver/NeoFL_SymbolResolver_SelfTest.mq5` — MT5 Script, places no orders,
  prints PASS/FAIL for every canon case. Deployed to `MQL5/Scripts/NeoFL/`.
- `python/neofl_core/symbol_resolver.py` — reference mirror of the same rules, so the logic is
  testable in milliseconds rather than only inside MetaTrader.
- `tests/unit/test_symbol_resolver.py` — 11 tests covering valid variants, rejections, normalization,
  and mirror consistency with the MQL5 module.

### Fixed
- The repository's gold-only guard flagged the resolver itself, since the resolver must name
  `BTCXAU`/`ETHXAU` to reject them. Exempted the resolver in both languages as the designated
  rejection authority; its own tests assert the rejection behavior.

### Verified
- MQL5 compile: 0 errors, 0 warnings.
- Python suite: 26 tests pass.
- Logic checked case by case; `BTCXAU`, `ETHXAU`, `BTCXAU.pro` all correctly rejected.
- NOT verified: runtime behavior in MT5 against a live broker symbol. The self-test's live-resolve
  section needs a human to run it on a chart.

Trading-behavior change: no (no entry, exit, filter, or risk rule; classification only)

## 2026-08-16 (later) — v2 canon: platform architecture supersedes v1.0

The product owner supplied a revised handoff defining NeoFL as a multi-strategy platform. This
supersedes the v1.0 gold/Trend+ARK specification. No trading code; canon, structure, and docs only.

### Added
- `docs/product/HANDOFF_DIRECTIVE.md` — canon governance; highest-authority document.
- `docs/product/MASTER_ARCHITECTURE_v2.md` — current architecture canon.
- `docs/product/ENGINE_OBSERVER_SCRIPTS_LAYER.md` — engine/observer/scripts layers.
- `docs/product/MASTER_UNIVERSE_CANON.md` — universe structure and whitepaper index.
- v2 directory structure: `CORE/` (19 engines), `STRATEGIES/` (7), `OBSERVER/`, `SCRIPTS/`,
  `DATA/`, `EXTERNAL_BRAIN/`, `BACKTEST/`, `DEPLOYMENTS/`, `python/`.

### Changed
- `MASTER_SPEC_v1.0.md` marked **SUPERSEDED** with a documented v1→v2 diff. Retained per the
  handoff directive's preserve-don't-delete rule.
- `ARCHITECTURE.md`, `CLAUDE.md`, `README.md` rewritten for the platform architecture.
- Tests updated: 12 checks covering core engines, per-strategy isolation, canon presence,
  supersession marking, and the gold-only instrument rule.

### Removed
- Empty v1-only scaffolding (`mt5/`, `external-data/`, `agentic-brain/`, `monitoring/`,
  `infrastructure/`, `backtesting/`). No files lost — all were empty.

### Architecture changes (v1.0 → v2)
- Gold-only platform → multi-asset platform; Gold is one of seven strategies.
- Trend EA + ARK EA → seven independent strategies over one shared Core Engine.
- **Trend Engine removed** from the architecture entirely.
- ARK redefined: gold liquidity/SMC engine → Liquid Flow aimed at indices, requiring external data.
- **Bucket Engine and Straddle Engine added as core** with explicit state machines.
- `ARK_STATE` cross-engine execution lock removed; strategies are independent.
- Build order: 12 phases starting at repo scaffolding → 17 phases starting at NeoFL Core.
- Hard packaging rule: every EA ships with its includes in one folder.

### Findings — legacy reclassified
- `NeoFL_ARK_Backtest_v3_00.mq5` is named ARK but **implements today's Jobbing** (US open, first M15
  candle as opening range, M5 breakout, EMA/RSI). Verified by reading the source. The name moved
  between strategies; the earlier "unrelated strategy" assessment was wrong.
- Its `RequireM5CHoCH` input is **declared and never referenced** — CHOCH is not implemented despite
  being required by the v2 Jobbing architecture. Must be built, not ported.
- `NeoFL_MasterBrain_v3_85.mqh` is the **ancestor of the v2 Straddle Engine** — the most valuable
  legacy asset. Legacy calls it "basket"; v2 calls it "bucket".
- `NeoFL_Observer_Core_v2_00.mqh` is present and is one of the two canon-confirmed latest observer
  components. Its companion `NeoFL_Observer_Network_v2_00.mq5` is **missing**.
- GOLD 5.x/6.x dual-engine line demoted: it implements a Trend Engine that no longer exists.

### Blocked
- ARK / Liquid Flow signal rules remain unspecified in every file and document. Blocks build step 10.
- Four of seven strategies (Price Action, FX, BTC, Indices) have no source at all.

Trading-behavior change: no

## 2026-08-16 — Phase 1: repository foundation

Initial NeoFL repository. No trading code; scaffolding, preservation, and documentation only.

### Added
- Repository structure, master specification, source inventory, architecture and AI docs.
- `tests/` framework with structural and legacy-preservation guards.
- `.gitignore` covering secrets, market data, and MQL5 build output.

### Preserved
- 42 legacy source files copied into `legacy/`, deduplicated and classified into five families.
  Originals untouched in `~/Downloads`.

Trading-behavior change: no
