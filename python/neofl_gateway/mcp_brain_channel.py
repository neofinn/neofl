"""Direct, scoped MCP -> Brain data-feeder channel.

Admin remains the authority: only capabilities explicitly authorized by the
Admin policy can enter this channel. This module does not store MCP secrets and
never grants execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class MCPBrainPolicy:
    enabled: bool = True
    allowed_capabilities: frozenset[str] = frozenset()


class MCPBrainChannel:
    """Normalize and authorize MCP data before delivering it to Brain."""

    name = "mcp.brain.input"

    def __init__(self, policy: MCPBrainPolicy) -> None:
        self._policy = policy

    def feed(self, capability: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not self._policy.enabled:
            raise PermissionError("MCP direct Brain channel disabled by Admin")
        if capability not in self._policy.allowed_capabilities:
            raise PermissionError(f"MCP capability not authorized: {capability}")
        return {
            "channel": self.name,
            "source": "mcp",
            "capability": capability,
            "payload": dict(payload),
        }
