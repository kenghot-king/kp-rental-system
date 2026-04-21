## ADDED Requirements

### Requirement: Company has Damage Location and Inspection Location fields
The `res.company` model SHALL have two new Many2one fields to `stock.location` (internal usage only):
- `damage_loc_id`: the location where damaged returned items are sent
- `inspection_loc_id`: the location where items pending inspection are sent

#### Scenario: Fields exist on company
- **WHEN** a company record is loaded
- **THEN** `damage_loc_id` and `inspection_loc_id` are available as Many2one fields

### Requirement: Locations auto-created on company setup
When a new company is created, the system SHALL automatically create a Damage Location and an Inspection Location (both internal) and assign them to the company.

#### Scenario: New company gets locations
- **WHEN** a new company is created
- **THEN** a stock location named "Damage" and a stock location named "Inspection" are created for that company and assigned to `damage_loc_id` and `inspection_loc_id` respectively

### Requirement: Missing locations created on module install/upgrade
A `post_init_hook` SHALL create Damage and Inspection locations for any existing company that does not already have them assigned.

#### Scenario: Existing company missing locations after upgrade
- **WHEN** the module is installed or upgraded and a company has no `damage_loc_id` or `inspection_loc_id`
- **THEN** the hook creates and assigns both locations for that company

### Requirement: Locations configurable in Settings
Both `damage_loc_id` and `inspection_loc_id` SHALL be exposed in `res.config.settings` under the rental configuration section, allowing staff to point to a custom location if desired.

#### Scenario: Staff overrides Damage Location in Settings
- **WHEN** staff selects a different internal location for Damage Location in Settings and saves
- **THEN** company.damage_loc_id is updated and subsequent damaged returns route to the new location

#### Scenario: Staff overrides Inspection Location in Settings
- **WHEN** staff selects a different internal location for Inspection Location in Settings and saves
- **THEN** company.inspection_loc_id is updated and subsequent inspect returns route to the new location
