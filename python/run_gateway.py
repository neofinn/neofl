#!/usr/bin/env python3
"""Start the NeoFL gateway.

    python3 python/run_gateway.py [--port 8787] [--token SECRET]

Prints the webhook URLs and their signing secrets on startup. Those secrets are
credentials: configure them in the sending provider, and never commit them.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from neofl_gateway.api import StateStore, build_default_api
from neofl_gateway.normalizers import normalize_cme, normalize_tradingview
from neofl_gateway.server import make_server
from neofl_gateway.webhooks import WebhookRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description="NeoFL data gateway")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--token", default=None,
                        help="bearer token for the read API; omit to disable auth (local only)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    store = StateStore()
    api = build_default_api(store, token=args.token)

    webhooks = WebhookRegistry()
    tv = webhooks.create("tradingview", normalize_tradingview)
    cme = webhooks.create("cme", normalize_cme)

    base = f"http://{args.host}:{args.port}"
    print("=" * 68)
    print("  NeoFL Gateway")
    print("=" * 68)
    print(f"  read API      {base}/")
    print(f"  auth          {'Bearer token required' if args.token else 'DISABLED (local only)'}")
    print()
    print("  Webhooks — configure these in the sending provider:")
    for hook in (tv, cme):
        print(f"    {hook.name:<12} POST {base}{hook.path}")
        print(f"    {'':<12} secret: {hook.secret}")
    print()
    print("  Every payload must include request_id and sent_at, and be signed:")
    print("    X-NeoFL-Signature: hex(hmac_sha256(secret, raw_body))")
    print()
    print("  This surface is READ-ONLY and cannot place orders (decision D-001).")
    print("=" * 68)

    server = make_server(api, webhooks, store, host=args.host, port=args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
