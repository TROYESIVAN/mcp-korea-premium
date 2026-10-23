# ChainPulse Korea — MCP server

Korea market microstructure data for AI agents, exposed as MCP tools.
No API key, no account, read-only.

Four tools, all free:

| Tool | What it returns |
|---|---|
| `korea_premium` | Per asset on Upbit and Bithumb: KRW price, OKX USDT reference price, trade staleness, and three premiums — `prem_usdt`, `prem_vs_btc`, `prem_fx` (ECB reference rate) |
| `usdt_krw_premium` | USDT-KRW price on both Korean venues vs the ECB reference rate |
| `upbit_caution_watchlist` | Every KRW market currently carrying an Upbit investment caution / warning flag, with when the flag was first observed |
| `krw_listing_changes` | New listings and delistings across the full KRW market list of Upbit and Bithumb over the last N days |

## Install

```bash
uvx --from git+https://github.com/<owner>/mcp-korea-premium chainpulse-korea
```

or with pip:

```bash
pip install "git+https://github.com/<owner>/mcp-korea-premium"
chainpulse-korea
```

## Configure an MCP client

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "chainpulse-korea": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/<owner>/mcp-korea-premium", "chainpulse-korea"]
    }
  }
}
```

Cursor / Cline / any stdio MCP client: same command and args.

## Data sources

- Upbit public API (`market/all`, `ticker`) — KRW markets, caution/warning flags
- Bithumb public API (`ALL_KRW`, `v1/ticker`) — KRW markets
- OKX public API (`market/ticker`) — USDT reference price
- frankfurter.app — ECB reference rates (business days only; returned with `fx_timestamp`)

The upstream snapshot refreshes every 5 minutes. Responses carry `snapshot_ts`,
`snapshot_age_s` and `observed_since` so a caller can judge freshness.

## Notes on accuracy

- `mapping_status` marks assets whose symbol mapping between venues has been verified (`verified`)
  versus still under observation (`candidate`). Candidate assets do not get a premium figure.
- A token that trades in Korea but has no OKX reference price returns flags only.
- A token that is not listed in Korea returns `not_listed_in_korea`.
- `stale_ticker` / `stale_ticker_inferred` mark venues whose last trade is old.

Listing-change detection polls the open market list every 5 minutes. It is designed for
**data completeness**, not for announcement-speed alerting — a dedicated news bot will
usually be faster. Use it to check *what changed*, not to front-run an announcement.

## Disclaimer

Measurements only. No investment advice, no price predictions, no trade execution.
Trading decisions are yours.

## License

MIT
