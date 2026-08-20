import os
import unittest

from python.neofl_gateway.channel_registry import Channel, ChannelDirection, ChannelRegistry
from python.neofl_gateway.connections import ConnectionError, ConnectionManager, ConnectionSpec, default_connections


class ConnectionTests(unittest.TestCase):
    def test_nse_connection_defaults_to_docker_service(self):
        old = os.environ.pop("NEOFL_NSE_ENDPOINT", None)
        try:
            spec = default_connections().get("nseindia")
            self.assertEqual(spec.endpoint, "http://nseindia:3001")
            self.assertEqual(spec.direction.value, "input")
        finally:
            if old is not None:
                os.environ["NEOFL_NSE_ENDPOINT"] = old

    def test_credentials_are_runtime_only(self):
        os.environ["TEST_NEOFL_KEY"] = "secret-value"
        try:
            manager = ConnectionManager((ConnectionSpec(
                name="test", direction="input", kind="api", endpoint="https://example.test",
                credential_env=("TEST_NEOFL_KEY",),
            ),))
            self.assertEqual(manager.credentials("test")["TEST_NEOFL_KEY"], "secret-value")
            health = manager.health("test")
            self.assertNotIn("secret-value", str(health))
        finally:
            os.environ.pop("TEST_NEOFL_KEY", None)

    def test_missing_credentials_fail_closed(self):
        manager = ConnectionManager((ConnectionSpec(
            name="test", direction="input", kind="api", endpoint="https://example.test",
            credential_env=("MISSING_NEOFL_KEY",),
        ),))
        with self.assertRaises(ConnectionError):
            manager.credentials("test")

    def test_channel_direction_requires_matching_handler(self):
        registry = ChannelRegistry()
        with self.assertRaises(ValueError):
            registry.register(Channel("bad", ChannelDirection.INPUT, "test"))
        with self.assertRaises(ValueError):
            registry.register(Channel("bad", ChannelDirection.OUTPUT, "test"))


if __name__ == "__main__":
    unittest.main()
