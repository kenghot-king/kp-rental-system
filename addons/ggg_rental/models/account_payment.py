from odoo import _, api, fields, models
from odoo.exceptions import UserError


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

    cashier_id = fields.Many2one(
        'res.users',
        string="Cashier",
        default=lambda self: self.env.user,
        tracking=True,
        help="User who collected this payment. Defaults to the current user at "
             "registration time and is not editable from the Pay wizard.",
    )

    approval_code = fields.Char(
        string="Approval Code",
        copy=False,
        tracking=True,
        help="Free-text metadata: EDC approval code, QR transaction ID, online "
             "gateway reference, etc.",
    )

    display_method = fields.Char(
        string="Method (Display)",
        compute='_compute_display_method',
        store=True,
        help="Payment method line name, used as the grouping key for rental "
             "payment reports and daily reconciliation.",
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

    reconciliation_id = fields.Many2one(
        'rental.daily.reconciliation',
        string="Reconciliation",
        readonly=True,
        index=True,
        copy=False,
    )

    @api.depends('payment_method_line_id', 'payment_method_line_id.name')
    def _compute_display_method(self):
        for payment in self:
            payment.display_method = payment.payment_method_line_id.name or False

    @api.model_create_multi
    def create(self, vals_list):
        Recon = self.env['rental.daily.reconciliation'].sudo()
        for vals in vals_list:
            cashier_id = vals.get('cashier_id')
            date = vals.get('date')
            if cashier_id and date:
                confirmed = Recon.search([
                    ('cashier_id', '=', cashier_id),
                    ('date', '=', date),
                    ('state', '=', 'confirmed'),
                ], limit=1)
                if confirmed:
                    cashier = self.env['res.users'].browse(cashier_id)
                    raise UserError(_(
                        "Cannot create payment: %(cashier)s's day %(date)s is already "
                        "confirmed in reconciliation '%(recon)s'. "
                        "Ask a rental supervisor to reopen it.",
                        cashier=cashier.name,
                        date=date,
                        recon=confirmed.name,
                    ))
        return super().create(vals_list)

    def write(self, vals):
        for payment in self:
            if payment.reconciliation_id and payment.reconciliation_id.state == 'confirmed':
                raise UserError(_(
                    "Payment is locked: reconciliation '%(recon)s' is confirmed. "
                    "Ask a rental supervisor to reopen it first.",
                    recon=payment.reconciliation_id.name,
                ))
            new_cashier_id = vals.get('cashier_id', payment.cashier_id.id)
            new_date = vals.get('date', payment.date)
            if ('cashier_id' in vals or 'date' in vals) and new_cashier_id and new_date:
                confirmed = self.env['rental.daily.reconciliation'].sudo().search([
                    ('cashier_id', '=', new_cashier_id),
                    ('date', '=', new_date),
                    ('state', '=', 'confirmed'),
                ], limit=1)
                if confirmed:
                    raise UserError(_(
                        "Cannot move payment into confirmed reconciliation '%(recon)s'.",
                        recon=confirmed.name,
                    ))
        return super().write(vals)

    def unlink(self):
        for payment in self:
            if payment.reconciliation_id and payment.reconciliation_id.state == 'confirmed':
                raise UserError(_(
                    "Cannot delete payment linked to confirmed reconciliation '%(recon)s'.",
                    recon=payment.reconciliation_id.name,
                ))
        return super().unlink()
