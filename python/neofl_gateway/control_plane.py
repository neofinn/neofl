"""Control-plane policy for NeoFL connections and Brain channels.

This module deliberately contains no provider credentials and no trading logic.  It models the
boundary between Admin/MCP infrastructure and the Brain engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class ChannelDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ConnectionStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Connection:
    connection_id: str
    provider: str
    status: ConnectionStatus
    secret_ref: str | None = None
    capabilities: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Channel:
    channel_id: str
    connection_id: str
    direction: ChannelDirection
    capability: str


class ControlPlaneError(RuntimeError):
    pass


class ControlPlane:
    """Admin-owned routing policy; Brain sees only authorized channel payloads."""

    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}
        self._channels: dict[str, Channel] = {}

    def register_connection(self, connection: Connection) -> None:
        if connection.connection_id in self._connections:
            raise ControlPlaneError("connection already exists")
        self._connections[connection.connection_id] = connection

    def register_channel(self, channel: Channel) -> None:
        connection = self._connections.get(channel.connection_id)
        if connection is None:
            raise ControlPlaneError("connection does not exist")
        if connection.status is ConnectionStatus.DISABLED:
            raise ControlPlaneError("connection is disabled")
        if channel.capability not in connection.capabilities:
            raise ControlPlaneError("channel capability is not authorized")
        if channel.channel_id in self._channels:
            raise ControlPlaneError("channel already exists")
        self._channels[channel.channel_id] = channel

    def authorize(self, channel_id: str, direction: ChannelDirection) -> Channel:
        channel = self._channels.get(channel_id)
        if channel is None or channel.direction is not direction:
            raise ControlPlaneError("route denied")
        connection = self._connections[channel.connection_id]
        if connection.status is not ConnectionStatus.ENABLED:
            raise ControlPlaneError("connection disabled")
        return channel

    def connection_secret_ref(self, channel_id: str, direction: ChannelDirection) -> str:
        channel = self.authorize(channel_id, direction)
        secret_ref = self._connections[channel.connection_id].secret_ref
        if not secret_ref:
            raise ControlPlaneError("connection unavailable")
        return secret_ref

    def brain_input(self, channel_id: str, payload: Mapping[str, object]) -> dict[str, object]:
        channel = self.authorize(channel_id, ChannelDirection.INPUT)
        return {"channel_id": channel.channel_id, "provider": self._connections[channel.connection_id].provider, "payload": dict(payload)}

    def brain_output(self, channel_id: str, payload: Mapping[str, object]) -> dict[str, object]:
        channel = self.authorize(channel_id, ChannelDirection.OUTPUT)
        return {"channel_id": channel.channel_id, "provider": self._connections[channel.connection_id].provider, "payload": dict(payload)}
