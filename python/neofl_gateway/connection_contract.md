# NeoFL Connection Architecture

The Brain is an engine. External provider connections are controlled by the Admin Dock.
MCP is the intentional exception: it is a Brain data feeder and therefore has a direct,
scoped Brain-facing channel. Admin still owns MCP authorization and connection policy.

## Canonical wiring

```text
NSE / MT5 / TradingView / broker / calendar / user API
                    |
                    v
               ADMIN DOCK
          control plane / keys / policy
                    |
                    v
              INPUT CHANNELS
                    |
                    v
                BRAIN ENGINE
                    |
                    v
              OUTPUT CHANNELS
                    |
                    v
               ADMIN DOCK
              output routing

MCP DOCK
   |
   | direct Brain data-feed channel
   v
BRAIN ENGINE
```

## Rules

- External non-MCP connections never connect directly to Brain.
- Admin Dock owns connection registration, credential references, permissions, enable/disable,
  routing, and health state for external connections.
- MCP is a privileged Brain data-feeder path. It has a direct Brain-facing channel so MCP tools,
  resources, and data can feed the engine without an unnecessary Admin routing hop.
- MCP does not bypass Admin authorization: Admin controls which MCP server, session, tool, resource,
  and capability may use the direct Brain channel.
- The direct MCP channel is input/data/tool-feed only. It does not grant unrestricted output or
  trading authority.
- Brain never stores provider secrets. Secrets remain scoped to their connection and are supplied
  at runtime by the connection/control layer.
- Channels are directional: `input` or `output`.
- Missing or unavailable input must propagate as `DATA_UNAVAILABLE`; it must never be replaced by a guess.
- Brain output is routed through Admin Dock before reaching external destinations.
- MQL5 remains the execution authority under D-001.

## NSE India

The initial external connection is `nseindia`, backed by the `imcodeman/nseindia` Docker service on
port `3001`. It follows the Admin-controlled path: NSE -> Admin Dock -> Input Channel -> Brain.

Endpoint-specific NSE ingestion must only be added after the container is actually running and its
routes are verified.

## MCP Brain channel

The canonical direct channel name is `mcp.brain.input`. The channel accepts normalized, authorized
MCP data/tool results and rejects unscoped MCP capabilities. The Admin Dock supplies the authorization
policy; the Brain consumes the resulting normalized feed.
