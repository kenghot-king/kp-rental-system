from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    channel_type = fields.Selection(
        [
            ('cash', 'Cash'),
            ('edc', 'EDC'),
            ('qr', 'QR'),
            ('online', 'Online'),
            ('other', 'Other'),
        ],
        string="Channel Type",
        help="Rental payment channel classification. Used for reporting and daily "
             "reconciliation groupings; does not affect payment form behavior.",
    )
