# Tools

Generated file - do not edit by hand. It is produced from the server's own tool definitions, so it matches what `tools/list` returns.

All 7 tools are read-only. Endpoint: `https://www.topimones.lt/mcp`. Protocol revisions: 2026-07-28, 2025-11-25, 2025-06-18, 2025-03-26; `initialize` answers the requested revision when it is supported, otherwise `2025-11-25`; a request without an `MCP-Protocol-Version` header is served as `2025-03-26`.

## Answer envelope

Every successful answer is `structuredContent` shaped `{ data, meta }`:

- `data`: the result. A field or block that cannot be served is `null`.
- `meta.withheld`: one `{ field, reason }` entry for each such `null`. Missing is never zero: report the reason, never estimate the value.
- `meta.sources`: for each source behind the answer its `code`, `licence`, `attribution`, `url` and `retrieved_at`. Name the publisher when you reuse the data.
- `meta.as_of`: the date the answer describes.
- `meta.next_cursor`: on lists, pass it back as `cursor` (with the same other arguments) for the next page; `null` means there is no further page. Answers are capped at 16 KB, so long lists continue this way.
- `meta.usage`: what the answer cost and what is left for the day.

`meta.withheld[].reason` is one of:

| Reason | Meaning |
|---|---|
| `not_collected` | We do not collect this for the entity or the country. |
| `not_licensed` | A source behind the block has no confirmed licence, so the block is not served. |
| `small_cell` | A count or a statistic over too few entities or persons. |
| `privacy` | A privacy rule withholds it (for example a wage floor). |
| `tier` | The coverage tier of the entity does not include the block. |
| `unknown_for_date` | No complete snapshot covers the requested date. |

Treat any other value as "withheld" as well.

## Errors

A tool error is a result with `isError: true` and `structuredContent` `{ "error": { "code", "message" } }`:

| Code | Meaning |
|---|---|
| `invalid_request` | Bad arguments; the message says which. |
| `not_in_coverage` | No servable record; does not mean the entity does not exist. |
| `quota_exceeded` | A daily limit is used up; budget names it and resets_at gives the reset (UTC). Without a key it is sent with HTTP 429 and Retry-After. |
| `rate_limited` | Too many requests; wait retry_after_s seconds. Without a key it comes as HTTP 429 and JSON-RPC error -31006, not as a tool result. |
| `busy` | Service busy or the answer missed its 5 s deadline; retry after retry_after_s. |
| `internal_error` | The answer could not be built. |

## Limits without a key

- 30 requests a minute per address
- 300 tool calls a day per address
- 300 entity records (identity disclosures) a day per address
- 100 detail disclosures (for example one entity in get_entity_series) a day per address
- 30 misses (ids or queries with no servable record) a day per address
- 2 requests in flight at once per address
- answers are capped at 16 KB; continue with meta.next_cursor

When a limit is reached:

- Per-minute or in-flight limit: HTTP 429 with a `Retry-After` header and JSON-RPC error `-31006` with `data.error` `"rate_limited"` and `data.retry_after_s` (seconds). It is not a tool result.
- Daily limit used up (calls, entity records, detail disclosures or misses): HTTP 429 with `Retry-After` (seconds to 00:00 UTC) and a tool result with `isError: true` whose error `quota_exceeded` names the `budget` and gives `resets_at`.
- Limits count per address: an IPv4 address on its own, an IPv6 address by its /64. A client whose egress alternates between IPv4 and IPv6 sees two separate counters in `meta.usage`.

Wait as long as `Retry-After` says; do not retry in a loop. Daily counters reset at 00:00 UTC.

Each tool description below names what an answer costs: one call, plus entity records ("disclosures") counted against the daily limits above.

## resolve_entity

**Find an entity by name, id, VAT number or LEI**

