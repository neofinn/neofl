# NSE India input service

This directory defines how NeoFL can run the public `imcodeman/nseindia` container as an external market-data input service.

The service is intentionally isolated from MQL5 execution code. It is a **data source adapter only**.

## Container

Image:

```text
imcodeman/nseindia
```

Port:

```text
3001
```

Start locally:

```bash
docker compose -f python/nseindia/docker-compose.yml up -d
```

Stop:

```bash
docker compose -f python/nseindia/docker-compose.yml down
```

## Integration boundary

```text
NSE India container
      -> HTTP :3001
      -> Python/data adapter
      -> validation + normalization
      -> NeoFL external-data stream
      -> analysis / agentic brain

MQL5 execution remains the only order authority.
```

Do not put API keys, broker credentials, account credentials, or other secrets in this directory or in Compose files committed to Git.

## Important

The container image and its available HTTP routes are treated as an external dependency. Do not invent endpoint paths. Integration code must validate the actual response and emit `DATA_UNAVAILABLE` on connection, parsing, or schema failure rather than fabricating market values.
