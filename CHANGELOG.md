# Changelog

## 2026-08-20 — NSE India Docker input service

### Added
- `python/nseindia/docker-compose.yml` — reproducible local/server container definition for `imcodeman/nseindia`, exposing port `3001`.
- `python/nseindia/README.md` — data-only integration boundary, startup commands, and safety rules.

### Design constraints
- NSE service is an external data source only; it does not receive order authority.
- Secrets remain outside Git and Compose configuration.
- Actual HTTP routes/schema must be discovered from the running image before an endpoint-specific adapter is implemented.
- Connection, parsing, or schema failures must produce `DATA_UNAVAILABLE`, never fabricated market values.

Trading-behavior change: no.

## 2026-08-16 (build step 6) — Bucket engine

A bucket is a portfolio of related positions, not one position. In this architecture the
basket mechanism **is** the risk control — the legacy analysis confirmed there are no broker
stops behind it — so bucket integrity is treated as a safety property.

### Added
- `python/neofl_core/bucket.py` — bucket composition, aggregate P/L, signed and gross
  exposure, state machine, and the zero-floating-price calculation.
- `tests/unit/test_bucket.py` — 15 tests including the delta-neutral trap.
