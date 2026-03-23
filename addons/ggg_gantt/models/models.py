from collections import defaultdict
from datetime import datetime, timezone, timedelta
from lxml.builder import E
from pytz import utc

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import _, unique, OrderedSet

DATE_FIELD_ADAPTERS = {
    'date': {
        'parse': fields.Date.to_date,
        'now': fields.Date.today,
    },
    'datetime': {
        'parse': fields.Datetime.to_datetime,
        'now': fields.Datetime.now,
    },
}


class Base(models.AbstractModel):
    _inherit = 'base'

    _start_name = 'date_start'
    _stop_name = 'date_stop'

    _WEB_GANTT_RESCHEDULE_FORWARD = 'forward'
    _WEB_GANTT_RESCHEDULE_BACKWARD = 'backward'
    _WEB_GANTT_RESCHEDULE_MAINTAIN_BUFFER = 'maintainBuffer'
    _WEB_GANTT_RESCHEDULE_CONSUME_BUFFER = 'consumeBuffer'
    _WEB_GANTT_LOOP_ERROR = 'loop_error'

    # -------------------------------------------------------------------------
    # Default View
    # -------------------------------------------------------------------------

    @api.model
    def _get_default_gantt_view(self):
        """Generate a default gantt view by inferring time-based fields."""
        view = E.gantt(string=self._description)

        gantt_field_names = {
            '_start_name': [
                'date_start', 'start_date', 'x_date_start', 'x_start_date',
            ],
            '_stop_name': [
                'date_stop', 'stop_date', 'date_end', 'end_date',
                'x_date_stop', 'x_stop_date', 'x_date_end', 'x_end_date',
            ],
        }
        for name in gantt_field_names:
            if getattr(self, name) not in self._fields:
                for dt in gantt_field_names[name]:
                    if dt in self._fields:
                        setattr(self, name, dt)
                        break
                else:
                    raise UserError(_("Insufficient fields for Gantt View!"))
        view.set('date_start', self._start_name)
        view.set('date_stop', self._stop_name)

        return view

    # -------------------------------------------------------------------------
    # Data Fetching
    # -------------------------------------------------------------------------

    @api.model
    def get_gantt_data(
        self, domain, groupby, read_specification,
        limit=None, offset=0,
        unavailability_fields=None, progress_bar_fields=None,
        start_date=None, stop_date=None, scale=None,
    ):
        """Fetch grouped records with unavailabilities and progress bars for the Gantt view.

        :param domain: search domain
        :param groupby: list of fields to group on
        :param read_specification: web_read specification
        :param limit: max number of groups
        :param offset: group offset
        :param unavailability_fields: list of many2x fields for unavailability
        :param progress_bar_fields: list of fields for progress bars
        :param start_date: start datetime in UTC string
        :param stop_date: stop datetime in UTC string
        :param scale: 'day', 'week', 'month', or 'year'
        :returns: dict with groups, records, length, unavailabilities, progress_bars
        """
        if groupby:
            groups, length = self.with_context(
                read_group_expand=True
            )._formatted_read_group_with_length(
                domain, groupby, ['id:array_agg'],
                offset=offset, limit=limit,
            )

            final_result = {
                'groups': groups,
                'length': length,
            }

            all_record_ids = tuple(unique(
                record_id
                for one_group in groups
                for record_id in one_group['id:array_agg']
            ))

            all_records = self.with_context(
                active_test=False
            ).search_fetch(
                [('id', 'in', all_record_ids)],
                read_specification.keys(),
            )
        else:
            all_records = self.search_fetch(domain, read_specification.keys())
            final_result = {
                'groups': [{
                    'id:array_agg': all_records._ids,
                    '__extra_domain': [],
                }],
                'length': 1,
            }

        final_result['records'] = all_records.with_env(self.env).web_read(
            read_specification
        )

        if unavailability_fields is None:
            unavailability_fields = []
        if progress_bar_fields is None:
            progress_bar_fields = []

        ordered_set_ids = OrderedSet(all_records._ids)
        res_ids_for_unavailabilities = defaultdict(set)
        res_ids_for_progress_bars = defaultdict(set)
        for group in final_result['groups']:
            for field in unavailability_fields:
                res_id = group[field][0] if group[field] else False
                if res_id:
                    res_ids_for_unavailabilities[field].add(res_id)
            for field in progress_bar_fields:
                res_id = group[field][0] if group[field] else False
                if res_id:
                    res_ids_for_progress_bars[field].add(res_id)
            group['__record_ids'] = list(
                ordered_set_ids & OrderedSet(group.pop('id:array_agg'))
            )
            del group['__extra_domain']
            group.pop('__fold', None)

        if unavailability_fields or progress_bar_fields:
            start = fields.Datetime.from_string(start_date)
            stop = fields.Datetime.from_string(stop_date)

        unavailabilities = {}
        for field in unavailability_fields:
            unavailabilities[field] = self._gantt_unavailability(
                field, list(res_ids_for_unavailabilities[field]),
                start, stop, scale,
            )
        final_result['unavailabilities'] = unavailabilities

        progress_bars = {}
        for field in progress_bar_fields:
            progress_bars[field] = self._gantt_progress_bar(
                field, list(res_ids_for_progress_bars[field]),
                start, stop,
            )
        final_result['progress_bars'] = progress_bars

        return final_result

    # -------------------------------------------------------------------------
    # Progress Bar & Unavailability Hooks
    # -------------------------------------------------------------------------

    @api.model
    def _gantt_progress_bar(self, field, res_ids, start, stop):
        """Get progress bar value per record.

        Override this method to implement progress bars on Gantt groups.
        Should return a dict like: {res_id: {'value': X, 'max_value': Y}}

        :param field: field on which there are progress bars
        :param res_ids: resource IDs to compute progress for
        :param start: start datetime
        :param stop: stop datetime
        :returns: dict of value and max_value per record
        """
        return {}

    @api.model
    def _gantt_unavailability(self, field, res_ids, start, stop, scale):
        """Get unavailability periods for a given set of resources.

        Override this method to implement unavailability display on Gantt views.
        Should return a dict like: {res_id: [{'start': dt, 'stop': dt}, ...]}

        :param field: name of a many2x field
        :param res_ids: list of resource IDs
        :param start: start datetime
        :param stop: stop datetime
        :param scale: 'day', 'week', 'month', or 'year'
        :returns: dict of unavailability periods per resource
        """
        return {}

    # -------------------------------------------------------------------------
    # Rescheduling
    # -------------------------------------------------------------------------

    def web_gantt_init_old_vals_per_pill_id(self, vals):
        """Store old values before rescheduling for undo support."""
        old_vals_per_pill_id = defaultdict(dict)
        for field in vals:
            field_type = self.fields_get(field)[field]['type']
            if field_type in ['many2many', 'one2many']:
                old_vals_per_pill_id[self.id][field] = self[field].ids or False
            elif field_type == 'many2one':
                old_vals_per_pill_id[self.id][field] = self[field].id or False
            else:
                old_vals_per_pill_id[self.id][field] = self[field]
        return old_vals_per_pill_id

    @api.model
    def web_gantt_reschedule(
        self,
        vals,
        reschedule_method,
        record_id,
        dependency_field_name,
        dependency_inverted_field_name,
        start_date_field_name,
        stop_date_field_name,
    ):
        """Reschedule a record with dependency-aware cascading updates.

        :param vals: new values for the moved pill
        :param reschedule_method: 'maintainBuffer' or 'consumeBuffer'
        :param record_id: ID of the moved record
        :param dependency_field_name: field for master→slave dependencies
        :param dependency_inverted_field_name: field for slave→master dependencies
        :param start_date_field_name: start date field name
        :param stop_date_field_name: stop date field name
        :returns: dict with type, message, old_vals_per_pill_id
        """
        if reschedule_method not in (
            self._WEB_GANTT_RESCHEDULE_CONSUME_BUFFER,
            self._WEB_GANTT_RESCHEDULE_MAINTAIN_BUFFER,
        ):
            raise ValueError(
                self.env._("Invalid reschedule method %s", reschedule_method)
            )

        record = self.env[self._name].browse(record_id)
        message = self.env._("Tasks rescheduled")

        start_date_field = self.env[self._name]._fields[start_date_field_name]
        start_date = now_value = None
        if start_date_field_name in vals:
            start_date = DATE_FIELD_ADAPTERS[start_date_field.type]['parse'](
                vals[start_date_field_name]
            )
            now_value = DATE_FIELD_ADAPTERS[start_date_field.type]['now']()

        if (
            not (
                start_date_field_name in vals
                and stop_date_field_name in vals
                and dependency_field_name
                and dependency_inverted_field_name
            )
            or (start_date and start_date < now_value)
        ):
            old_vals_per_pill_id = record.web_gantt_init_old_vals_per_pill_id(vals)
            record.write(vals)
            return {
                "type": "success",
                "message": message,
                "old_vals_per_pill_id": old_vals_per_pill_id,
            }

        with self.env.cr.savepoint() as sp:
            log_messages, old_vals_per_pill_id = (
                record._web_gantt_action_reschedule_candidates(
                    dependency_field_name, dependency_inverted_field_name,
                    start_date_field_name, stop_date_field_name,
                    reschedule_method, vals,
                )
            )
            has_errors = bool(log_messages.get("errors"))
            sp.close(rollback=has_errors)

        notification_type = "success"
        if has_errors or log_messages.get("warnings"):
            message = self._web_gantt_get_reschedule_message(log_messages)
            notification_type = "warning" if has_errors else "info"

        return {
            "type": notification_type,
            "message": message,
            "old_vals_per_pill_id": old_vals_per_pill_id,
        }

    # -------------------------------------------------------------------------
    # Undo Support
    # -------------------------------------------------------------------------

    def action_rollback_scheduling(self, old_vals_per_pill_id):
        """Revert rescheduled records to their original dates."""
        for record in self:
            vals = old_vals_per_pill_id.get(
                str(record.id), old_vals_per_pill_id.get(record.id)
            )
            if vals:
                record.write(vals)

    def gantt_undo_drag_drop(self, drag_action, data=None):
        """Undo a drag-drop operation (copy or reschedule)."""
        if not self.exists():
            return False
        if drag_action == "copy":
            return self.unlink()
        elif drag_action == "reschedule" and data:
            return self.write(data)
        return False

    # -------------------------------------------------------------------------
    # Reschedule Message Helpers
    # -------------------------------------------------------------------------

    def _web_gantt_get_reschedule_message_per_key(self, key, params=None):
        if key == self._WEB_GANTT_LOOP_ERROR:
            return _("The dependencies are not valid, there is a cycle.")
        elif key == "past_error":
            if params:
                return _("%s cannot be scheduled in the past", params.display_name)
            else:
                return _("Impossible to schedule in the past.")
        return ""

    def _web_gantt_get_reschedule_message(self, log_messages):
        def get_messages(logs):
            messages = []
            for key in logs:
                message = self._web_gantt_get_reschedule_message_per_key(
                    key, log_messages.get(key)
                )
                if message:
                    messages.append(message)
            return messages

        messages = []
        errors = log_messages.get("errors")
        if errors:
            messages = get_messages(log_messages.get("errors"))
        else:
            messages = get_messages(log_messages.get("warnings", []))
        return "\n".join(messages)

    # -------------------------------------------------------------------------
    # Reschedule Internals
    # -------------------------------------------------------------------------

    def _web_gantt_get_direction(self, start_date_field_name, vals):
        start_date_field = self.env[self._name]._fields[start_date_field_name]
        date_start = DATE_FIELD_ADAPTERS[start_date_field.type]['parse'](
            vals[start_date_field_name]
        )
        if date_start > self[start_date_field_name]:
            return self._WEB_GANTT_RESCHEDULE_FORWARD
        return self._WEB_GANTT_RESCHEDULE_BACKWARD

    def _web_gantt_action_reschedule_candidates(
        self,
        dependency_field_name, dependency_inverted_field_name,
        start_date_field_name, stop_date_field_name,
        reschedule_method, vals,
    ):
        """Prepare and move candidates for dependency-aware rescheduling."""
        search_forward = (
            self._web_gantt_get_direction(start_date_field_name, vals)
            == self._WEB_GANTT_RESCHEDULE_FORWARD
        )
        candidates_ids = []
        dep_field = (
            dependency_inverted_field_name if search_forward
            else dependency_field_name
        )
        if self._web_gantt_check_cycle_existance_and_get_rescheduling_candidates(
            candidates_ids, dep_field,
            start_date_field_name, stop_date_field_name,
        ):
            return {'errors': self._WEB_GANTT_LOOP_ERROR}, {}

        return self._web_gantt_move_candidates(
            start_date_field_name, stop_date_field_name,
            dependency_field_name, dependency_inverted_field_name,
            search_forward, candidates_ids,
            reschedule_method == self._WEB_GANTT_RESCHEDULE_CONSUME_BUFFER,
            vals,
        )

    def _web_gantt_is_candidate_in_conflict(
        self, start_date_field_name, stop_date_field_name,
        dependency_field_name, dependency_inverted_field_name,
    ):
        return (
            any(
                r[start_date_field_name] and r[stop_date_field_name]
                and self[start_date_field_name] < r[stop_date_field_name]
                for r in self[dependency_field_name]
            )
            or any(
                r[start_date_field_name] and r[stop_date_field_name]
                and self[stop_date_field_name] > r[start_date_field_name]
                for r in self[dependency_inverted_field_name]
            )
        )

    def _web_gantt_update_next_pills_first_possible_date(
        self,
        dependency_field_name, dependency_inverted_field_name,
        search_forward,
        first_possible_start_date_per_candidate,
        last_possible_end_date_per_candidate,
        consume_buffer,
        start_date_field_name, stop_date_field_name,
        start_date, end_date,
        old_start_date, old_end_date,
    ):
        related_field = (
            dependency_inverted_field_name if search_forward
            else dependency_field_name
        )
        for next_rec in self[related_field]:
            if search_forward:
                end_dt = end_date.astimezone(utc)
                first_possible_start_date_per_candidate[next_rec.id] = max(
                    first_possible_start_date_per_candidate.get(next_rec.id, end_dt),
                    end_dt,
                )
                if (
                    not consume_buffer
                    and next_rec[start_date_field_name] > old_end_date
                ):
                    buffer_duration = (
                        next_rec[start_date_field_name] - old_end_date
                    ).total_seconds()
                    start_date_after_buffer = end_dt + timedelta(
                        seconds=buffer_duration
                    )
                    first_possible_start_date_per_candidate[next_rec.id] = max(
                        first_possible_start_date_per_candidate.get(
                            next_rec.id, start_date_after_buffer
                        ),
                        start_date_after_buffer,
                    )
            else:
                start_dt = start_date.astimezone(utc)
                last_possible_end_date_per_candidate[next_rec.id] = min(
                    last_possible_end_date_per_candidate.get(next_rec.id, start_dt),
                    start_dt,
                )
                if (
                    not consume_buffer
                    and next_rec[stop_date_field_name] < old_start_date
                ):
                    buffer_duration = (
                        old_start_date - next_rec[stop_date_field_name]
                    ).total_seconds()
                    end_date_after_buffer = start_dt - timedelta(
                        seconds=buffer_duration
                    )
                    last_possible_end_date_per_candidate[next_rec.id] = min(
                        last_possible_end_date_per_candidate.get(
                            next_rec.id, end_date_after_buffer
                        ),
                        end_date_after_buffer,
                    )

    def _web_gantt_get_first_and_last_possible_dates(
        self, dependency_field_name, dependency_inverted_field_name,
        search_forward, stop_date_field_name, start_date_field_name,
    ):
        first_possible_start_date_per_candidate = {}
        last_possible_end_date_per_candidate = {}

        for candidate in self:
            related_candidates = (
                candidate[dependency_field_name] if search_forward
                else candidate[dependency_inverted_field_name]
            ).filtered(
                lambda pill: pill[start_date_field_name] and pill[stop_date_field_name]
            )
            not_replanned_candidates = related_candidates - self

            if not not_replanned_candidates:
                continue

            boundary_date = (
                stop_date_field_name if search_forward
                else start_date_field_name
            )
            boundary_dates = not_replanned_candidates.mapped(boundary_date)

            if search_forward:
                first_possible_start_date_per_candidate[candidate.id] = (
                    max(boundary_dates).astimezone(utc)
                )
            else:
                last_possible_end_date_per_candidate[candidate.id] = (
                    min(boundary_dates).astimezone(utc)
                )

        return (
            first_possible_start_date_per_candidate,
            last_possible_end_date_per_candidate,
        )

    def _web_gantt_move_candidates(
        self, start_date_field_name, stop_date_field_name,
        dependency_field_name, dependency_inverted_field_name,
        search_forward, candidates_ids, consume_buffer, vals,
    ):
        """Move candidates according to the provided parameters."""
        result = {
            "errors": [],
            "warnings": [],
        }

        old_vals_per_pill_id = self.web_gantt_init_old_vals_per_pill_id(vals)

        candidates = self.browse(
            [rec_id for rec_id in candidates_ids if rec_id != self.id]
        )
        self.write(vals)

        (
            first_possible_start_date_per_candidate,
            last_possible_end_date_per_candidate,
        ) = candidates._web_gantt_get_first_and_last_possible_dates(
            dependency_field_name, dependency_inverted_field_name,
            search_forward, stop_date_field_name, start_date_field_name,
        )

        self._web_gantt_update_next_pills_first_possible_date(
            dependency_field_name, dependency_inverted_field_name,
            search_forward,
            first_possible_start_date_per_candidate,
            last_possible_end_date_per_candidate,
            consume_buffer, start_date_field_name, stop_date_field_name,
            self[start_date_field_name], self[stop_date_field_name],
            old_vals_per_pill_id[self.id][start_date_field_name],
            old_vals_per_pill_id[self.id][stop_date_field_name],
        )

        for candidate in candidates:
            if (
                consume_buffer
                and not candidate._web_gantt_is_candidate_in_conflict(
                    start_date_field_name, stop_date_field_name,
                    dependency_field_name, dependency_inverted_field_name,
                )
            ):
                continue

            date_map = (
                first_possible_start_date_per_candidate if search_forward
                else last_possible_end_date_per_candidate
            )
            start_date, end_date = candidate._web_gantt_reschedule_compute_dates(
                date_map[candidate.id],
                search_forward,
                start_date_field_name, stop_date_field_name,
            )
            start_date = start_date.astimezone(timezone.utc)
            end_date = end_date.astimezone(timezone.utc)
            old_start_date = candidate[start_date_field_name]
            old_end_date = candidate[stop_date_field_name]

            if not candidate._web_gantt_reschedule_write_new_dates(
                start_date, end_date,
                start_date_field_name, stop_date_field_name,
            ):
                result["errors"].append("past_error")
                result["past_error"] = candidate
                return result, {}

            old_vals_per_pill_id[candidate.id] = {
                start_date_field_name: old_start_date,
                stop_date_field_name: old_end_date,
            }

            candidate._web_gantt_update_next_pills_first_possible_date(
                dependency_field_name, dependency_inverted_field_name,
                search_forward,
                first_possible_start_date_per_candidate,
                last_possible_end_date_per_candidate,
                consume_buffer, start_date_field_name, stop_date_field_name,
                candidate[start_date_field_name],
                candidate[stop_date_field_name],
                old_start_date, old_end_date,
            )

        return result, old_vals_per_pill_id

    # -------------------------------------------------------------------------
    # Cycle Detection & Candidate Selection
    # -------------------------------------------------------------------------

    def _web_gantt_record_has_dependencies(self):
        return True

    def _web_gantt_check_cycle_existance_and_get_rescheduling_candidates(
        self, candidates_ids, dependency_field_name,
        start_date_field_name, stop_date_field_name,
        visited=None, ancestors=None,
    ):
        """Check for cycles via DFS and collect rescheduling candidates.

        :param candidates_ids: list populated with candidate IDs in topological order
        :param dependency_field_name: field linking to dependent records
        :param start_date_field_name: start date field
        :param stop_date_field_name: stop date field
        :param visited: set of visited record IDs
        :param ancestors: list of ancestor IDs in current DFS path
        :returns: True if cycle detected, False otherwise
        """
        if visited is None:
            visited = set()
        if ancestors is None:
            ancestors = []
        visited.add(self.id)
        ancestors.append(self.id)

        children = (
            self[dependency_field_name]
            if self._web_gantt_record_has_dependencies()
            else []
        )
        for child in children:
            if child.id in ancestors:
                return True
            if (
                child.id not in visited
                and child._web_gantt_reschedule_is_record_candidate(
                    start_date_field_name, stop_date_field_name,
                )
                and child._web_gantt_check_cycle_existance_and_get_rescheduling_candidates(
                    candidates_ids, dependency_field_name,
                    start_date_field_name, stop_date_field_name,
                    visited, ancestors,
                )
            ):
                return True

        ancestors.pop()
        candidates_ids.insert(0, self.id)

        return False

    def _web_gantt_reschedule_compute_dates(
        self, date_candidate, search_forward,
        start_date_field_name, stop_date_field_name,
    ):
        """Compute new start/end dates preserving the original duration.

        Override this to add constraints (e.g., working hours).

        :param date_candidate: the optimal date without constraints
        :param search_forward: True if rescheduling forward
        :param start_date_field_name: start date field
        :param stop_date_field_name: stop date field
        :returns: tuple(start_date, end_date)
        """
        search_factor = 1 if search_forward else -1
        duration = search_factor * (
            self[stop_date_field_name] - self[start_date_field_name]
        )
        return sorted([date_candidate, date_candidate + duration])

    def _web_gantt_reschedule_is_record_candidate(
        self, start_date_field_name, stop_date_field_name,
    ):
        """Check if record is eligible for rescheduling."""
        return self._web_gantt_reschedule_can_record_be_rescheduled(
            start_date_field_name, stop_date_field_name,
        )

    def _web_gantt_reschedule_can_record_be_rescheduled(
        self, start_date_field_name, stop_date_field_name,
    ):
        """Check if record has valid future dates and can be rescheduled."""
        self.ensure_one()
        return (
            self[start_date_field_name]
            and self[stop_date_field_name]
            and self[start_date_field_name].replace(tzinfo=timezone.utc)
            > datetime.now(timezone.utc)
        )

    def _web_gantt_reschedule_write_new_dates(
        self, new_start_date, new_stop_date,
        start_date_field_name, stop_date_field_name,
    ):
        """Write new dates if start date is not in the past.

        A 30-second epsilon is applied because the first valid interval
        can be 'now' and rounding may push it slightly into the past.

        :returns: True if successful, False if dates are in the past
        """
        new_start_date = new_start_date.astimezone(timezone.utc).replace(
            tzinfo=None
        )
        if new_start_date < datetime.now() + timedelta(seconds=-30):
            return False

        self.write({
            start_date_field_name: new_start_date,
            stop_date_field_name: (
                new_stop_date.astimezone(timezone.utc).replace(tzinfo=None)
            ),
        })
        return True
