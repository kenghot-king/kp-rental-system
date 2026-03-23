## ADDED Requirements

### Requirement: Gantt view type registration
The system SHALL register `gantt` as a valid view type in Odoo's view registry (`ir.ui.view`) and action registry (`ir.actions.act_window.view`), allowing any model to define a `<gantt>` view arch.

#### Scenario: Gantt view type available
- **WHEN** a developer defines `<gantt date_start="start_date" date_stop="end_date">` in an XML view
- **THEN** the system validates and stores the view arch without errors

#### Scenario: Action includes gantt view mode
- **WHEN** an `ir.actions.act_window` record includes `gantt` in `view_mode`
- **THEN** the Gantt view tab appears in the action's view switcher

### Requirement: Gantt arch validation
The system SHALL validate `<gantt>` XML archs against a defined set of allowed attributes including `date_start`, `date_stop`, `default_scale`, `default_range`, `color`, `decoration-*`, `progress`, `consolidation`, `dependency_field`, `display_unavailability`, `disable_drag_drop`, `scales`, `precision`, `form_view_id`, `thumbnails`, `progress_bar`, `pill_label`, `total_row`, `collapse_first_level`, `display_mode`, `create`, `edit`, `delete`, `plan`, `cell_create`, `on_create`, `sample`, `groups_limit`, and `offset`.

#### Scenario: Valid gantt arch accepted
- **WHEN** a `<gantt>` arch contains only allowed attributes
- **THEN** the view validates successfully

#### Scenario: Invalid gantt arch rejected
- **WHEN** a `<gantt>` arch contains an unknown attribute
- **THEN** the system raises a validation error

### Requirement: get_gantt_data API
The system SHALL provide a `get_gantt_data()` method on the `base` model that accepts `domain`, `groupby`, `read_specification`, `limit`, `offset`, `unavailability_fields`, `progress_bar_fields`, `start_date`, `stop_date`, and `scale` parameters, and returns grouped records with their data, unavailability periods, and progress bar values.

#### Scenario: Fetch gantt data with grouping
- **WHEN** `get_gantt_data()` is called with `domain=[('active','=',True)]`, `groupby=['user_id']`, and a date range
- **THEN** the response contains `groups` (grouped record sets), `records` (flattened), `length` (total group count), `unavailabilities`, and `progress_bars`

#### Scenario: Fetch gantt data with pagination
- **WHEN** `get_gantt_data()` is called with `limit=20` and `offset=0`
- **THEN** only the first 20 groups are returned, with `length` reflecting the total count

#### Scenario: Fetch with unavailability
- **WHEN** `get_gantt_data()` is called with `unavailability_fields=['user_id']`
- **THEN** the response includes `unavailabilities` mapping each resource to its unavailable time periods

### Requirement: Default gantt view generation
The system SHALL auto-generate a default `<gantt>` view for models that have compatible date fields (`date_start`/`date_stop` or similar named fields) when no explicit gantt view is defined.

#### Scenario: Model with date fields
- **WHEN** a model has `date_start` and `date_stop` fields and no gantt view defined
- **THEN** the system generates a default gantt view using those fields

#### Scenario: Model without date fields
- **WHEN** a model has no suitable date field pair
- **THEN** the system raises a `UserError`

### Requirement: Dependency-aware rescheduling
The system SHALL provide a `web_gantt_reschedule()` method that handles moving a pill (record) while cascading changes to dependent records, with cycle detection and undo support.

#### Scenario: Reschedule with cascading dependencies
- **WHEN** a record is rescheduled via `web_gantt_reschedule()` and has dependent records via `dependency_field`
- **THEN** dependent records are automatically shifted to maintain their relative positioning, and the response includes `old_vals_per_pill_id` for undo

#### Scenario: Cycle detection
- **WHEN** rescheduling would create a circular dependency
- **THEN** the system returns a `loop_error` response without modifying any records

#### Scenario: Reschedule into the past
- **WHEN** cascading rescheduling would push a dependent record's start date into the past
- **THEN** the system returns a `past_error` response with the conflicting record details

#### Scenario: Reschedule methods
- **WHEN** `reschedule_method` is `maintainBuffer`
- **THEN** gaps between dependent records are preserved during cascading
- **WHEN** `reschedule_method` is `consumeBuffer`
- **THEN** gaps between dependent records are removed when moving the upstream record earlier

### Requirement: Gantt JS rendering with CSS Grid
The system SHALL render the Gantt chart using CSS Grid layout with rows (grouped records), columns (time intervals), and pills (record bars) positioned via `grid-row` and `grid-column` CSS properties.

#### Scenario: Basic rendering
- **WHEN** a Gantt view is opened with records
- **THEN** records appear as horizontal pills spanning their date range, organized in rows by grouping field, with time columns based on the selected scale

#### Scenario: Scale selection
- **WHEN** the user selects a scale (day/week/month/year)
- **THEN** the time axis changes granularity (hours for day, days for week/month, months for year) and pills are repositioned accordingly

