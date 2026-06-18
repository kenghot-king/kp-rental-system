## ADDED Requirements

### Requirement: Company-level Default Pickup Time

The system SHALL provide a company-level configuration field `default_pickup_time` representing the default time-of-day applied to a rental order's pickup datetime when no time component is explicitly specified.

The field SHALL be a `Float` storing hours since midnight (e.g., `9.0` for 09:00, `13.5` for 13:30) and SHALL default to `9.0` (09:00) on company creation.

#### Scenario: Default value on new company

- **WHEN** a new company is created
- **THEN** `company.default_pickup_time` equals `9.0`

#### Scenario: Existing company on module update

- **WHEN** the module is updated on an instance with existing companies
- **THEN** every existing `res.company` record has `default_pickup_time` equal to `9.0`

### Requirement: Company-level Default Return Time

The system SHALL provide a company-level configuration field `default_return_time` representing the default time-of-day applied to a rental order's return datetime when no time component is explicitly specified.

The field SHALL be a `Float` storing hours since midnight and SHALL default to `23.983333` (≈ 23:59) on company creation.

#### Scenario: Default value on new company

- **WHEN** a new company is created
- **THEN** `company.default_return_time` equals `23.983333` (23:59)

#### Scenario: Existing company on module update

- **WHEN** the module is updated on an instance with existing companies
- **THEN** every existing `res.company` record has `default_return_time` equal to `23.983333`

### Requirement: Settings UI exposure

The system SHALL expose `default_pickup_time` and `default_return_time` in the **Rental → Configuration → Settings** screen, inside the existing **Default Delay Costs** section, with the labels "Default Pickup Time" and "Default Return Time" respectively.

The fields SHALL use the `float_time` widget so users see HH:MM input rather than decimal hours.

#### Scenario: Settings page displays both fields

- **WHEN** a user with rental admin access opens **Rental → Configuration → Settings**
- **THEN** the **Default Delay Costs** section contains a "Default Pickup Time" field and a "Default Return Time" field
- **AND** both are rendered with the `float_time` widget (HH:MM format)

#### Scenario: User edits and saves a default

- **WHEN** a user changes "Default Pickup Time" from 09:00 to 10:00 and saves
- **THEN** `company.default_pickup_time` is updated to `10.0`

### Requirement: Pickup time snap on rental order

When the user sets `rental_start_date` on a sale order to a value whose time component equals `00:00:00` (the convention for a date-only pick), the system SHALL replace the time component with the company's `default_pickup_time`, preserving the original date in the user's timezone.

The system SHALL NOT modify `rental_start_date` if its time component is anything other than `00:00:00`, treating any non-midnight time as a deliberate user choice.

#### Scenario: Date-only pickup picks up default time

- **WHEN** a user picks `2026-05-01` as `rental_start_date` (the picker stores it as `2026-05-01 00:00:00` in the user's TZ)
- **AND** the company's `default_pickup_time` is `9.0`
- **THEN** `rental_start_date` is set to `2026-05-01 09:00:00` in the user's TZ

#### Scenario: User-specified time is preserved

- **WHEN** a user picks `2026-05-01 14:30:00` as `rental_start_date`
- **THEN** `rental_start_date` remains `2026-05-01 14:30:00` (no snap)

### Requirement: Return time snap on rental order

When the user sets `rental_return_date` on a sale order to a value whose time component equals `00:00:00`, the system SHALL replace the time component with the company's `default_return_time`, preserving the original date in the user's timezone.

The system SHALL NOT modify `rental_return_date` if its time component is anything other than `00:00:00`.

#### Scenario: Date-only return picks up default time

- **WHEN** a user picks `2026-05-05` as `rental_return_date` (stored as `2026-05-05 00:00:00` in the user's TZ)
- **AND** the company's `default_return_time` is `23.983333`
- **THEN** `rental_return_date` is set to `2026-05-05 23:59:00` in the user's TZ

#### Scenario: User-specified return time is preserved

- **WHEN** a user picks `2026-05-05 17:00:00` as `rental_return_date`
- **THEN** `rental_return_date` remains `2026-05-05 17:00:00` (no snap)

### Requirement: Timezone correctness

The snap behavior SHALL be applied in the user's timezone (`self.env.user.tz`), not the server's timezone. After snapping the time component in the user's TZ, the resulting datetime SHALL be converted to UTC for storage.

#### Scenario: User in Asia/Bangkok picks a date

- **WHEN** a user with `tz='Asia/Bangkok'` picks `2026-05-01` as `rental_start_date`
- **AND** the company's `default_pickup_time` is `9.0`
- **THEN** the stored UTC value of `rental_start_date` is `2026-05-01 02:00:00 UTC` (09:00 Bangkok = 02:00 UTC)
