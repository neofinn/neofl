"""Credential-safe connection registry for NeoFL input/output channels.

Secrets are never stored in the repository or returned in logs. A connection stores
only a reference to an environment variable containing the credential. Consumers
ask for a named connection and receive a short-lived credential mapping when needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ConnectionDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ConnectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ConnectionSpec:
    name: str
    direction: ConnectionDirection
    kind: str
    endpoint: str
    credential_env: tuple[str, ...] = ()
    enabled: bool = True


class ConnectionManager:
    """Resolve configured connections without persisting their secret values."""

    def __init__(self, specs: tuple[ConnectionSpec, ...] = ()) -> None:
        self._specs = {spec.name: spec for spec in specs}

    def register(self, spec: ConnectionSpec) -> None:
        if spec.name in self._specs:
            raise ConnectionError(f"connection already registered: {spec.name}")
        self._specs[spec.name] = spec

    def get(self, name: str, *, require_enabled: bool = True) -> ConnectionSpec:
        try:
            spec = self._specs[name]
        except KeyError as exc:
            raise ConnectionError(f"unknown connection: {name}") from exc
        if require_enabled and not spec.enabled:
            raise ConnectionError(f"connection disabled: {name}")
        return spec

    def credentials(self, name: str) -> Mapping[str, str]:
        """Return only credentials that are present in the process environment."""
        spec = self.get(name)
        missing = [key for key in spec.credential_env if not os.environ.get(key)]
        if missing:
            raise ConnectionError(
                f"credentials unavailable for {name}: {', '.join(missing)}"
            )
        return {key: os.environ[key] for key in spec.credential_env}

    def health(self, name: str) -> dict[str, object]:
        spec = self.get(name, require_enabled=False)
        return {
            "name": spec.name,
            "direction": spec.direction.value,
            "kind": spec.kind,
            "endpoint": spec.endpoint,
            "enabled": spec.enabled,
            "credentials_configured": all(
                bool(os.environ.get(key)) for key in spec.credential_env
            ),
        }

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))


def default_connections() -> ConnectionManager:
    """Canonical external connection registry for the first data boundary."""
    return ConnectionManager((
        ConnectionSpec(
            name="nseindia",
            direction=ConnectionDirection.INPUT,
            kind="docker-http",
            endpoint=os.getenv("NEOFL_NSE_ENDPOINT", "http://nseindia:3001"),
        ),
    ))
