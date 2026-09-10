# Codex Development Guide

## Project scope

- This repository provides Odoo 19 Community Edition rental functionality.
- Custom modules live in `addons/`: `ggg_rental` is the core module; `ggg_gantt`,
  `ggg_rental_website`, and `ggg_app_launcher` are supporting modules.
- `enterprise/` is a local reference copy only. Do not modify or commit it.
- The rental lifecycle, stock moves, deposits, invoicing, payments, and Thai tax
  documents are business-critical. Preserve accounting and stock consistency.

## Change workflow

1. For an exploratory question, investigate first; do not change code.
2. For a material feature or business-rule change, create an OpenSpec change before
   implementation. Use the project OpenSpec skills: propose, apply, and archive.
3. Read the relevant consolidated specs in `openspec/specs/` and related archived
   changes before altering an established flow.
4. Keep changes scoped to the requested module. Do not modify Odoo core or the
   Enterprise reference copy to implement a custom feature.
5. Update tests and user-facing documentation whenever behavior changes.

## Implementation conventions

- Follow Odoo patterns: extend models with `_inherit`, declare XML/data files in the
  module manifest, and add access rules for new persistent models.
- Treat XML/QWeb reports as production code. Preserve Thai labels, PDF layout, and
  print behavior when changing report templates.
- Do not hard-code production credentials, URLs, database names, or tokens. Keep
  local MCP configuration untracked and use environment variables for real secrets.
- Do not make destructive changes to live Odoo data through MCP without explicit
  user approval and a verified target database.

## Verification

Run the static baseline after every code change:

```bash
python3 scripts/verify_addons.py
find addons -name '*.js' -print0 | xargs -0 -n1 node --check
```

For behavior changes, run the focused Odoo test suite in the local Docker database
after upgrading the affected module. For example:

```bash
docker compose exec odoo-ce odoo --addons-path=/mnt/extra-addons/test \
  --db_host=db --db_user=odoo --db_password=odoo \
  -d test_ce -u ggg_rental --test-enable --stop-after-init
```

Never run tests against production. Record manual QA steps when a workflow depends
on printed documents, browser UI behavior, stock moves, or accounting postings.
