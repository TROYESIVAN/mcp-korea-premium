"""Local smoke test: spin up the MCP server over stdio and call each tool."""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


async def main() -> int:
    params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(HERE, "server.py")],
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])
            calls = [
                ("korea_premium", {"venue": "both", "limit": 3}),
                ("usdt_krw_premium", {}),
                ("upbit_caution_watchlist", {"flag": "all", "limit": 3}),
                ("krw_listing_changes", {"days": 7}),
            ]
            ok = 0
            for name, args in calls:
                res = await session.call_tool(name, args)
                text = res.content[0].text if res.content else ""
                try:
                    data = json.loads(text)
                    bad = isinstance(data, dict) and data.get("error")
                except Exception:
                    bad = True
                print("%-24s %s  %s" % (name, "FAIL" if bad else "OK  ", text[:150].replace("\n", " ")))
                if not bad:
                    ok += 1
            print("passed %d/%d" % (ok, len(calls)))
            return 0 if ok == len(calls) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
