## Why

When resetting the test database (drop & reinstall), all custom configuration is lost — taxes, journals, rental settings. This forces manual reconfiguration each time, which is error-prone and time-consuming.

## What Changes

- Add `initial_config.xml` data file to `ggg_rental` module with repeatable configuration
- Add `l10n_th` as a module dependency to ensure Thai localization is always installed first

## Capabilities

### New Capabilities
- `initial-config`: Automatic provisioning of custom taxes, payment journals, and rental settings on module install

### Modified Capabilities

## Impact

- **Files**: `data/initial_config.xml` (new), `__manifest__.py` (updated dependency + data list)
- **No new model changes**
- **Idempotent**: uses `noupdate="1"` so existing records are not overwritten on module upgrade
