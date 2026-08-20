"""MCP Dock boundary.

MCP sessions are mediated by the Admin-owned ControlPlane. This module deliberately does not store
or forward raw provider credentials to the Brain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .control_plane import ChannelDirection, ControlPlane, ControlPlaneError


@dataclass(frozen=True)
class MCPRequest:
    session_id: str
    channel_id: str
    tool: str
    arguments: Mapping[str, object]


class MCPGateway:
    def __init__(self, control_plane: ControlPlane) -> None:
        self.control_plane = control_plane

    def authorize_tool(self, request: MCPRequest) -> dict[str, object]:
        channel = self.control_plane.authorize(request.channel_id, ChannelDirection.INPUT)
        if channel.capability != "mcp.tool":
            raise ControlPlaneError("MCP tool capability denied")
        return {
            "session_id": request.session_id,
            "channel_id": channel.channel_id,
            "tool": request.tool,
            "arguments": dict(request.arguments),
        }

    def send_brain_output(self, channel_id: str, payload: Mapping[str, object]) -> dict[str, object]:
        return self.control_plane.brain_output(channel_id, payload)
