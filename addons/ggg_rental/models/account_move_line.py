from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_payment_state = fields.Selection(
        related='move_id.payment_state',
        string="Payment Status",
        store=False,
    )

    signed_subtotal = fields.Monetary(
        string="Signed Subtotal",
        compute='_compute_signed_amounts',
        store=True,
        currency_field='currency_id',
    )

    signed_tax_amount = fields.Monetary(
        string="Signed Tax",
        compute='_compute_signed_amounts',
        store=True,
        currency_field='currency_id',
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Order",
        compute='_compute_sale_order_id',
        store=True,
        index='btree_not_null',
    )

    reversed_entry_id = fields.Many2one(
        related='move_id.reversed_entry_id',
        string="Reversal Of",
    )

    @api.depends('price_subtotal', 'price_total', 'move_id.move_type')
    def _compute_signed_amounts(self):
        """price_subtotal and price_total are positive on credit notes."""
        for line in self:
            sign = -1 if line.move_id.move_type == 'out_refund' else 1
            line.signed_subtotal = sign * line.price_subtotal
            line.signed_tax_amount = sign * (line.price_total - line.price_subtotal)

    @api.depends('sale_line_ids.order_id')
    def _compute_sale_order_id(self):
        for line in self:
            line.sale_order_id = line.sale_line_ids.order_id[:1]
