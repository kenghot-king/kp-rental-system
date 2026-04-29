from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import UserError


class QaScenario(models.Model):
    _name = 'qa.scenario'
    _description = 'QA Test Scenario'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    scenario = fields.Selection(
        selection=[
            ('late_pickup', 'Late Pickup'),
            ('late_return', 'Late Return'),
        ],
        string='Scenario Type',
        required=True,
    )
    days = fields.Integer(string='Days Late', default=1, required=True)
    order_ids = fields.Many2many(
        'sale.order',
        'qa_scenario_order_rel',
        'scenario_id',
        'order_id',
        string='Rental Orders',
        domain=[('is_rental_order', '=', True)],
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('applied', 'Applied'),
            ('reverted', 'Reverted'),
        ],
        default='draft',
        required=True,
        readonly=True,
    )
    log_ids = fields.One2many('qa.scenario.log', 'scenario_id', string='Logs', readonly=True)

    def _safety_check(self, order):
        """Return skip reason string, or None if order passes all checks."""
        if not order.is_rental_order:
            return _('Not a rental order')
        if order.state != 'sale':
            return _('Order not confirmed')
        expected_status = 'pickup' if self.scenario == 'late_pickup' else 'return'
        if order.rental_status != expected_status:
            return _('Wrong rental status (expected "%s", got "%s")') % (
                expected_status, order.rental_status or 'none'
            )
        if order.is_late:
            return _('Already late')
        open_invoices = order.invoice_ids.filtered(
            lambda i: i.state == 'posted'
            and i.payment_state not in ('paid', 'in_payment', 'reversed')
        )
        if open_invoices:
            return _('Has open invoice')
        return None

    def action_apply(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Scenario already applied.'))
        if not self.order_ids:
            raise UserError(_('No orders selected.'))

        now = fields.Datetime.now()
        delta = timedelta(days=self.days)
        applied = []
        skipped = []

        for order in self.order_ids:
            reason = self._safety_check(order)
            if reason:
                skipped.append('%s: %s' % (order.name, reason))
                continue

            if self.scenario == 'late_pickup':
                field_name = 'rental_start_date'
                original = order.rental_start_date
            else:
                field_name = 'rental_return_date'
                original = order.rental_return_date

            new_val = now - delta
            order.sudo().write({field_name: new_val})

            self.env['qa.scenario.log'].sudo().create({
                'scenario_id': self.id,
                'order_id': order.id,
                'field_changed': field_name,
                'original_value': original,
                'new_value': new_val,
                'applied_by': self.env.uid,
                'applied_at': now,
            })
            applied.append(order.name)

        if not applied:
            raise UserError(
                _('No orders were mutated.\n\nSkipped:\n%s') % '\n'.join(skipped)
            )

        self.state = 'applied'

        if skipped:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Applied with warnings'),
                    'message': _('Applied to %d order(s). Skipped %d:\n%s') % (
                        len(applied), len(skipped), '\n'.join(skipped)
                    ),
                    'type': 'warning',
                    'sticky': True,
                },
            }

    def action_revert(self):
        self.ensure_one()
        if self.state != 'applied':
            raise UserError(_('Scenario has not been applied.'))

        status_changed = []

        for log in self.log_ids.filtered(lambda l: not l.reverted):
            order = log.order_id
            expected_status = 'pickup' if self.scenario == 'late_pickup' else 'return'
            if order.rental_status != expected_status:
                status_changed.append(order.name)
            order.sudo().write({log.field_changed: log.original_value})
            log.reverted = True

        self.state = 'reverted'

        if status_changed:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Reverted with warnings'),
                    'message': _(
                        'Revert complete. The following orders changed status since apply — verify their state:\n%s'
                    ) % '\n'.join(status_changed),
                    'type': 'warning',
                    'sticky': True,
                },
            }
