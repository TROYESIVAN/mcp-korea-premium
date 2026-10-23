#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ChainPulse Korea — MCP server exposing four free Korea-market datasets.

Wraps the public read-only endpoints of api.onchainlabs.cc as MCP tools so any
MCP-capable agent (Claude Desktop, Cursor, Cline, ...) can query Korea market
microstructure without an API key.

Data: Upbit / Bithumb / OKX public APIs + ECB reference rates (frankfurter).
Measurements only — no advice, no predictions.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from mcp.server.fastmcp import FastMCP

BASE = os.environ.get("KOREA_API_BASE", "https://api.onchainlabs.cc")
CLIENT_TAG = "mcp-wrapper"
TIMEOUT = 30

mcp = FastMCP("chainpulse-korea")


def _get(path: str, params: dict | None = None) -> dict:
    url = BASE.rstrip("/") + path
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean)
    req = urllib.request.Request(url, headers={
        "User-Agent": "chainpulse-korea-mcp/1.0",
        "X-Client": CLIENT_TAG,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        return {"error": True, "status": e.code, "detail": body}
    except Exception as e:  # network, timeout, json
        return {"error": True, "detail": str(e)[:300]}


@mcp.tool()
def korea_premium(venue: str = "both", asset: str | None = None, limit: int = 20) -> str:
    """Korea premium snapshot: per asset on Upbit and Bithumb, the KRW price,
    the OKX USDT reference price, trade staleness and three premiums
    (prem_usdt, prem_vs_btc, prem_fx).

    Args:
        venue: upbit | bithumb | both (default both)
        asset: single symbol such as BTC (optional)
        limit: max rows, default 20
    """
    return json.dumps(_get("/api/kr/premium", {"venue": venue, "asset": asset, "limit": limit}),
                      ensure_ascii=False)[:20000]


@mcp.tool()
def usdt_krw_premium(venue: str = "both") -> str:
    """USDT-KRW premium: the KRW price of USDT on Upbit and Bithumb against the
    ECB reference rate — how far Korean dollar demand deviates from the official rate.

    Args:
        venue: upbit | bithumb | both (default both)
    """
    return json.dumps(_get("/api/kr/usdt-premium", {"venue": venue}), ensure_ascii=False)[:20000]


@mcp.tool()
def upbit_caution_watchlist(flag: str = "all", asset: str | None = None, limit: int = 50) -> str:
    """Upbit caution and warning watchlist: every KRW market currently carrying an
    Upbit investment caution or warning flag (global price difference, deposit
    surge, volume surge, trading volume) and when the flag was first observed.

    Args:
        flag: caution | warning | all (default all)
        asset: single symbol (optional)
        limit: max rows, default 50
    """
    return json.dumps(_get("/api/kr/caution", {"flag": flag, "asset": asset, "limit": limit}),
                      ensure_ascii=False)[:20000]


@mcp.tool()
def krw_listing_changes(days: int = 7, venue: str = "both") -> str:
    """KRW listing and delisting changes: new listings and removals across the full
    KRW market list of Upbit and Bithumb over the last N days.

    Note: detection runs every 5 minutes on the open market list, so a change is
    reported within minutes of the pair becoming tradable — this is NOT the
    announcement-level latency of a dedicated news bot.

    Args:
        days: lookback window in days, default 7, max 30
        venue: upbit | bithumb | both (default both)
    """
    days = max(1, min(int(days), 30))
    return json.dumps(_get("/api/kr/listings", {"days": days, "venue": venue}),
                      ensure_ascii=False)[:20000]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