Resolve a name, a national id, a public id "CC:id", a VAT number or an LEI to up to 10 candidate entities (register identity only), each with its coverage tier and its public id ("LT:110053842"). Pass the two parts as country and id to get_entity and get_entity_history, the whole id to get_entity_series. Name pages carry meta.next_cursor; 200 candidates are reachable per query. An LEI needs no country (it is unique worldwide). Costs one identity disclosure per candidate; an id or identifier with no match counts one miss.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `q` | `string` | yes | A name (words of 3+ characters, any case, diacritics optional), a national id, a public id "CC:id", a VAT number or an LEI. |
| `country` | `string` | no | ISO 3166-1 alpha-2. Required unless q is a full public id "CC:id" or an LEI (an LEI is unique worldwide). |
| `cursor` | `string` | no | meta.next_cursor of the previous page, with the same q and country. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "resolve_entity",
    "arguments": {
      "q": "telsiu keliai",
      "country": "LT"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "candidates": [
      {
        "id": "<id>",
        "country": "<country>",
        "national_id": "<national_id>",
        "name": "<name>",
        "legal_form": {
          "elf": null,
          "national": "<national>"
        },
        "status": "active",
        "status_date": "<status_date>",
        "registered_on": "<registered_on>",
        "struck_off_on": "<struck_off_on>",
        "tier": "identity",
        "match": "id",
        "confidence": 0
      }
    ],
    "same_name_warning": false
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "served",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## get_entity

**One entity by id, in blocks**

The register identity of one entity by exact id (country + the national id, the part after "LT:" of a public id; resolve_entity finds it from a name), plus the enriched blocks asked for in include: financials, workforce, tax, debt, insolvency, procurement, score. A block is null when it is not asked for, not collected, not licensed or outside the entity's coverage tier; meta.withheld names the reason. An id outside coverage answers not_in_coverage, which does not mean the entity does not exist. With as_of=YYYY-MM-DD, the name, legal form and status valid on that date (null with unknown_for_date where no history covers it); enriched blocks are not dated in this version. Costs one identity disclosure, plus one detail disclosure when an enriched block is served.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `country` | `string` | yes | ISO 3166-1 alpha-2 country code, any case (e.g. "LT"). |
| `id` | `string` | yes | National id as issued by the register (the part after "CC:" of a public id). |
| `include` | `string[]` | no | Blocks to return besides identity (always returned). Default: identity only. Values: `identity`, `financials`, `workforce`, `tax`, `debt`, `insolvency`, `procurement`, `score`. Default: `["identity"]`. |
| `detail` | `string` | no | concise: the newest year of each yearly block (tax: also the last full year when the newest is the running, partial year); full: every year held. Values: `concise`, `full`. Default: `"concise"`. |
| `as_of` | `string` | no | YYYY-MM-DD: the identity valid on that date, as we know it now. Not after today in the country's calendar; today = omitted. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_entity",
    "arguments": {
      "country": "LT",
      "id": "110053842"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "id": "<id>",
    "country": "<country>",
    "national_id": "<national_id>",
    "name": "<name>",
    "legal_form": {
      "elf": null,
      "national": "<national>"
    },
    "status": "active",
    "status_date": "<status_date>",
    "registered_on": "<registered_on>",
    "struck_off_on": "<struck_off_on>",
    "tier": "identity",
    "identifiers": [
      {
        "scheme": "lei",
        "value": "<value>"
      }
    ],
    "financials": null,
    "workforce": null,
    "tax": null,
    "debt": null,
    "insolvency": null,
    "procurement": null,
    "score": null
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "served",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## search_entities

**List entities by filters**

To find one entity from a name or an id use resolve_entity; this lists many. Identity rows of entities matching filters: name words, legal form, status and registration window on the register; score_risk and vat_registered where the country has them and their source is licensed. A narrowing filter is required (a name word, or a legal form or status - not every status - with a registration window of whole calendar years, at most 5). Up to 20 rows a page, 200 per filter set, no totals; person-like legal forms are never listed. Costs one identity disclosure per row, plus one detail disclosure per row (at least one) with score_risk; an empty page with no next cursor counts one miss. legal_form also takes the common national abbreviation of a form. Identity filters all run before paging, so a page of identity filters is empty only at the end of the matches.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `country` | `string` | yes | ISO 3166-1 alpha-2 country code, any case (e.g. "LT"). |
| `name` | `string` | no | Name words (3+ characters each, any case, diacritics optional). |
| `legal_form` | `string[]` | no | Legal forms: national labels or ISO 20275 ELF codes, as lookup_code kind=legal_form lists them, or the common national abbreviation of a form (lookup_code kind=legal_form with q set to it shows the form it names). |
| `status` | `string[]` | no | Register statuses. Values: `active`, `winding_up`, `insolvent`. |
| `registered_from` | `string` | no | Registered on or after this date (YYYY-MM-DD). Without name it must be 1 January of a year (YYYY-01-01). |
| `registered_to` | `string` | no | Registered on or before this date (YYYY-MM-DD). Without name it must be 31 December (YYYY-12-31), at most 5 calendar years after registered_from. |
| `score_risk` | `string[]` | no | Enriched filter: published score risk level. Costs one detail disclosure per row. Values: `low`, `medium`, `high`, `critical`. |
| `vat_registered` | `boolean` | no | Enriched filter: registered VAT payer now (true) or not / unknown (false). |
| `page_size` | `integer` | no | Rows per page, 1-20 (at most 10 with an enriched filter). Default: `20`. |
| `cursor` | `string` | no | meta.next_cursor of the previous page, with the same filters. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_entities",
    "arguments": {
      "country": "LT",
      "name": "statyba"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "rows": [
      {
        "id": "<id>",
        "country": "<country>",
        "national_id": "<national_id>",
        "name": "<name>",
        "legal_form": {
          "elf": null,
          "national": "<national>"
        },
        "status": "active",
        "status_date": "<status_date>",
        "registered_on": "<registered_on>",
        "struck_off_on": "<struck_off_on>",
        "tier": "identity"
      }
    ],
    "truncated_at_depth": false
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "served",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## get_entity_series

**One series over time for up to five entities**

Use it for values over several periods; for the current state of one entity, get_entity. Numbers over time for 1-5 entities given as whole public ids ("LT:110053842"): revenue, net_profit or tax_paid per year, insured or avg_wage per month, between from and to (at most 12 years or 24 months). A series whose source has no confirmed licence is null with not_licensed. Wages are withheld under the small-cell floor and where two months would isolate a few people. Costs one detail disclosure per entity served; an id outside coverage or without a published profile counts one miss.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `series` | `string` | yes | revenue, net_profit and tax_paid are yearly; insured and avg_wage are monthly. Values: `revenue`, `net_profit`, `tax_paid`, `insured`, `avg_wage`. |
| `ids` | `string[]` | yes | 1-5 different public ids "CC:national_id". |
| `from` | `string` | yes | First period, inclusive: YYYY for grain year, YYYY-MM for grain month. |
| `to` | `string` | yes | Last period, inclusive. At most 12 years or 24 months after from. |
| `grain` | `string` | yes | Must match the series: year or month. Values: `year`, `month`. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_entity_series",
    "arguments": {
      "series": "tax_paid",
      "ids": [
        "LT:110053842"
      ],
      "from": "2020",
      "to": "2024",
      "grain": "year"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "series": "tax_paid",
    "grain": "year",
    "unit": "currency",
    "items": [
      {
        "id": "<id>",
        "currency": "<currency>",
        "points": [
          {
            "period": "<period>",
            "value": 0,
            "withheld": null,
            "partial": true,
            "period_end": null
          }
        ]
      }
    ],
    "not_in_coverage": [
      "<not_in_coverage>"
    ]
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "not_requested",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "served",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## get_entity_history

**When an identity attribute changed**

Use it for every period of an attribute; for the identity on one date, get_entity with as_of is simpler. The periods of the name, legal form and status of one entity (country + the national id, the part after "LT:" of a public id): each value with the day it was first observed (valid_from) and the day it was replaced (valid_to, exclusive; null = current). History starts at the first register load that recorded the attribute; before it the attribute is unknown (meta.withheld: unknown_for_date). Oldest first, at most 100 periods per page. An id outside coverage answers not_in_coverage, which does not mean the entity does not exist. Costs one identity disclosure.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `country` | `string` | yes | ISO 3166-1 alpha-2 country code, any case (e.g. "LT"). |
| `id` | `string` | yes | National id as issued by the register (the part after "CC:" of a public id). |
| `attributes` | `string[]` | no | Attributes whose periods to return. Default: all three. Values: `name`, `legal_form`, `status`. Default: `["name","legal_form","status"]`. |
| `from` | `string` | no | YYYY-MM-DD: only periods still valid on or after this date. |
| `to` | `string` | no | YYYY-MM-DD: only periods that started on or before this date. |
| `cursor` | `string` | no | meta.next_cursor of the previous page, with the same parameters. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_entity_history",
    "arguments": {
      "country": "LT",
      "id": "110053842"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "id": "<id>",
    "periods": [
      {
        "attribute": "name",
        "value": "<value>",
        "legal_form_elf": "<legal_form_elf>",
        "valid_from": "<valid_from>",
        "valid_to": "<valid_to>",
        "change": false,
        "register_date": "<register_date>"
      }
    ]
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "served",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## lookup_code

**Look up legal forms and statuses**

The values the filters accept, per country: legal forms (ISO 20275 ELF code and national label; q also finds a common national abbreviation of the form) and register statuses (platform status and the national labels it maps from), every value a page at a time (meta.next_cursor). kind=activity is not served yet: its source has no confirmed licence, so it answers no rows with meta.withheld not_licensed. Costs one call only.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `kind` | `string` | yes |  Values: `activity`, `legal_form`, `status`. |
| `country` | `string` | yes | ISO 3166-1 alpha-2 country code, any case (e.g. "LT"). |
| `q` | `string` | no | Words, a code or a code prefix. Required for activity; without it legal_form and status list every value, a page at a time. |
| `limit` | `integer` | no | Maximum rows per page, 1-20. Default: `20`. |
| `cursor` | `string` | no | legal_form and status: meta.next_cursor of the previous page, with the same kind, country and q. Not for activity. |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "lookup_code",
    "arguments": {
      "kind": "legal_form",
      "country": "LT"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "kind": "legal_form",
    "rows": [
      {
        "code": "<code>",
        "scheme": "<scheme>",
        "label": "<label>",
        "national_value": "<national_value>",
        "entities": 0
      }
    ],
    "truncated": false
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "not_requested",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```

## get_coverage

**Coverage, sources and licences of a country**

For one country: every data domain with its sources (licence, licence status, cadence, last successful run) and whether it is served or why not; the last completed register load; servable entity counts by coverage tier and status, rounded to hundreds. Your remaining daily usage is in meta.usage. Costs one call only.

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `country` | `string` | yes | ISO 3166-1 alpha-2 country code, any case (e.g. "LT"). |

### Example call

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_coverage",
    "arguments": {
      "country": "LT"
    }
  }
}
```

### Answer

Placeholder values (`<...>`) show the shape.

```json
{
  "data": {
    "country": "<country>",
    "name": "<name>",
    "domains": [
      {
        "domain": "identity",
        "served": false,
        "reason": "not_collected",
        "sources": [
          {
            "code": "<code>",
            "title": "<title>",
            "publisher": "<publisher>",
            "url": "<url>",
            "licence": "<licence>",
            "licence_status": "confirmed",
            "cadence": "<cadence>",
            "last_success_at": "<last_success_at>",
            "state": "fresh"
          }
        ],
        "earliest_available": "<earliest_available>"
      }
    ],
    "identity_load": {
      "source": "<source>",
      "completed_at": "<completed_at>",
      "rows": 0
    },
    "entities": {
      "total": 0,
      "by_tier": {
        "identity": 0,
        "enriched": 0,
        "evaluated": 0
      },
      "by_status": {
        "active": 0,
        "winding_up": 0,
        "insolvent": 0,
        "struck_off": 0
      }
    }
  },
  "meta": {
    "coverage": {
      "country": "<country>",
      "tier": "identity",
      "domains": {
        "identity": "not_requested",
        "financials": "not_requested",
        "workforce": "not_requested",
        "tax": "not_requested",
        "debt": "not_requested",
        "insolvency": "not_requested",
        "procurement": "not_requested",
        "score": "not_requested"
      }
    },
    "as_of": "<as_of>",
    "sources": [
      {
        "code": "<code>",
        "licence": "<licence>",
        "licence_status": "confirmed",
        "attribution": "<attribution>",
        "url": "<url>",
        "retrieved_at": "<retrieved_at>",
        "changes_made": [
          "selected"
        ]
      }
    ],
    "withheld": [],
    "usage": {
      "cost": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "remaining": {
        "calls": 0,
        "identity_disclosures": 0,
        "detail_disclosures": 0,
        "misses": 0
      },
      "resets_at": "<resets_at>"
    },
    "next_cursor": "<next_cursor>"
  }
}
```