#### Scenario: Empty state with sample data
- **WHEN** a Gantt view has no records and `sample="1"` is set
- **THEN** the view displays sample placeholder data

### Requirement: Virtual scrolling
The system SHALL implement virtual scrolling that renders only visible rows and columns, with a buffer for smooth scrolling.

#### Scenario: Large dataset
- **WHEN** a Gantt view has 500+ rows
- **THEN** only the visible rows (plus buffer) are rendered in the DOM, and scrolling dynamically loads/unloads rows

### Requirement: Pill drag and drop
The system SHALL allow users to drag pills horizontally (change dates) and vertically (change group) to reschedule records.

#### Scenario: Drag pill to new date
- **WHEN** a user drags a pill to a different column
- **THEN** the record's `date_start` and `date_stop` are updated to match the new column's time range, preserving the original duration

#### Scenario: Drag pill to different row
- **WHEN** a user drags a pill to a different row (group)
- **THEN** the record's grouping field is updated to match the target row's value

#### Scenario: Drag disabled
- **WHEN** `disable_drag_drop="1"` is set in the gantt arch
- **THEN** pills cannot be dragged

### Requirement: Pill resizing
The system SHALL allow users to resize pills from the left (change start date) or right (change end date) edges.

#### Scenario: Resize from right edge
- **WHEN** a user drags the right edge of a pill
- **THEN** the record's `date_stop` is updated to the new position while `date_start` remains unchanged

#### Scenario: Resize from left edge
- **WHEN** a user drags the left edge of a pill
- **THEN** the record's `date_start` is updated to the new position while `date_stop` remains unchanged

### Requirement: Dependency connectors
The system SHALL display SVG Bezier curve connectors between pills that have dependency relationships, and allow users to create/delete dependencies by dragging between connector bullets.

#### Scenario: Display existing dependencies
- **WHEN** records have values in the `dependency_field`
- **THEN** SVG curves connect the dependent pills visually

#### Scenario: Create dependency via drag
- **WHEN** a user drags from one pill's connector bullet to another pill
- **THEN** a dependency relationship is created (target's `dependency_field` updated with source ID)

#### Scenario: Delete dependency
- **WHEN** a user clicks the delete button on a highlighted connector
- **THEN** the dependency relationship is removed

### Requirement: Pill popover
The system SHALL display a popover with record details when a user clicks on a pill, with options to edit or delete the record.

#### Scenario: Click pill
- **WHEN** a user clicks on a pill
- **THEN** a popover appears showing the record's key fields and action buttons (Open, Edit, Delete)

#### Scenario: Custom popover template
- **WHEN** the gantt arch includes a `<gantt-popover>` child element
- **THEN** the popover renders the custom template instead of the default

### Requirement: Progress bars
The system SHALL display progress bars in row headers when `progress_bar` is configured in the gantt arch.

#### Scenario: Progress bar display
- **WHEN** `progress_bar="user_id:warning"` is set and `_gantt_progress_bar()` returns data
- **THEN** each row header shows a colored progress bar with value/max ratio

### Requirement: Pill colors and decorations
The system SHALL support 12 built-in pill colors (assigned via `color` field attribute) and conditional decorations via `decoration-*` attributes.

#### Scenario: Color assignment
- **WHEN** `color="user_id"` is set in the gantt arch
- **THEN** pills are colored based on `record.user_id.id % 12`

#### Scenario: Decoration applied
- **WHEN** `decoration-danger="is_overdue == True"` is set
- **THEN** pills matching the condition receive the danger decoration style

### Requirement: Unavailability display
The system SHALL grey out time cells where resources are unavailable when `display_unavailability="1"` is set.

#### Scenario: Unavailable periods shown
- **WHEN** `display_unavailability="1"` is set and `_gantt_unavailability()` returns periods
- **THEN** cells within unavailable periods have a grey background

### Requirement: Gantt controls toolbar
The system SHALL provide a toolbar with Previous/Today/Next navigation buttons and a scale/range selector.

#### Scenario: Navigate forward
- **WHEN** the user clicks "Next"
- **THEN** the visible date range shifts forward by one unit of the current scale

#### Scenario: Today button
- **WHEN** the user clicks "Today"
- **THEN** the view centers on the current date

### Requirement: Multi-cell selection and creation
The system SHALL allow users to select multiple cells by dragging across the grid and create records from the selection.

#### Scenario: Select cells and create
- **WHEN** a user drags across multiple cells and clicks "Create"
- **THEN** a form dialog opens (or records are batch-created) with dates and group values pre-filled from the selected cells

### Requirement: Consolidation and total row
The system SHALL support consolidation rows that aggregate pill data and a total row showing combined metrics.

#### Scenario: Total row
- **WHEN** `total_row="1"` is set in the gantt arch
- **THEN** a summary row at the bottom aggregates pill counts/values across all rows

#### Scenario: Consolidation display
- **WHEN** `consolidation="field_name"` is set
- **THEN** group rows show aggregated values from overlapping pills
