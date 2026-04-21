from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

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
