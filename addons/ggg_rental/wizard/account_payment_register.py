from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_reference = fields.Char(string="Reference 1")
    payment_reference_2 = fields.Char(string="Reference 2")
    approval_code = fields.Char(string="Approval Code")

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
        if self.approval_code:
            vals['approval_code'] = self.approval_code
        vals['cashier_id'] = self.env.user.id
        return vals

    def _create_payments(self):
        payment_date = self.payment_date or fields.Date.today()

        if self.journal_id.for_hold:
            return self._create_hold_payment()

        cashier_id = self.env.user.id
        confirmed = self.env['rental.daily.reconciliation'].sudo().search([
            ('cashier_id', '=', cashier_id),
            ('date', '=', payment_date),
            ('state', '=', 'confirmed'),
        ], limit=1)
        if confirmed:
            raise UserError(_(
                "Cannot register payment: your day %(date)s is already confirmed "
                "in reconciliation '%(recon)s'. "
                "Ask rental supervisor %(supervisor)s to reopen it.",
                date=payment_date,
                recon=confirmed.name,
                supervisor=confirmed.confirmed_by.name or _("(unknown)"),
            ))
        return super()._create_payments()

    def _create_hold_payment(self):
        invoice = self.line_ids.move_id[:1]
        if not invoice:
            raise UserError(_("No invoice found to create a hold payment for."))

        is_deposit = any(
            line.product_id.is_rental_deposit
            for line in invoice.invoice_line_ids
        )
        if not is_deposit:
            raise UserError(_(
                "The Hold (HLD) journal can only be used on deposit invoices, "
                "not on rental invoices."
            ))

        payment = self.env['account.payment'].sudo().create({
            'is_deposit_hold': True,
            'hold_state': 'active',
            'deposit_invoice_id': invoice.id,
            'partner_id': invoice.partner_id.id,
            'journal_id': self.journal_id.id,
            'date': self.payment_date or fields.Date.today(),
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'approval_code': self.approval_code or False,
            'payment_reference_2': self.payment_reference_2 or False,
            'cashier_id': self.env.user.id,
            'memo': self.communication or False,
        })
        return payment
