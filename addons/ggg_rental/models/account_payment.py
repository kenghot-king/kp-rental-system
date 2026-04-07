from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_reference_2 = fields.Char(
        string="Reference 2",
        copy=False,
        tracking=True,
        help="Second external payment reference (e.g. EDC ref, 2c2p ref).",
    )

    is_rental_payment = fields.Boolean(
        string="Is Rental Payment",
        compute='_compute_is_rental_payment',
        store=True,
    )

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_is_rental_payment(self):
        for payment in self:
            rental = False
            for invoice in payment.reconciled_invoice_ids:
                sale_orders = invoice.invoice_line_ids.sale_line_ids.order_id
                if any(so.is_rental_order for so in sale_orders):
                    rental = True
                    break
            payment.is_rental_payment = rental
