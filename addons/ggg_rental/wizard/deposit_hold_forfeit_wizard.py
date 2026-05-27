from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DepositHoldForfeitWizard(models.TransientModel):
    _name = 'account.payment.forfeit.wizard'
    _description = "Forfeit Deposit Hold Wizard"

    invoice_id = fields.Many2one('account.move', string="Deposit Invoice", required=True)
    payment_id = fields.Many2one('account.payment', string="Hold Payment", required=True)
    date = fields.Date(
        string="Forfeiture Date",
        required=True,
        default=fields.Date.today,
    )

    def action_confirm(self):
        self.ensure_one()
        payment = self.payment_id
        invoice = self.invoice_id

        if not payment.is_deposit_hold or payment.hold_state != 'active':
            raise UserError(_("The hold payment is no longer active."))

        payment.date = self.date
        payment.with_context(_forfeit_flow=True).action_post()
        payment.hold_state = 'forfeited'

        domain = [
            ('parent_state', '=', 'posted'),
            ('account_type', 'in', self.env['account.payment']._get_valid_payment_account_types()),
            ('reconciled', '=', False),
        ]
        payment_lines = payment.move_id.line_ids.filtered_domain(domain)
        invoice_lines = invoice.line_ids.filtered_domain(domain)
        for account in payment_lines.account_id:
            (payment_lines + invoice_lines).filtered_domain([
                ('account_id', '=', account.id),
                ('reconciled', '=', False),
            ]).reconcile()
