"""Typed channel boundary between NeoFL infrastructure and the Brain.

MCP is the intentional direct Brain data-feeder path. The direct path is still
scoped by Admin policy before a channel is registered.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class ChannelDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ChannelAuthority(str, Enum):
    ADMIN_ROUTED = "admin_routed"
    MCP_DIRECT_BRAIN = "mcp_direct_brain"


@dataclass(frozen=True)
class Channel:
    name: str
    direction: ChannelDirection
    connection: str
    authority: ChannelAuthority = ChannelAuthority.ADMIN_ROUTED
    send: Callable[[Any], Any] | None = None
    receive: Callable[[], Any] | None = None


class ChannelRegistry:
    """Keeps Brain I/O boundaries explicit and independently replaceable."""

    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}

    def register(self, channel: Channel) -> None:
        if channel.name in self._channels:
            raise ValueError(f"channel already registered: {channel.name}")
        if channel.direction is ChannelDirection.INPUT and channel.receive is None:
            raise ValueError("input channel requires receive")
        if channel.direction is ChannelDirection.OUTPUT and channel.send is None:
            raise ValueError("output channel requires send")
        if channel.authority is ChannelAuthority.MCP_DIRECT_BRAIN:
            if channel.connection != "mcp":
                raise ValueError("direct Brain authority is reserved for MCP")
            if channel.direction is not ChannelDirection.INPUT:
                raise ValueError("MCP direct Brain channel is input-only")
        self._channels[channel.name] = channel

    def get(self, name: str) -> Channel:
        return self._channels[name]

    def describe(self) -> list[dict[str, str]]:
        return [
            {
                "name": c.name,
                "direction": c.direction.value,
                "connection": c.connection,
                "authority": c.authority.value,
            }
            for c in self._channels.values()
        ]
