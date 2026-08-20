# NeoFL Connection Architecture

The external brain is an engine. It does not own provider credentials and it does not
embed provider-specific secrets in strategy code.

## Boundary

```text
INPUT CONNECTIONS
  NSE / MT5 / TradingView / broker / calendar / user-provided API
          |
          v
  Connection Manager
  - resolves connection
  - supplies credential only when requested
  - reports configuration health without exposing values
          |
          v
  Input Channels -> Brain Engine -> Output Channels
                                      |
                                      +-> recommendation / telemetry / approved handoff
```

## Rules

- A connection owns endpoint configuration and a reference to credential environment variables.
- Secret values are never committed, serialized, or printed by the connection manager.
- Channels are directional: `input` or `output`.
- The Brain can consume many input channels and publish to many output channels.
- A connection may be replaced without changing brain/strategy logic.
- Provider credentials are supplied at runtime only when the adapter requests them.
- Missing or unavailable input must propagate as `DATA_UNAVAILABLE`; it must never be replaced by a guess.
- Output channels do not grant trading authority. MQL5 remains the execution authority under D-001.
- User-provided credentials remain scoped to that user's connection; they are not canonicalized into shared data.

## NSE India

The initial connection is `nseindia`, backed by the `imcodeman/nseindia` Docker service on port `3001`.
The endpoint is configurable with `NEOFL_NSE_ENDPOINT`; the default inside the Docker network is
`http://nseindia:3001`.

Endpoint-specific NSE ingestion should be added only after the container is actually running and
its routes are verified. This layer deliberately does not invent API responses or credentials.
