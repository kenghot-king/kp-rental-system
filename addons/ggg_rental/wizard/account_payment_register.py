from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_reference = fields.Char(string="Reference 1")
    payment_reference_2 = fields.Char(string="Reference 2")

    is_rental_payment = fields.Boolean(
        compute='_compute_is_rental_payment',
    )

    @api.depends('line_ids')
    def _compute_is_rental_payment(self):
        for wizard in self:
            sale_orders = wizard.line_ids.move_id.invoice_line_ids.sale_line_ids.order_id
            wizard.is_rental_payment = any(so.is_rental_order for so in sale_orders)

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        if self.payment_reference:
            vals['payment_reference'] = self.payment_reference
        if self.payment_reference_2:
            vals['payment_reference_2'] = self.payment_reference_2
        return vals
