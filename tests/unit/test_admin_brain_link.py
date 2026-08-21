from __future__ import annotations

import pytest

from neofl_gateway.admin_brain_link import AdminBrainLink
from neofl_gateway.control_plane import (
    Channel,
    ChannelDirection,
    Connection,
    ConnectionStatus,
    ControlPlane,
)


class FakeBrain:
    def __init__(self) -> None:
        self.received = []

    def ingest(self, payload):
        self.received.append(dict(payload))
        return {"accepted": True}


def test_admin_delivers_authorized_input_to_brain() -> None:
    cp = ControlPlane()
    cp.register_connection(Connection("nse", "nseindia", ConnectionStatus.ENABLED, capabilities=frozenset({"market.read"})))
    cp.register_channel(Channel("nse.market", "nse", ChannelDirection.INPUT, "market.read"))
    brain = FakeBrain()
    link = AdminBrainLink(cp, brain)

    result = link.deliver_input("nse.market", {"symbol": "NIFTY"})
    assert result.output == {"accepted": True}
    assert brain.received == [{"symbol": "NIFTY"}]


def test_admin_link_denies_unauthorized_input_before_brain() -> None:
    cp = ControlPlane()
    cp.register_connection(Connection("nse", "nseindia", ConnectionStatus.ENABLED, capabilities=frozenset()))
    brain = FakeBrain()
    link = AdminBrainLink(cp, brain)

    with pytest.raises(Exception):
        link.deliver_input("nse.market", {"symbol": "NIFTY"})
    assert brain.received == []


def test_admin_link_does_not_turn_brain_output_into_execution_authority() -> None:
    cp = ControlPlane()
    cp.register_connection(Connection("mt5", "mt5", ConnectionStatus.ENABLED, capabilities=frozenset({"output.route"})))
    cp.register_channel(Channel("mt5.output", "mt5", ChannelDirection.OUTPUT, "output.route"))
    link = AdminBrainLink(cp, FakeBrain())

    routed = link.authorize_output("mt5.output", {"decision": "BUY"})
    assert routed["provider"] == "mt5"
    assert routed["payload"]["decision"] == "BUY"
