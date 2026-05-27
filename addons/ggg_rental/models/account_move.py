from num2words import num2words
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    deposit_hold_payment_ids = fields.One2many(
        'account.payment',
        'deposit_invoice_id',
        string="Hold Payments",
    )

    deposit_hold_state = fields.Selection(
        [('none', 'None'), ('hold', 'On Hold')],
        string="Deposit Hold State",
        compute='_compute_deposit_hold_state',
        store=True,
    )

    is_deposit_invoice = fields.Boolean(
        string="Is Deposit Invoice",
        compute='_compute_is_deposit_invoice',
    )

    is_picked_up = fields.Boolean(
        string="Item Picked Up",
        compute='_compute_is_picked_up',
    )

    @api.depends('deposit_hold_payment_ids.hold_state')
    def _compute_deposit_hold_state(self):
        for move in self:
            active = move.deposit_hold_payment_ids.filtered(
                lambda p: p.is_deposit_hold and p.hold_state == 'active'
            )
            move.deposit_hold_state = 'hold' if active else 'none'

    @api.depends('move_type', 'invoice_line_ids.product_id.is_rental_deposit')
    def _compute_is_deposit_invoice(self):
        for move in self:
            move.is_deposit_invoice = (
                move.move_type == 'out_invoice'
                and any(l.product_id.is_rental_deposit for l in move.invoice_line_ids)
            )

    @api.depends('invoice_line_ids.sale_line_ids.order_id.rental_status')
    def _compute_is_picked_up(self):
        for move in self:
            orders = move._get_linked_rental_orders()
            move.is_picked_up = any(o.rental_status in ('return', 'returned') for o in orders)

    def _get_active_hold_payment(self):
        self.ensure_one()
        return self.deposit_hold_payment_ids.filtered(
            lambda p: p.is_deposit_hold and p.hold_state == 'active'
        )[:1]

    def action_unhold(self):
        self.ensure_one()
        payment = self._get_active_hold_payment()
        if not payment:
            raise UserError(_("No active credit hold found on this invoice."))
        payment.hold_state = 'released'

    def action_forfeit(self):
        self.ensure_one()
        payment = self._get_active_hold_payment()
        if not payment:
            raise UserError(_("No active credit hold found on this invoice."))
        return {
            'name': _("Forfeit Deposit Hold"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.forfeit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_payment_id': payment.id,
            },
        }

    def action_print_deposit_certificate(self):
        self.ensure_one()
        return self.env.ref('ggg_rental.action_report_deposit_certificate').report_action(self)

    def action_view_hold_payments(self):
        self.ensure_one()
        return {
            'name': _("Hold Payments"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('deposit_invoice_id', '=', self.id), ('is_deposit_hold', '=', True)],
        }

    def amount_in_thai_words(self):
        if self.currency_id.name != 'THB':
            return ''
        return num2words(self.amount_total, lang='th', to='currency')

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.move_type == 'out_invoice' and self.payment_state != 'paid':
            raise UserError(_("ไม่สามารถพิมพ์ใบเสร็จได้ เนื่องจากยังไม่ชำระเงิน"))
        return 'ggg_rental.ggg_report_invoice_document'

    def write(self, vals):
        res = super().write(vals)
        if 'payment_state' in vals:
            rental_orders = self._get_linked_rental_orders()
            if rental_orders:
                rental_orders._recompute_rental_completion()
        return res

    def _get_linked_rental_orders(self):
        """Return rental sale orders linked to these invoices."""
        orders = self.env['sale.order']
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                continue
            for line in move.invoice_line_ids:
                orders |= line.sale_line_ids.order_id
        return orders.filtered('is_rental_order')
