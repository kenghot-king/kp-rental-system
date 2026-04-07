# BRD: Odoo MCP Server

> Generic MCP server for Claude Code ↔ Odoo integration via JSON-RPC
> Date: 2026-04-06

---

## 1. Overview

A Model Context Protocol (MCP) server that connects Claude Code to any running Odoo instance via JSON-RPC. Provides generic tools for querying, creating, updating, and executing methods on any Odoo model — no custom endpoints needed, no updates required when models change.

```
┌──────────┐     stdio     ┌──────────────┐   JSON-RPC   ┌──────────┐
│  Claude  │──────────────▶│  MCP Server  │─────────────▶│  Odoo    │
│  Code    │◀──────────────│  (Python)    │◀─────────────│  Instance│
└──────────┘               └──────────────┘              └──────────┘
```

---

## 2. Goals

1. **Dev acceleration** — Claude can query live Odoo data, inspect models, verify field values, and test features without the developer switching to a browser
2. **Automated testing** — Claude can create test records, execute workflows, and verify expected outcomes programmatically
3. **Generic & reusable** — Works with any Odoo module, any model, any version (14+). Build once, never update for model changes
4. **Zero Odoo modification** — Uses only Odoo's built-in JSON-RPC endpoints, no server-side module required

---

## 3. Architecture

### 3.1 Tech Stack

- **Language:** Python 3.10+
- **MCP SDK:** `mcp` (Anthropic's Python SDK)
- **Transport:** stdio (for Claude Code integration)
- **Odoo Communication:** JSON-RPC via `requests` or `aiohttp`
- **Config:** Environment variables or `.env` file

### 3.2 Project Structure

```
odoo-mcp-server/
├── src/
│   └── odoo_mcp/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point
│       ├── odoo_client.py      # JSON-RPC client wrapper
│       └── tools.py            # MCP tool definitions
├── pyproject.toml
├── .env.example
└── README.md
```

### 3.3 Configuration

```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo19
ODOO_USER=admin
ODOO_PASSWORD=admin
```

---

## 4. MCP Tools Specification

### 4.1 `odoo_authenticate`

Connect and authenticate to the Odoo instance. Must be called first or auto-called on first tool use.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | No | Override ODOO_URL from env |
| db | string | No | Override ODOO_DB from env |
| login | string | No | Override ODOO_USER from env |
| password | string | No | Override ODOO_PASSWORD from env |

**Returns:** Session info (uid, user name, database)

### 4.2 `odoo_search_read`

Search and read records from any Odoo model.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name (e.g. `sale.order`) |
| domain | array | No | Odoo domain filter (default: `[]`) |
| fields | array | No | Fields to return (default: all) |
| limit | integer | No | Max records (default: 80) |
| offset | integer | No | Pagination offset |
| order | string | No | Sort order (e.g. `create_date desc`) |

**Returns:** List of record dicts

**Examples:**
```
odoo_search_read("sale.order", [("is_rental_order","=",true),("rental_status","=","pickup")], ["name","partner_id","rental_start_date"])
odoo_search_read("rental.damage.log", [("lot_id.name","=","SN001")])
odoo_search_read("product.template", [("rent_ok","=",true)], ["name","display_price","qty_in_rent"])
```

### 4.3 `odoo_read`

Read specific records by IDs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| ids | array | Yes | List of record IDs |
| fields | array | No | Fields to return (default: all) |

**Returns:** List of record dicts

### 4.4 `odoo_create`

Create one or more records.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| values | object/array | Yes | Field values dict, or list of dicts for multi-create |

**Returns:** Created record ID(s)

### 4.5 `odoo_write`

Update existing records.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| ids | array | Yes | Record IDs to update |
| values | object | Yes | Field values to write |

**Returns:** `true` on success

### 4.6 `odoo_unlink`

Delete records.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| ids | array | Yes | Record IDs to delete |

**Returns:** `true` on success

### 4.7 `odoo_execute`

Call any method on any model. This is the most powerful tool — it can trigger wizards, run actions, call custom business logic.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| method | string | Yes | Method name to call |
| args | array | No | Positional arguments (default: `[]`) |
| kwargs | object | No | Keyword arguments (default: `{}`) |
| ids | array | No | Record IDs (prepended to args if provided) |

**Returns:** Method return value

**Examples:**
```
odoo_execute("sale.order", "action_confirm", ids=[42])
odoo_execute("sale.order", "action_open_pickup", ids=[42])
odoo_execute("product.template", "fields_get", kwargs={"attributes": ["string","type","required"]})
```

### 4.8 `odoo_fields_get`

Inspect model schema — fields, types, labels, relations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| attributes | array | No | Field attributes to return (default: `["string","type","relation","required","readonly"]`) |

**Returns:** Dict of field name → field attributes

### 4.9 `odoo_search_count`

Count records matching a domain without fetching data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Odoo model name |
| domain | array | No | Odoo domain filter (default: `[]`) |

**Returns:** Integer count

---

## 5. Claude Code Integration

### 5.1 MCP Config

Add to Claude Code's MCP settings (`~/.claude/claude_code_config.json` or project-level):

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "odoo_mcp.server"],
      "cwd": "/path/to/odoo-mcp-server/src",
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo19",
        "ODOO_USER": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

