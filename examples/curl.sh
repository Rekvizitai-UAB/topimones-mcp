#!/usr/bin/env bash
# Talk to the public MCP server by hand: initialize, list the tools, call one.
# No API key is needed. Requires curl; jq is optional (pretty-printing).
set -euo pipefail

URL="https://www.topimones.lt/mcp"
VERSION="2025-11-25"
pretty() { if command -v jq >/dev/null 2>&1; then jq .; else cat; fi; }
post() {
  curl -sS -X POST "$URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "MCP-Protocol-Version: $VERSION" \
    -d "$1" | pretty
}

echo "== initialize"
post '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"'"$VERSION"'","capabilities":{},"clientInfo":{"name":"curl-example","version":"1.0"}}}'

echo "== tools/list"
post '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

echo "== tools/call resolve_entity"
post '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"resolve_entity","arguments":{"q":"telsiu keliai","country":"LT"}}}'
