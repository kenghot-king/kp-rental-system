from num2words import num2words
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

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
