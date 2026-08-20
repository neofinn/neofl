"""Typed channel boundary between the NeoFL brain and external systems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class ChannelDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass(frozen=True)
class Channel:
    name: str
    direction: ChannelDirection
    connection: str
    send: Callable[[Any], Any] | None = None
    receive: Callable[[], Any] | None = None


class ChannelRegistry:
    """Keeps the brain's I/O boundary explicit and independently replaceable."""

    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}

    def register(self, channel: Channel) -> None:
        if channel.name in self._channels:
            raise ValueError(f"channel already registered: {channel.name}")
        if channel.direction is ChannelDirection.INPUT and channel.receive is None:
            raise ValueError("input channel requires receive")
        if channel.direction is ChannelDirection.OUTPUT and channel.send is None:
            raise ValueError("output channel requires send")
        self._channels[channel.name] = channel

    def get(self, name: str) -> Channel:
        return self._channels[name]

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": c.name, "direction": c.direction.value, "connection": c.connection}
            for c in self._channels.values()
        ]
