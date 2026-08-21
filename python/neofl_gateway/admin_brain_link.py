"""Admin Dock <-> Brain link.

The Admin Dock is the authoritative control plane. Brain never connects directly
to provider infrastructure. This link is the single controlled interface through
which Admin delivers authorized inputs and receives Brain outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from .control_plane import ChannelDirection, ControlPlane


class BrainEngine(Protocol):
    def ingest(self, payload: Mapping[str, object]) -> object: ...


@dataclass(frozen=True)
class BrainLinkResult:
    channel_id: str
    output: object


class AdminBrainLink:
    """Authorizes Admin channels before handing data to the Brain engine."""

    def __init__(self, control_plane: ControlPlane, brain: BrainEngine) -> None:
        self._control_plane = control_plane
        self._brain = brain

    def deliver_input(self, channel_id: str, payload: Mapping[str, object]) -> BrainLinkResult:
        authorized = self._control_plane.brain_input(channel_id, payload)
        output = self._brain.ingest(authorized["payload"])
        return BrainLinkResult(channel_id=channel_id, output=output)

    def authorize_output(self, channel_id: str, payload: Mapping[str, object]) -> dict[str, object]:
        # Output remains under Admin routing; this does not grant execution authority.
        return self._control_plane.brain_output(channel_id, payload)

    def can_receive(self, channel_id: str) -> bool:
        try:
            self._control_plane.authorize(channel_id, ChannelDirection.INPUT)
            return True
        except Exception:
            return False
