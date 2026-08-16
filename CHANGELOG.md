# Changelog

## 2026-08-16 — Phase 1: repository foundation

Initial NeoFL repository. No trading code; scaffolding, preservation, and documentation only.

### Added
- Repository structure per master spec section 5.
- `docs/product/MASTER_SPEC_v1.0.md` — master specification, captured verbatim as product source of truth.
- `docs/architecture/SOURCE_INVENTORY.md` — audit of all 42 legacy `.mq5`/`.mqh` files.
- `docs/architecture/ARCHITECTURE.md` — system shape and hard boundaries.
- `docs/ai/DEVELOPMENT_WORKFLOW.md`, `CLAUDE.md` — AI development instructions.
- `tests/` framework with structural and legacy-preservation guards.
- `.gitignore` covering secrets, market data, and MQL5 build output.

### Preserved
- 42 legacy source files copied into `legacy/`, deduplicated and classified into five families.
  Originals untouched in `~/Downloads`. Byte-identical browser re-downloads dropped.

### Findings
- Legacy source is five unrelated strategy families, not one lineage.
- No existing file implements the target architecture (separate Trend EA + ARK EA).
- `NeoFL_GOLD_6.6_ARK_PREEXECUTION_LOCK.mq5` is the closest ancestor of the spec's ARK lock.
- `NeoFL_ARK_Backtest_v3_00.mq5` is an opening-range strategy sharing only a name with spec ARK.
- GOLD 7.0 Trend/ARK builds referenced in spec section 6 are not present on this machine.

### Blocked
- Phase 2 requires the ARK detection rules from the product owner. `ARKSignal()` is an empty stub in
  legacy 7.1 and the mathematics appear in no file or document here.

Trading-behavior change: no
