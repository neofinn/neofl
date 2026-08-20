# Changelog

## 2026-08-20 — MCP direct Brain data-feed wiring

### Changed
- MCP is now the intentional direct Brain-facing data feeder.
- Added `mcp.brain.input` as the canonical scoped MCP -> Brain channel.
- Admin remains authoritative for MCP capability authorization, enable/disable state, credentials, and connection policy.
- Non-MCP external systems remain Admin-routed and cannot use the direct Brain authority.
- MCP direct channel is input-only and does not grant execution authority.

### Added
- `python/neofl_gateway/mcp_brain_channel.py` — scoped MCP -> Brain feed.
- `tests/unit/test_mcp_brain_channel.py` — direct-feed authorization and channel-isolation tests.
- Updated `python/neofl_gateway/channel_registry.py` and `python/neofl_gateway/connection_contract.md` to enforce/document the wiring.

Trading-behavior change: no.

## 2026-08-20 — Admin and MCP control plane

### Added
- `docs/architecture/CONTROL_PLANE.md` — hard boundary between external connections, Admin Control Plane, MCP Dock, and Brain.
- `python/neofl_gateway/control_plane.py` — connection/channel authorization policy with scoped secret references and no raw credential storage.
- `python/neofl_gateway/mcp_gateway.py` — MCP Dock gateway that requires an Admin-authorized channel before presenting a tool request to the Brain interface.
- `tests/unit/test_control_plane.py` — isolation, disabled-connection, and MCP capability tests.

### Architecture rule
- External systems do not connect directly to Brain.
- Admin Control Plane is authoritative for connections, permissions, routing, and secret references.
- MCP Dock is separate from Admin UI and has a direct, scoped Brain data-feed channel.
- Brain receives normalized authorized channel payloads only.
- No trading logic or execution authority is added.

Trading-behavior change: no.

## 2026-08-20 — NSE India Docker input service

### Added
- `python/nseindia/docker-compose.yml` — reproducible local/server container definition for `imcodeman/nseindia`, exposing port `3001`.
- `python/nseindia/README.md` — data-only integration boundary, startup commands, and safety rules.
