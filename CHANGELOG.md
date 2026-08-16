# Changelog

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