### 5.2 Usage Scenarios

**Development verification:**
```
"Check if is_rental_payment field exists on account.payment"
→ odoo_fields_get("account.payment") → look for field in result

"Show me all rental orders in pickup status"
→ odoo_search_read("sale.order", [("is_rental_order","=",true),("rental_status","=","pickup")])

"What views are registered for rental.damage.log?"
→ odoo_search_read("ir.ui.view", [("model","=","rental.damage.log")], ["name","type"])
```

**Automated testing:**
```
"Run TC-RO-001: create rental order with dates and verify status"
→ odoo_create("sale.order", {...})
→ odoo_search_read("sale.order", [("id","=",new_id)], ["rental_status","duration_days"])
→ assert rental_status == "draft" and duration_days == 2

"Run TC-DA-010: damage log per serial"
→ create order → confirm → pickup with serials → return as damaged
→ odoo_search_read("rental.damage.log", [("order_id","=",order_id)])
→ assert 3 records, each with fee=300
```

---

## 6. Error Handling

| Error | MCP Response |
|-------|-------------|
| Odoo not running | Tool returns error: "Connection refused at {url}" |
| Auth failure | Tool returns error: "Authentication failed for {user}@{db}" |
| Access denied | Tool returns Odoo AccessError message |
| Invalid model | Tool returns error: "Model '{model}' not found" |
| Invalid field | Tool returns Odoo ValueError message |
| Session expired | Auto-reconnect and retry |

---

## 7. Security Considerations

- Credentials stored in env vars or `.env` file (never hardcoded)
- `.env` file in `.gitignore`
- MCP server runs locally (stdio), no network exposure
- All operations execute under the authenticated Odoo user's access rights
- No elevated privileges — respects Odoo record rules and ACLs

---

## 8. Non-Goals (Out of Scope)

- No SSE/HTTP transport (stdio only for Claude Code)
- No Odoo module installation required
- No custom Odoo endpoints
- No caching layer (Odoo handles its own caching)
- No multi-instance management (one connection at a time)
- No user-facing UI (this is a developer tool)

---

## 9. Future Extensions

| Feature | Description | When |
|---------|-------------|------|
| Test runner | Wrapper tool that executes `odoo-bin --test-tags` and parses output | After MCP is stable |
| Log reader | Read Odoo server logs for error diagnosis | When needed |
| Module installer | Install/upgrade modules via RPC | When needed |
| Multi-instance | Switch between dev/staging/prod | When needed |
| AI Assistant reuse | Same tool design powers user-facing chat widget in Odoo | Phase 2+ |
