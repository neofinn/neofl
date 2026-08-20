import unittest

from python.neofl_gateway.control_plane import (
    Channel,
    ChannelDirection,
    Connection,
    ConnectionStatus,
    ControlPlane,
    ControlPlaneError,
)
from python.neofl_gateway.mcp_gateway import MCPGateway, MCPRequest


class ControlPlaneTests(unittest.TestCase):
    def setUp(self):
        self.cp = ControlPlane()
        self.cp.register_connection(
            Connection(
                "nse",
                "nseindia",
                ConnectionStatus.ENABLED,
                secret_ref=None,
                capabilities=frozenset({"market.read"}),
            )
        )
        self.cp.register_channel(Channel("nse-input", "nse", ChannelDirection.INPUT, "market.read"))

    def test_brain_receives_only_registered_input_channel(self):
        result = self.cp.brain_input("nse-input", {"symbol": "NIFTY 50"})
        self.assertEqual(result["provider"], "nseindia")
        self.assertEqual(result["payload"]["symbol"], "NIFTY 50")

    def test_unregistered_route_is_denied(self):
        with self.assertRaises(ControlPlaneError):
            self.cp.brain_input("direct-to-brain", {"price": 1})

    def test_disabled_connection_is_denied(self):
        self.cp2 = ControlPlane()
        self.cp2.register_connection(Connection("x", "provider", ConnectionStatus.DISABLED, capabilities=frozenset({"read"})))
        with self.assertRaises(ControlPlaneError):
            self.cp2.register_channel(Channel("x-in", "x", ChannelDirection.INPUT, "read"))

    def test_mcp_requires_mcp_capability(self):
        cp = ControlPlane()
        cp.register_connection(Connection("mcp", "provider", ConnectionStatus.ENABLED, capabilities=frozenset({"mcp.tool"})))
        cp.register_channel(Channel("mcp-in", "mcp", ChannelDirection.INPUT, "mcp.tool"))
        gateway = MCPGateway(cp)
        result = gateway.authorize_tool(MCPRequest("s1", "mcp-in", "market_status", {}))
        self.assertEqual(result["tool"], "market_status")

    def test_mcp_cannot_use_market_channel(self):
        with self.assertRaises(ControlPlaneError):
            MCPGateway(self.cp).authorize_tool(MCPRequest("s1", "nse-input", "market_status", {}))


if __name__ == "__main__":
    unittest.main()
