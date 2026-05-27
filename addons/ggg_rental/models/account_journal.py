from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    for_hold = fields.Boolean(
        string="Hold Journal",
        default=False,
        help="Mark this journal as a credit-hold journal (HLD). Payments using this "
             "journal on deposit invoices create a hold record without posting a journal entry.",
    )

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
