# topimones-mcp

[![TOP Įmonės MCP connector](https://glama.ai/mcp/connectors/lt.topimones/registry/badges/score.svg)](https://glama.ai/mcp/connectors/lt.topimones/registry)

The public [Model Context Protocol](https://modelcontextprotocol.io) server of [topimones.lt](https://www.topimones.lt), the Lithuanian business registry. It lets an AI agent find a Lithuanian company and read its register data, with the source and the date next to every value.

- **URL:** `https://www.topimones.lt/mcp`
- **Transport:** Streamable HTTP, `POST`, JSON-RPC 2.0, no session
- **Authentication:** none. No API key, no sign-up.
- **Read-only:** no tool changes anything.
<!-- generated:protocol:start -->
- **Protocol revisions:** `2026-07-28`, `2025-11-25`, `2025-06-18`, `2025-03-26`; `initialize` answers the requested revision when it is supported, otherwise `2025-11-25`; a request without an `MCP-Protocol-Version` header is served as `2025-03-26`.
- **Official MCP Registry:** `lt.topimones/registry` ([search](https://registry.modelcontextprotocol.io/v0/servers?search=topimones))
<!-- generated:protocol:end -->
- **Status:** beta. Tools, answer fields and limits may still change; the page below always shows the current state.

Lietuviškai: žr. [skyrių apačioje](#lietuviškai).

## Quick start

### Claude Code

```bash
claude mcp add --transport http topimones https://www.topimones.lt/mcp
```

### Cursor

Add to `~/.cursor/mcp.json` (or `.cursor/mcp.json` in a project):

```json
{
  "mcpServers": {
    "topimones": {
      "url": "https://www.topimones.lt/mcp"
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "topimones": {
      "type": "http",
      "url": "https://www.topimones.lt/mcp"
    }
  }
}
```

### Claude (claude.ai and desktop app) and ChatGPT

Add a remote MCP server (a custom connector) in the client's settings, enter `https://www.topimones.lt/mcp` and choose no authentication. Menu names change between versions, so follow your client's current documentation for adding a remote MCP server by URL.

Claude Desktop can also read a config file; it starts local programs, so a remote server goes through the `mcp-remote` bridge (needs Node.js). See [`examples/claude-desktop-config.json`](examples/claude-desktop-config.json).

### Any other MCP client

Streamable HTTP, `POST`, no authentication, URL `https://www.topimones.lt/mcp`. Requests that carry an `Origin` header are refused, so call the server from a server-side client, not from a web page.

### Try it without a client

[`examples/curl.sh`](examples/curl.sh) (initialize, list the tools, one call) and [`examples/python_client.py`](examples/python_client.py) (standard library only).

Send a descriptive `User-Agent` header (for example `User-Agent: my-agent/1.0`). The site's edge refuses some library defaults, such as Python's `Python-urllib/3.x`, with HTTP 403 (Cloudflare error 1010) before the request reaches the server; the Python example sets one for this reason. Send `Content-Type: application/json` and `Accept: application/json, text/event-stream`.

## Tools

<!-- generated:tools:start -->
| Tool | What it does |
|---|---|
| `resolve_entity` | Find an entity by name, id, VAT number or LEI. |
| `get_entity` | One entity by id, in blocks. |
| `search_entities` | List entities by filters. |
| `get_entity_series` | One series over time for up to five entities. |
| `get_entity_history` | When an identity attribute changed. |
| `lookup_code` | Look up legal forms and statuses. |
| `get_coverage` | Coverage, sources and licences of a country. |
<!-- generated:tools:end -->

Input fields, example calls and the answer shape of every tool: [`docs/TOOLS.md`](docs/TOOLS.md).

## Example prompts

1. "Find the company 'Telšių keliai' and tell me its code, legal form and status."
2. "How much tax did Telšių keliai (LT:180200843) pay each year from 2021 to 2024?"
3. "List private limited companies (uždaroji akcinė bendrovė, UAB) registered in 2023 whose name contains 'logistika'."
4. "Which legal form code corresponds to 'uždaroji akcinė bendrovė'?"
5. "Which data domains does the Lithuanian registry server not serve yet, and why?"

## What you get, and what you do not

Every answer states its source, licence and as-of date. When a value cannot be served the field is `null` and `meta.withheld` names the reason; the server does not invent numbers.

<!-- generated:domains:start -->
Data domains served today: `identity`, `tax`, `insolvency`, `procurement`. Withheld as `not_licensed` until the licence of their sources is confirmed: `financials`, `workforce`, `debt`, `score`.
<!-- generated:domains:end -->

Not served, at present:

- **Financial statements, workforce and wages, SODRA debt and the EBRS reputation score** are withheld until the data licences of their sources are confirmed (the score methodology is public, see below). Such fields come back as `null` with a reason such as `not_licensed`.
- **Natural persons:** person-like legal forms are not listed, and no names, contact details or court records are served.
- **Activity codes:** `lookup_code` with `kind` `activity` answers `not_licensed` until the licence of its source is confirmed; legal forms and statuses are served.
- **Identity on a past date:** the identity history is recent (its snapshots began in November 2026); for an earlier `as_of` the name, legal form and status are `null` with `unknown_for_date`.
- **Series:** `get_entity_series` lists only the periods that have a value; a year without data is left out, not returned as zero.
- **Struck-off entities** are not served. `not_in_coverage` means "no servable record", not "this entity does not exist".

`get_coverage` always tells you what is served today.

## Limits and fair use

Per address:

<!-- generated:limits:start -->
| Limit | Value |
|---|---|
| Requests per minute | 30 |
| Tool calls per day | 300 |
| Entity records per day | 300 |
| Detail disclosures per day (for example one entity in `get_entity_series`) | 100 |
| Misses per day (ids or queries with no servable record) | 30 |
| Requests in flight at once | 2 |

When a limit is reached:

- Per-minute or in-flight limit: HTTP 429 with a `Retry-After` header and JSON-RPC error `-31006` with `data.error` `"rate_limited"` and `data.retry_after_s` (seconds). It is not a tool result.
- Daily limit used up (calls, entity records, detail disclosures or misses): HTTP 429 with `Retry-After` (seconds to 00:00 UTC) and a tool result with `isError: true` whose error `quota_exceeded` names the `budget` and gives `resets_at`.
- Limits count per address: an IPv4 address on its own, an IPv6 address by its /64. A client whose egress alternates between IPv4 and IPv6 sees two separate counters in `meta.usage`.
<!-- generated:limits:end -->

Answers are capped at 16 KB; long lists continue with `meta.next_cursor`. Daily counters reset at 00:00 UTC. Wait as long as `Retry-After` says; do not retry in a loop.

Automated bulk copying of the data is not permitted. Bulk data and higher limits are available by agreement: [www.topimones.lt/kontaktai](https://www.topimones.lt/kontaktai).

## Data sources and attribution

Lithuanian public registers (Registrų centras, VMI, AVNT, Viešųjų pirkimų tarnyba, GLEIF and others), mostly through the open-data portal data.gov.lt. Each answer lists its sources in `meta.sources` with licence, attribution and retrieval time. Where a source is published under CC BY 4.0, name the publisher when you reuse the data. Data is modified by topimones.lt (selection, mapping, rounding).

## Links and status

- Page with the live status (served entity count, data domains, last update of each source) and the FAQ: <https://www.topimones.lt/imones-mcp> (Markdown version for agents: <https://www.topimones.lt/imones-mcp/md>). The same facts in the protocol: the `get_coverage` tool.
- Site summary for AI systems: <https://www.topimones.lt/llms.txt>
- Official MCP Registry: `lt.topimones/registry` (<https://registry.modelcontextprotocol.io/v0/servers?search=topimones>)
- Terms of use: <https://www.topimones.lt/naudojimo-salygos>
- Open-source reputation score (EBRS): <https://github.com/Rekvizitai-UAB/ebrs-score>
- Problems, questions and ideas: open an issue in this repository.

## Licence

The text and examples in this repository are MIT licensed, see [`LICENSE`](LICENSE). The data served by the server is **not** covered by the MIT licence: it is governed by the licences of its sources and by the [terms of topimones.lt](https://www.topimones.lt/naudojimo-salygos). See [`NOTICE`](NOTICE).

## Lietuviškai

Tai viešasis [topimones.lt](https://www.topimones.lt) įmonių MCP serveris: DI agentas suranda Lietuvos įmonę ir gauna jos registro duomenis su šaltiniu ir data. Prieigai **rakto nereikia**; adresas - `https://www.topimones.lt/mcp`.

- Prisijungimas: Claude Code - `claude mcp add --transport http topimones https://www.topimones.lt/mcp`; Cursor ir VS Code - pavyzdžiai viršuje; Claude ir ChatGPT - pridėkite nuotolinį MCP serverį pagal adresą.
- Septyni įrankiai: įmonės paieška, registro tapatybė, sąrašai pagal filtrus, rodiklių eiga, pavadinimo ir statuso istorija, filtrų reikšmės (teisinės formos ir statusai; veiklos kodai kol kas neteikiami), aprėptis.
- Oficialiame MCP Registry serveris vadinasi `lt.topimones/registry`.
<!-- generated:domains-lt:start -->
- Šiuo metu teikiama: registro tapatybė, mokesčiai, nemokumas, viešieji pirkimai. Kol nepatvirtintos šaltinių licencijos, neteikiama: finansinės ataskaitos, darbuotojai ir atlyginimai, skolos, EBRS balas.
<!-- generated:domains-lt:end -->
- Neteikiamos srities reikšmė - `null` su priežastimi. Fizinių asmenų, išregistruotų subjektų ir teismų bylų duomenų nėra.
<!-- generated:limits-lt:start -->
- Limitai vienam adresui: 30 užklausų per minutę, 300 įrankių iškvietimų ir 300 įmonių įrašų per parą, 100 išsamių įrašų ir 30 nerastų įrašų per parą, 2 užklausos vienu metu; atsakymas ne didesnis kaip 16 KB. Pasiekus limitą - HTTP 429 ir antraštė Retry-After.
<!-- generated:limits-lt:end -->
- Masinis automatizuotas kopijavimas neleidžiamas; dideli kiekiai ir didesni limitai - susitarus per [kontaktų puslapį](https://www.topimones.lt/kontaktai).
- Šio repozitorijaus tekstai ir pavyzdžiai - MIT licencija; duomenims ji netaikoma, juos reglamentuoja šaltinių licencijos ir [naudojimo sąlygos](https://www.topimones.lt/naudojimo-salygos).
- Puslapis su būsena: <https://www.topimones.lt/imones-mcp>. Pranešimai apie klaidas - GitHub issues.
