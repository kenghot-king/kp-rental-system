from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_payment_state = fields.Selection(
        related='move_id.payment_state',
        string="Payment Status",
        store=False,
    )

    tax_amount = fields.Monetary(
        string="Tax Amount",
        compute='_compute_tax_amount',
        currency_field='currency_id',
    )

    def _compute_tax_amount(self):
        for line in self:
            line.tax_amount = line.price_total - line.price_subtotal
