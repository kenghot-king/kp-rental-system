from odoo import _, fields, models


class RentalDepositSyncWizard(models.TransientModel):
    _name = 'rental.deposit.sync.wizard'
    _description = 'Rental Deposit Sync Wizard'

    order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    original_action = fields.Char(string="Original Action", required=True)
    mismatch_info = fields.Text(string="Mismatch Details", readonly=True)

    def action_update_and_continue(self):
        """Sync deposits then execute the original action."""
        self.order_id.action_sync_deposits()
        return getattr(self.order_id.with_context(_skip_deposit_check=True), self.original_action)()

    def action_update_and_goback(self):
        """Sync deposits then close wizard, returning to the order form."""
        self.order_id.action_sync_deposits()
        return {'type': 'ir.actions.act_window_close'}

    def action_continue_as_is(self):
        """Execute the original action without syncing deposits."""
        return getattr(self.order_id.with_context(_skip_deposit_check=True), self.original_action)()
