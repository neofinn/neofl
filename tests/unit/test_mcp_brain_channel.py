from __future__ import annotations

import pytest

from neofl_gateway.channel_registry import (
    Channel,
    ChannelAuthority,
    ChannelDirection,
    ChannelRegistry,
)
from neofl_gateway.mcp_brain_channel import MCPBrainChannel, MCPBrainPolicy


def test_mcp_direct_channel_accepts_authorized_feed() -> None:
    channel = MCPBrainChannel(MCPBrainPolicy(allowed_capabilities=frozenset({"market.read"})))
    result = channel.feed("market.read", {"symbol": "NIFTY"})
    assert result["channel"] == "mcp.brain.input"
    assert result["source"] == "mcp"


def test_mcp_direct_channel_rejects_unauthorized_capability() -> None:
    channel = MCPBrainChannel(MCPBrainPolicy(allowed_capabilities=frozenset({"market.read"})))
    with pytest.raises(PermissionError):
        channel.feed("orders.execute", {})


def test_mcp_direct_channel_can_be_disabled_by_admin() -> None:
    channel = MCPBrainChannel(MCPBrainPolicy(enabled=False))
    with pytest.raises(PermissionError):
        channel.feed("market.read", {})


def test_registry_only_allows_mcp_direct_brain_as_input() -> None:
    registry = ChannelRegistry()
    registry.register(
        Channel(
            name="mcp.brain.input",
            direction=ChannelDirection.INPUT,
            connection="mcp",
            authority=ChannelAuthority.MCP_DIRECT_BRAIN,
            receive=lambda: {},
        )
    )

    with pytest.raises(ValueError):
        registry.register(
            Channel(
                name="bad.direct",
                direction=ChannelDirection.INPUT,
                connection="nseindia",
                authority=ChannelAuthority.MCP_DIRECT_BRAIN,
                receive=lambda: {},
            )
        )

    with pytest.raises(ValueError):
        registry.register(
            Channel(
                name="bad.mcp.output",
                direction=ChannelDirection.OUTPUT,
                connection="mcp",
                authority=ChannelAuthority.MCP_DIRECT_BRAIN,
                send=lambda _: None,
            )
        )
