# Changelog

## 2026-08-20 — Admin and MCP control plane

### Added
- `docs/architecture/CONTROL_PLANE.md` — hard boundary between external connections, Admin Control Plane, MCP Dock, and Brain.
- `python/neofl_gateway/control_plane.py` — connection/channel authorization policy with scoped secret references and no raw credential storage.
- `python/neofl_gateway/mcp_gateway.py` — MCP Dock gateway that requires an Admin-authorized channel before presenting a tool request to the Brain interface.
- `tests/unit/test_control_plane.py` — isolation, disabled-connection, and MCP capability tests.

### Architecture rule
- External systems do not connect directly to Brain.
- Admin Control Plane is authoritative for connections, permissions, routing, and secret references.
- MCP Dock is separate from Admin UI but remains policy-mediated; its logical Brain interface is not an uncontrolled infrastructure path.
- Brain receives normalized authorized channel payloads only.
- No trading logic or execution authority is added.

Trading-behavior change: no.

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
