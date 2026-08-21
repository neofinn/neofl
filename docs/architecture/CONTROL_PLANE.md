# NeoFL Control Plane

## Hard boundary

The Brain is an engine. It has no direct provider connections and never owns provider credentials.

The Admin Dock is the Brain's authoritative control-plane link. All non-MCP external systems terminate
at Admin, and Admin delivers only authorized normalized inputs to Brain. Brain outputs return to Admin
for routing. MCP is the intentional exception: MCP is a Brain data feeder and has a direct, scoped
Brain-facing input channel, while Admin still controls MCP authorization and capabilities.

```text
NSE / MT5 / APIs / other external systems
              |
              v
         ADMIN DOCK
     control / keys / policy
              |
       authorized inputs
              |
              v
          BRAIN ENGINE
              ^
              |
     DIRECT MCP DATA FEED
              |
          MCP DOCK
       (Admin-authorized)

Brain outputs
      |
      v
  ADMIN DOCK
      |
  authorized routing
      |
 external destinations
```

## Admin Dock

The Admin Dock is the authoritative control surface for the NeoFL universe **and the controlled link
to the Brain**.

Responsibilities:
- create, disable, rotate, and remove connections
- hold secret references; never expose raw credentials to Brain
- assign input/output channels
- enforce permissions and tenant/user scope
- deliver authorized normalized external inputs to Brain
- receive and route Brain outputs
- configure routing, limits, and health policy
- audit connection and routing changes
- block disabled or unauthorized connections

The Brain must not create an external connection on its own.

## Admin ↔ Brain link

`AdminBrainLink` is the single programmatic interface for Admin-to-Brain delivery and Brain-to-Admin
output authorization. It validates the channel through the Admin Control Plane before data reaches the
Brain engine. This makes the Admin Dock an actual connected control plane rather than documentation-only
wiring.

## MCP Dock

The MCP Dock is a separate MCP-specific control surface and data feeder. MCP has the intentional direct
Brain channel `mcp.brain.input` because MCP is an explicit Brain data/tool feeder.

Admin still controls:
- MCP server/session enablement
- allowed tools and resources
- capability authorization
- credential references
- channel policy

The MCP direct path is input/data-feed only. It does not grant unrestricted output or trading authority.

## Connection lifecycle

1. Admin creates a connection definition.
2. Secret material is stored outside Git and outside Brain state.
3. Admin assigns capabilities and channels.
4. The adapter requests credentials only at execution time.
5. Connection Manager supplies the scoped secret to the adapter.
6. Adapter emits normalized channel data.
7. Admin authorizes and delivers the data to Brain through `AdminBrainLink`.
8. MCP may feed Brain through `mcp.brain.input` when its capability is Admin-authorized.
9. Brain output returns to Admin through the controlled link.
10. Admin policy decides whether the output may reach its destination.

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
