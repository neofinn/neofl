# NeoFL Control Plane

## Hard boundary

The Brain is an engine. It has no direct provider connections and never owns provider credentials.

All external systems terminate at the Admin Control Plane. The Admin Control Plane decides which
connections exist, which channels are enabled, what data may enter the Brain, and where Brain output
may leave.

```text
External systems
  -> Admin Control Plane
  -> authorized input channels
  -> Brain Engine
  -> authorized output channels
  -> Admin Control Plane
  -> external systems
```

## Admin Dock

The Admin Dock is the authoritative control surface for the NeoFL universe.

Responsibilities:
- create, disable, rotate, and remove connections
- hold secret references; never expose raw credentials to Brain
- assign input/output channels
- enforce permissions and tenant/user scope
- configure routing, limits, and health policy
- audit connection and routing changes
- block disabled or unauthorized connections

## MCP Dock

The MCP Dock is a separate MCP-specific control surface. It manages MCP servers, tools, resources,
and sessions, but it does not bypass Admin policy.

```text
MCP Dock
  -> MCP Gateway / Policy
  -> authorized Brain interface
```

The MCP Dock may provide a logical Brain interface, but it must not create an uncontrolled network path
or inject provider credentials into Brain.

## Connection lifecycle

1. Admin creates a connection definition.
2. Secret material is stored outside Git and outside Brain state.
3. Admin assigns capabilities and channels.
4. The adapter requests credentials only at execution time.
5. Connection Manager supplies the scoped secret to the adapter.
6. Adapter emits normalized channel data.
7. Brain receives only the normalized authorized payload.
8. Brain output returns through the controlled channel/router.
9. Admin policy decides whether the output may reach its destination.

## Failure policy

- Missing secret: `CONNECTION_UNAVAILABLE`.
- Disabled connection: `CONNECTION_DISABLED`.
- Unauthorized route: `ROUTE_DENIED`.
- Provider failure: `DATA_UNAVAILABLE` for inputs.
- Invalid provider payload: `DATA_INVALID`.
- Never fabricate missing market/account data.
- A connection failure must never silently grant a fallback direct path to Brain.

## Execution authority

The control plane is infrastructure, not trading logic. It does not invent entry, exit, risk, or strategy
rules. MQL5 remains the only execution authority under the existing NeoFL architecture.
