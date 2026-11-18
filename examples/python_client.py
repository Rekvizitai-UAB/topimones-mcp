"""Call a tool of the public topimones.lt MCP server over HTTP JSON-RPC.

Standard library only, no API key. Usage:

    python python_client.py                              # resolve_entity example
    python python_client.py get_entity '{"country": "LT", "id": "110053842"}'
"""
import json
import sys
import urllib.request

URL = "https://www.topimones.lt/mcp"
VERSION = "2025-11-25"


def call(tool: str, arguments: dict) -> dict:
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": arguments}}
    request = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": VERSION,
            # The default "Python-urllib" user agent is refused by the site's edge (HTTP 403).
            "User-Agent": "topimones-mcp-example/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "resolve_entity"
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"q": "telsiu keliai", "country": "LT"}
    answer = call(name, args)
    result = answer.get("result", {})
    # structuredContent is {data, meta}; meta.withheld says why a value is null.
    print(json.dumps(result.get("structuredContent", answer), indent=2, ensure_ascii=False))
